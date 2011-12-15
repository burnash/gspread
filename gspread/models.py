from xml.etree import ElementTree
from xml.etree.ElementTree import Element, SubElement

from .ns import _ns, _ns1
from .urls import construct_url
from .utils import finditem


class Spreadsheet(object):
    """A class a spreadsheet object.

    """
    def __init__(self, client, feed_entry):
        self.client = client
        id_parts = feed_entry.find(_ns('id')).text.split('/')
        self.id = id_parts[-1]
        self._sheet_list = []

    def get_id_fields(self):
        return {'spreadsheet_id': self.id}

    def sheet_by_name(self, sheet_name):
        pass

    def _fetch_sheets(self):
        feed = self.client.get_worksheets_feed(self)
        for elem in feed.findall(_ns('entry')):
            self._sheet_list.append(Worksheet(self, elem))

    def worksheets(self):
        """Return a list of all worksheets in a spreadsheet."""
        if not self._sheet_list:
            self._fetch_sheets()
        return self._sheet_list[:]

    def get_worksheet(self, sheet_index):
        """Return a worksheet with index `sheet_index`.

        Indexes start from zero.

        """
        if not self._sheet_list:
            self._fetch_sheets()
        return self._sheet_list[sheet_index]


class Worksheet(object):
    """A model for worksheet object.

    """
    def __init__(self, spreadsheet, feed_entry):
        self.spreadsheet = spreadsheet
        self.client = spreadsheet.client
        self.id = feed_entry.find(_ns('id')).text.split('/')[-1]

    def get_id_fields(self):
        return {'spreadsheet_id': self.spreadsheet.id,
                'worksheet_id': self.id}

    def _cell_addr(self, row, col):
        return 'R%sC%s' % (row, col)

    def _fetch_cells(self):
        feed = self.client.get_cells_feed(self)
        cells_list = []
        for elem in feed.findall(_ns('entry')):
            cells_list.append(Cell(self, elem))

        return cells_list

    def cell(self, row, col):
        """Return a Cell object.

        Fetch a cell in row `row` and column `col`.

        """
        feed = self.client.get_cells_cell_id_feed(self,
                                                  self._cell_addr(row, col))
        return Cell(self, feed)

    def range(self, alphanum):
        feed = self.client.get_cells_feed(self, params={'range': alphanum,
                                                        'return-empty': 'true'})
        return [Cell(self, elem) for elem in feed.findall(_ns('entry'))]

    def get_all_rows(self):
        """Return a list of lists containing worksheet's rows."""
        cells = self._fetch_cells()

        rows = {}
        for cell in cells:
            rows.setdefault(int(cell.row), []).append(cell)

        rows_list = []
        for r in sorted(rows.keys()):
            rows_list.append(rows[r])

        simple_rows_list = []
        for r in rows_list:
            simple_row = []
            for c in r:
                simple_row.append(c.value)
            simple_rows_list.append(simple_row)

        return simple_rows_list

    def row_values(self, row):
        """Return a list of all values in row `row`.

        Empty cells in this list will be rendered as None.

        """
        cells_list = self._fetch_cells()

        cells = {}
        for cell in cells_list:
            if int(cell.row) == row:
                cells[int(cell.col)] = cell

        last_index = max(cells.keys())
        vals = []
        for i in range(1, last_index + 1):
            c = cells.get(i)
            vals.append(c.value if c else None)

        return vals

    def col_values(self, col):
        """Return a list of all values in column `col`.

        Empty cells in this list will be rendered as None.

        """
        cells_list = self._fetch_cells()

        cells = {}
        for cell in cells_list:
            if int(cell.col) == col:
                cells[int(cell.row)] = cell

        last_index = max(cells.keys())
        vals = []
        for i in range(1, last_index + 1):
            c = cells.get(i)
            vals.append(c.value if c else None)

        return vals

    def update_cell(self, row, col, val):
        """Set new value to a cell."""
        feed = self.client.get_cells_cell_id_feed(self,
                                                  self._cell_addr(row, col))
        cell_elem = feed.find(_ns1('cell'))
        cell_elem.set('inputValue', val)
        edit_link = finditem(lambda x: x.get('rel') == 'edit',
                feed.findall(_ns('link')))
        uri = edit_link.get('href')

        self.client.put_cell(uri, ElementTree.tostring(feed))

    def _create_update_feed(self, cell_list):
        feed = Element('feed',
                      {'xmlns': 'http://www.w3.org/2005/Atom',
                       'xmlns:batch': 'http://schemas.google.com/gdata/batch',
                       'xmlns:gs': 'http://schemas.google.com/spreadsheets/2006'})

        id_elem = SubElement(feed, 'id')

        id_elem.text = construct_url('cells', self)

        for cell in cell_list:
            entry = SubElement(feed, 'entry')

            SubElement(entry, 'batch:id').text = cell.element.find(_ns('title')).text
            SubElement(entry, 'batch:operation', {'type': 'update'})
            SubElement(entry, 'id').text = cell.element.find(_ns('id')).text

            edit_link = finditem(lambda x: x.get('rel') == 'edit',
                    cell.element.findall(_ns('link')))

            SubElement(entry, 'link', {'rel': 'edit',
                                       'type': edit_link.get('type'),
                                       'href': edit_link.get('href')})

            SubElement(entry, 'gs:cell', {'row': cell.row,
                                          'col': cell.col,
                                          'inputValue': cell.value})
        return feed

    def update_cells(self, cell_list):
        """Cells batch update."""
        feed = self._create_update_feed(cell_list)
        self.client.post_cells(self, ElementTree.tostring(feed))


class Cell(object):
    """An instance of this class represents a single cell in a spreadsheet.

    """
    def __init__(self, worksheet, element):
        self.element = element
        cell_elem = element.find(_ns1('cell'))
        self._row = cell_elem.get('row')
        self._col = cell_elem.get('col')

        #: Value of the cell.
        self.value = cell_elem.text

    @property
    def row(self):
        """Row number of the cell."""
        return self._row

    @property
    def col(self):
        """Column number of the cell."""
        return self._col

    def __repr__(self):
        return '<%s R%sC%s "%s">' % (self.__class__.__name__,
                                     self.row,
                                     self.col,
                                     self.value)
