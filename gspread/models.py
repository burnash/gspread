# -*- coding: utf-8 -*-

"""
gspread.models
~~~~~~~~~~~~~~

This module contains common spreadsheets' models

"""
import re
from collections import defaultdict
from itertools import chain

from xml.etree import ElementTree
from xml.etree.ElementTree import Element, SubElement

from .ns import _ns, _ns1, ATOM_NS, BATCH_NS, SPREADSHEET_NS
from .urls import construct_url
from .utils import finditem, numericise_all

from .exceptions import IncorrectCellLabel, WorksheetNotFound, CellNotFound


try:
    unicode
except NameError:
    basestring = unicode = str


class Spreadsheet(object):
    """A class for a spreadsheet object.

    """
    def __init__(self, client, feed_entry):
        self.client = client
        id_parts = feed_entry.find(_ns('id')).text.split('/')
        self.id = id_parts[-1]
        self._sheet_list = []

    def get_id_fields(self):
        return {'spreadsheet_id': self.id}

    def _fetch_sheets(self):
        feed = self.client.get_worksheets_feed(self)
        for elem in feed.findall(_ns('entry')):
            self._sheet_list.append(Worksheet(self, elem))

    def add_worksheet(self, title, rows, cols):
        """Adds a new worksheet to a spreadsheet.

        :param title: A title of a new worksheet.
        :param rows: Number of rows.
        :param cols: Number of columns.

        Returns a newly created :class:`worksheets <Worksheet>`.
        """
        feed = Element('entry', {'xmlns': ATOM_NS,
                                'xmlns:gs': SPREADSHEET_NS})

        SubElement(feed, 'title').text = title
        SubElement(feed, 'gs:rowCount').text = str(rows)
        SubElement(feed, 'gs:colCount').text = str(cols)

        url = construct_url('worksheets', self)
        elem = self.client.post_feed(url, ElementTree.tostring(feed))

        worksheet = Worksheet(self, elem)
        self._sheet_list.append(worksheet)

        return worksheet

    def worksheets(self):
        """Returns a list of all :class:`worksheets <Worksheet>` in a spreadsheet.

        """
        if not self._sheet_list:
            self._fetch_sheets()
        return self._sheet_list[:]

    def worksheet(self, title):
        """Returns a worksheet with specified `title`.

        The returning object is an instance of :class:`Worksheet`.

        :param title: A title of a worksheet. If there're multiple
                      worksheets with the same title, first one will
                      be returned.

        Example. Getting worksheet named 'Annual bonuses'

        >>> sht = client.open('Sample one')
        >>> worksheet = sht.worksheet('Annual bonuses')

        """
        if not self._sheet_list:
            self._fetch_sheets()

        try:
            return finditem(lambda x: x.title == title, self._sheet_list)
        except StopIteration:
            raise WorksheetNotFound(title)


    def get_worksheet(self, index):
        """Returns a worksheet with specified `index`.

        The returning object is an instance of :class:`Worksheet`.

        :param index: An index of a worksheet. Indexes start from zero.

        Example. To get first worksheet of a spreadsheet:

        >>> sht = client.open('My fancy spreadsheet')
        >>> worksheet = sht.get_worksheet(0)

        Returns `None` if the worksheet is not found.
        """
        if not self._sheet_list:
            self._fetch_sheets()
        try:
            return self._sheet_list[index]
        except IndexError:
            return None

    @property
    def sheet1(self):
        """Shortcut property for getting the first worksheet."""
        return self.get_worksheet(0)


class Worksheet(object):
    """A class for worksheet object.

    """
    def __init__(self, spreadsheet, element):
        self.spreadsheet = spreadsheet
        self.client = spreadsheet.client
        self._id = element.find(_ns('id')).text.split('/')[-1]
        self._title = element.find(_ns('title')).text
        self._element = element

    def __repr__(self):
        return '<%s "%s" id:%s>' % (self.__class__.__name__,
                                     self.title,
                                     self.id)

    @property
    def id(self):
        """Id of a worksheet."""
        return self._id

    @property
    def title(self):
        """Title of a worksheet."""
        return self._title

    @property
    def row_count(self):
        """Number of rows"""
        return int(self._element.find(_ns1('rowCount')).text)

    @property
    def col_count(self):
        """Number of columns"""
        return int(self._element.find(_ns1('colCount')).text)

    @property
    def updated(self):
        """Updated time in RFC 3339 format"""
        return self._element.find(_ns('updated')).text

    def get_id_fields(self):
        return {'spreadsheet_id': self.spreadsheet.id,
                'worksheet_id': self.id}

    def _cell_addr(self, row, col):
        return 'R%sC%s' % (row, col)

    def _get_link(self, link_type, feed):
        return finditem(lambda x: x.get('rel') == link_type,
                feed.findall(_ns('link')))

    def _fetch_cells(self):
        feed = self.client.get_cells_feed(self)
        return [Cell(self, elem) for elem in feed.findall(_ns('entry'))]

    _cell_addr_re = re.compile(r'([A-Za-z]+)(\d+)')
    def get_int_addr(self, label):
        """Translates cell's label address to a tuple of integers.

        The result is a tuple containing `row` and `column` numbers.

        :param label: String with cell label in common format, e.g. 'B1'.
                      Letter case is ignored.

        Example:

        >>> wks.get_int_addr('A1')
        (1, 1)

        """
        magic_number = 96
        m = self._cell_addr_re.match(label)
        if m:
            column_label = m.group(1).lower()
            row = int(m.group(2))

            col = 0
            for i, c in enumerate(reversed(column_label)):
                col += (ord(c) - magic_number) * (26 ** i)
        else:
            raise IncorrectCellLabel(label)

        return (row, col)

    def acell(self, label):
        """Returns an instance of a :class:`Cell`.

        :param label: String with cell label in common format, e.g. 'B1'.
                      Letter case is ignored.

        Example:

        >>> wks.acell('A1') # this could be 'a1' as well
        <Cell R1C1 "I'm cell A1">

        """
        return self.cell(*(self.get_int_addr(label)))

    def cell(self, row, col):
        """Returns an instance of a :class:`Cell` positioned in `row`
           and `col` column.

        :param row: Integer row number.
        :param col: Integer column number.

        Example:

        >>> wks.cell(1, 1)
        <Cell R1C1 "I'm cell A1">

        """
        feed = self.client.get_cells_cell_id_feed(self,
                                                  self._cell_addr(row, col))
        return Cell(self, feed)

    def range(self, alphanum):
        """Returns a list of :class:`Cell` objects from specified range.

        :param alphanum: A string with range value in common format,
                         e.g. 'A1:A5'.

        """
        feed = self.client.get_cells_feed(self, params={'range': alphanum,
                                                        'return-empty': 'true'})
        return [Cell(self, elem) for elem in feed.findall(_ns('entry'))]

    def get_all_values(self):
        """Returns a list of lists containing all cells' values as strings."""
        cells = self._fetch_cells()

        # defaultdicts fill in gaps for empty rows/cells not returned by gdocs
        rows = defaultdict(lambda: defaultdict(str))
        for cell in cells:
            row = rows.setdefault(int(cell.row), defaultdict(str))
            row[cell.col] = cell.value

        # we return a whole rectangular region worth of cells, including empties
        all_row_keys = chain.from_iterable(row.keys() for row in rows.values())
        rect_cols = range(1, max(all_row_keys)+1)
        rect_rows = range(1, max(rows.keys())+1)

        return [[rows[i][j] for j in rect_cols] for i in rect_rows]

    def get_all_records(self, empty2zero=False):
        """Returns a list of dictionaries, all of them having:
            - the contents of the spreadsheet's first row of cells as keys,
            And each of these dictionaries holding
            - the contents of subsequent rows of cells as values.
 

        Cell values are numericised (strings that can be read as ints 
        or floats are converted).

        :param empty2zero: determines whether empty cells are converted to zeros."""

        data = self.get_all_values()
        keys = data[0]
        values = [numericise_all(row, empty2zero) for row in data[1:]]

        return [dict(zip(keys, row)) for row in values]


    def _list_values(self, index, cell_tuple, position):
        cells_list = self._fetch_cells()
        cells = dict(map(cell_tuple, filter(position, cells_list)))

        try:
            last_index = max(cells.keys())
        except ValueError:
            return []

        vals = []
        for i in range(1, last_index + 1):
            c = cells.get(i)
            vals.append(c.value if c else None)

        return vals

    def row_values(self, row):
        """Returns a list of all values in a `row`.

        Empty cells in this list will be rendered as :const:`None`.

        """
        return self._list_values(row,
                                 lambda cell: (cell.col, cell),
                                 lambda cell: cell.row == row)

    def col_values(self, col):
        """Returns a list of all values in column `col`.

        Empty cells in this list will be rendered as :const:`None`.

        """
        return self._list_values(col,
                                 lambda cell: (cell.row, cell),
                                 lambda cell: cell.col == col)

    def update_acell(self, label, val):
        """Sets the new value to a cell.

        :param label: String with cell label in common format, e.g. 'B1'.
                      Letter case is ignored.
        :param val: New value.

        Example:

        >>> wks.update_acell('A1', '42') # this could be 'a1' as well
        <Cell R1C1 "I'm cell A1">

        """
        return self.update_cell(*(self.get_int_addr(label)), val=val)

    def update_cell(self, row, col, val):
        """Sets the new value to a cell.

        :param row: Row number.
        :param col: Column number.
        :param val: New value.

        """
        feed = self.client.get_cells_cell_id_feed(self,
                                                  self._cell_addr(row, col))
        cell_elem = feed.find(_ns1('cell'))
        cell_elem.set('inputValue', unicode(val))
        uri = self._get_link('edit', feed).get('href')

        self.client.put_feed(uri, ElementTree.tostring(feed))

    def _create_update_feed(self, cell_list):
        feed = Element('feed', {'xmlns': ATOM_NS,
                                'xmlns:batch': BATCH_NS,
                                'xmlns:gs': SPREADSHEET_NS})

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

            SubElement(entry, 'gs:cell', {'row': str(cell.row),
                                          'col': str(cell.col),
                                          'inputValue': unicode(cell.value)})
        return feed

    def update_cells(self, cell_list):
        """Updates cells in batch.

        :param cell_list: List of a :class:`Cell` objects to update.

        """
        feed = self._create_update_feed(cell_list)
        self.client.post_cells(self, ElementTree.tostring(feed))

    def resize(self, rows=None, cols=None):
        """Resizes the worksheet.

        :param rows: New rows number.
        :param cols: New columns number.
        """
        if rows is None and cols is None:
            raise TypeError("Either 'rows' or 'cols' should be specified.")

        self_uri = self._get_link('self', self._element).get('href')
        feed = self.client.get_feed(self_uri)
        uri = self._get_link('edit', feed).get('href')

        if rows:
            elem = feed.find(_ns1('rowCount'))
            elem.text = str(rows)

        if cols:
            elem = feed.find(_ns1('colCount'))
            elem.text = str(cols)

        # Send request and store result
        self._element = self.client.put_feed(uri, ElementTree.tostring(feed))

    def add_rows(self, rows):
        """Adds rows to worksheet.

        :param rows: Rows number to add.
        """
        self.resize(rows=self.row_count + rows)

    def add_cols(self, cols):
        """Adds colums to worksheet.

        :param cols: Columns number to add.
        """
        self.resize(cols=self.col_count + cols)

    def append_row(self, values):
        """"Adds a row to the worksheet and populates it with values.
        Widens the worksheet if there are more values than columns.

        :param values: List of values for the new row.
        """
        self.add_rows(1)
        new_row = self.row_count
        data_width = len(values)
        if self.col_count < data_width:
            self.resize(cols=data_width)

        cell_list = []
        for i, value in enumerate(values, start=1):
            cell = self.cell(new_row, i)
            cell.value = value
            cell_list.append(cell)

        self.update_cells(cell_list)

    def _finder(self, func, query):
        cells = self._fetch_cells()

        if isinstance(query, basestring):
            match = lambda x: x.value == query
        else:
            match = lambda x: query.search(x.value)

        return func(match, cells)

    def find(self, query):
        """Finds first cell matching query.

        :param query: A text string or compiled regular expression.
        """
        try:
            return self._finder(finditem, query)
        except StopIteration:
            raise CellNotFound(query)

    def findall(self, query):
        """Finds all cells matching query.

        :param query: A text string or compiled regular expression.
        """
        return self._finder(filter, query)


class Cell(object):
    """An instance of this class represents a single cell in a :class:`worksheet <Worksheet>`.

    """
    def __init__(self, worksheet, element):
        self.element = element
        cell_elem = element.find(_ns1('cell'))
        self._row = int(cell_elem.get('row'))
        self._col = int(cell_elem.get('col'))

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
