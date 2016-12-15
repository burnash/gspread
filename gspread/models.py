# -*- coding: utf-8 -*-

"""
gspread.models
~~~~~~~~~~~~~~

This module contains common spreadsheets' models

"""

from collections import defaultdict
from itertools import chain
from functools import wraps

from xml.etree import ElementTree
from xml.etree.ElementTree import Element, SubElement

from . import urlencode
from .ns import _ns, _ns1, ATOM_NS, BATCH_NS, SPREADSHEET_NS
from .urls import construct_url
from .utils import finditem, numericise_all
from .utils import rowcol_to_a1, a1_to_rowcol

from .exceptions import (
    IncorrectCellLabel, WorksheetNotFound, CellNotFound, ImportException
)

try:
    unicode
except NameError:
    basestring = unicode = str

# Patch ElementTree._escape_attrib
_elementtree_escape_attrib = ElementTree._escape_attrib


def _escape_attrib(text, encoding=None, replace=None):
    try:
        text = _elementtree_escape_attrib(text)
    except TypeError as e:
        if str(e) == '_escape_attrib() takes exactly 2 arguments (1 given)':
            text = _elementtree_escape_attrib(text, encoding)
    entities = {'\n': '&#10;', '\r': '&#13;', '\t': '&#9;'}
    for key, value in entities.items():
        text = text.replace(key, value)
    return text


ElementTree._escape_attrib = _escape_attrib


def cast_to_a1_notation(method):
    """
    Decorator function casts wrapped arguments to A1 notation
    in range method calls.
    """
    @wraps(method)
    def wrapper(self, *args, **kwargs):
        try:
            if len(args):
                int(args[0])

            # Convert to A1 notation
            range_start = rowcol_to_a1(*args[:2])
            range_end = rowcol_to_a1(*args[-2:])
            range_name = ':'.join((range_start, range_end))

            args = (range_name,) + args[4:]
        except ValueError:
            pass

        return method(self, *args, **kwargs)

    return wrapper


class Spreadsheet(object):
    """ A class for a spreadsheet object."""

    def __init__(self, client, feed_entry):
        self.client = client
        self._sheet_list = []
        self._feed_entry = feed_entry
        self._id = feed_entry.find(_ns('id')).text.split('/')[-1]
        self._title = feed_entry.find(_ns('title')).text
        self._updated = feed_entry.find(_ns('updated')).text

    @property
    def id(self):
        """Spreadsheet ID."""
        return self._id

    @property
    def title(self):
        """Spreadsheet title."""
        return self._title

    @property
    def updated(self):
        """Updated time in RFC 3339 format"""
        return self._updated

    @property
    def sheet1(self):
        """Shortcut property for getting the first worksheet."""
        return self.get_worksheet(0)

    def __iter__(self):
        for sheet in self.worksheets():
            yield(sheet)

    def __repr__(self):
        return '<%s %s id:%s>' % (self.__class__.__name__,
                                  repr(self.title),
                                  self.id)

    def get_id_fields(self):
        return {'spreadsheet_id': self.id}

    def _fetch_sheets(self):
        self._sheet_list = []
        feed = self.client.get_worksheets_feed(self)
        for elem in feed.findall(_ns('entry')):
            self._sheet_list.append(Worksheet(self, elem))

    def add_worksheet(self, title, rows, cols):
        """Adds a new worksheet to a spreadsheet.

        :param title: A title of a new worksheet.
        :param rows: Number of rows.
        :param cols: Number of columns.

        :returns: a newly created :class:`worksheets <Worksheet>`.
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

    def del_worksheet(self, worksheet):
        """Deletes a worksheet from a spreadsheet.

        :param worksheet: The worksheet to be deleted.

        """
        self.client.del_worksheet(worksheet)
        self._sheet_list.remove(worksheet)

    def worksheets(self):
        """Returns a list of all :class:`worksheets <Worksheet>`
        in a spreadsheet.

        """
        if not self._sheet_list:
            self._fetch_sheets()
        return self._sheet_list[:]

    def worksheet(self, title):
        """Returns a worksheet with specified `title`.

        :param title: A title of a worksheet. If there're multiple
                      worksheets with the same title, first one will
                      be returned.

        :returns: an instance of :class:`Worksheet`.

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

        :param index: An index of a worksheet. Indexes start from zero.

        :returns: an instance of :class:`Worksheet`
                  or `None` if the worksheet is not found.

        Example. To get first worksheet of a spreadsheet:

        >>> sht = client.open('My fancy spreadsheet')
        >>> worksheet = sht.get_worksheet(0)

        """
        if not self._sheet_list:
            self._fetch_sheets()
        try:
            return self._sheet_list[index]
        except IndexError:
            return None

    def share(self, value, perm_type, role, notify=True, email_message=None):
        """Share the spreadsheet with other accounts.
        :param value: user or group e-mail address, domain name
                      or None for 'default' type.
        :param perm_type: the account type.
               Allowed values are: ``user``, ``group``, ``domain``,
               ``anyone``.
        :param role: the primary role for this user.
               Allowed values are: ``owner``, ``writer``, ``reader``.
        :param notify: Whether to send an email to the target user/domain.
        :param email_message: The email to be sent if notify=True

        Example::

            # Give Otto a write permission on this spreadsheet
            sh.share('otto@example.com', perm_type='user', role='writer')

            # Transfer ownership to Otto
            sh.share('otto@example.com', perm_type='user', role='owner')

        """
        self.client.insert_permission(
            self.id,
            value=value,
            perm_type=perm_type,
            role=role,
            notify=notify,
            email_message=email_message
        )

    def list_permissions(self):
        """Lists the spreadsheet's permissions.
        """
        return self.client.list_permissions(self.id)

    def remove_permissions(self, value, role='any'):
        """
        Example::

            # Remove Otto's write permission for this spreadsheet
            sh.remove_permissions('otto@example.com', role='writer')

            # Remove all Otto's permissions for this spreadsheet
            sh.remove_permissions('otto@example.com')
        """
        permission_list = self.client.list_permissions(self.id)

        key = 'emailAddress' if '@' in value else 'domain'

        filtered_id_list = [
            p['id'] for p in permission_list
            if p[key] == value and (p['role'] == role or role == 'any')
        ]

        for permission_id in filtered_id_list:
            self.client.remove_permission(self.id, permission_id)

        return filtered_id_list


class Worksheet(object):

    """A class for worksheet object."""

    def __init__(self, spreadsheet, element):
        self.spreadsheet = spreadsheet
        self.client = spreadsheet.client
        self._id = element.find(_ns('id')).text.split('/')[-1]
        self._title = element.find(_ns('title')).text
        self._element = element
        try:
            self.version = self._get_link(
                'edit', element).get('href').split('/')[-1]
        except:
            # not relevant for read-only spreadsheets
            self.version = None

    def __repr__(self):
        return '<%s %s id:%s>' % (self.__class__.__name__,
                                  repr(self.title),
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

    def get_int_addr(self, label):
        """Translates cell's label address to a tuple of integers.

        .. deprecated:: 0.5
           Use :func:`utils.a1_to_rowcol` instead.

        """
        import warnings
        warnings.warn(
            "Worksheet.get_int_addr() is deprecated, "
            "use utils.a1_to_rowcol() instead",
            DeprecationWarning
        )
        return a1_to_rowcol(label)

    def get_addr_int(self, row, col):
        """Translates cell's tuple of integers to a cell label.

        .. deprecated:: 0.5
           Use :func:`utils.rowcol_to_a1` instead.

        """
        import warnings
        warnings.warn(
            "Worksheet.get_addr_int() is deprecated, "
            "use utils.rowcol_to_a1() instead",
            DeprecationWarning
        )
        return rowcol_to_a1(row, col)

    def acell(self, label):
        """Returns an instance of a :class:`Cell`.

        :param label: String with cell label in common format, e.g. 'B1'.
                      Letter case is ignored.

        Example:

        >>> wks.acell('A1') # this could be 'a1' as well
        <Cell R1C1 "I'm cell A1">

        """
        return self.cell(*(a1_to_rowcol(label)))

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

    @cast_to_a1_notation
    def range(self, name):
        """Returns a list of :class:`Cell` objects from a specified range.

        :param name: A string with range value in A1 notation, e.g. 'A1:A5'.

        Alternatively, you may specify numeric boundaries. All values
        index from 1 (one):

        :param first_row: Integer row number
        :param first_col: Integer row number
        :param last_row: Integer row number
        :param last_col: Integer row number

        """
        feed = self.client.get_cells_feed(
            self,
            params={'range': name, 'return-empty': 'true'}
        )
        return [Cell(self, elem) for elem in feed.findall(_ns('entry'))]

    def get_all_values(self):
        """Returns a list of lists containing all cells' values as strings.
        """
        cells = self._fetch_cells()

        # defaultdicts fill in gaps for empty rows/cells not returned by gdocs
        rows = defaultdict(lambda: defaultdict(str))
        for cell in cells:
            row = rows.setdefault(int(cell.row), defaultdict(str))
            row[cell.col] = cell.value

        # we return a whole rectangular region worth of cells, including
        # empties
        if not rows:
            return []

        all_row_keys = chain.from_iterable(row.keys() for row in rows.values())
        rect_cols = range(1, max(all_row_keys) + 1)
        rect_rows = range(1, max(rows.keys()) + 1)

        return [[rows[i][j] for j in rect_cols] for i in rect_rows]

    def get_all_records(self, empty2zero=False, head=1, default_blank=""):
        """Returns a list of dictionaries, all of them having:
            - the contents of the spreadsheet's with the head row as keys,
            And each of these dictionaries holding
            - the contents of subsequent rows of cells as values.


        Cell values are numericised (strings that can be read as ints
        or floats are converted).

        :param empty2zero: determines whether empty cells are converted to zeros.
        :param head: determines wich row to use as keys, starting from 1
            following the numeration of the spreadsheet.
        :param default_blank: determines whether empty cells are converted to
            something else except empty string or zero.

        """
        idx = head - 1

        data = self.get_all_values()
        keys = data[idx]
        values = [numericise_all(row, empty2zero, default_blank)
                  for row in data[idx + 1:]]

        return [dict(zip(keys, row)) for row in values]

    def row_values(self, row):
        """Returns a list of all values in a `row`.

        Empty cells in this list will be rendered as :const:`None`.

        """
        start_cell = rowcol_to_a1(row, 1)
        end_cell = rowcol_to_a1(row, self.col_count)

        row_cells = self.range('%s:%s' % (start_cell, end_cell))
        return [cell.value for cell in row_cells]

    def col_values(self, col):
        """Returns a list of all values in column `col`.

        Empty cells in this list will be rendered as :const:`None`.

        """
        start_cell = rowcol_to_a1(1, col)
        end_cell = rowcol_to_a1(self.row_count, col)

        row_cells = self.range('%s:%s' % (start_cell, end_cell))
        return [cell.value for cell in row_cells]

    def update_acell(self, label, val):
        """Sets the new value to a cell.

        :param label: String with cell label in common format, e.g. 'B1'.
                      Letter case is ignored.
        :param val: New value.

        Example:

        >>> wks.update_acell('A1', '42') # this could be 'a1' as well
        <Cell R1C1 "I'm cell A1">

        """
        return self.update_cell(*(a1_to_rowcol(label)), val=val)

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

            SubElement(entry, 'batch:id').text = cell.element.find(
                _ns('title')).text
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

    def update_title(self, title):
        """Renames the worksheet.

        :param title: A new title.
        """

        self_uri = self._get_link('self', self._element).get('href')
        feed = self.client.get_feed(self_uri)
        uri = self._get_link('edit', feed).get('href')

        elem = feed.find(_ns('title'))
        elem.text = title

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
        """Adds a row to the worksheet and populates it with values.
        Widens the worksheet if there are more values than columns.

        Note that a new Google Sheet has 100 or 1000 rows by default. You
        may need to scroll down to find the new row.

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

    def insert_row(self, values, index=1):
        """"Adds a row to the worksheet at the specified index
        and populates it with values.

        Widens the worksheet if there are more values than columns.

        :param values: List of values for the new row.
        """
        if index == self.row_count + 1:
            return self.append_row(values)
        elif index > self.row_count + 1:
            raise IndexError('Row index out of range')

        self.add_rows(1)
        data_width = len(values)
        if self.col_count < data_width:
            self.resize(cols=data_width)

        # Retrieve all Cells at or below `index` using a single batch query
        top_left = rowcol_to_a1(index, 1)
        bottom_right = rowcol_to_a1(self.row_count, self.col_count)
        range_str = '%s:%s' % (top_left, bottom_right)

        cells_after_insert = self.range(range_str)

        for ind, cell in reversed(list(enumerate(cells_after_insert))):
            if ind < self.col_count:
                # For the first row, take the cell values from `values`
                new_val = values[ind] if ind < len(values) else ''
            else:
                # For all other rows, take the cell values from the row above
                new_val = cells_after_insert[ind - self.col_count].input_value
            cell.value = new_val

        self.update_cells(cells_after_insert)

    def delete_row(self, index):
        """"Deletes a row from the worksheet at the specified index

        :param index: Index of a row for deletion
        """
        if index < 1 or index > self.row_count:
            raise IndexError('Row index out of range')

        # Retrieve all Cells at or below `index` using a single batch query
        cells_after_delete = self.range(
            index, 1, self.row_count, self.col_count
        )

        # Shift rows up
        for ind, cell in enumerate(cells_after_delete):
            if ind + self.col_count >= len(cells_after_delete):
                break
            new_val = cells_after_delete[ind + self.col_count].input_value
            cell.value = new_val

        self.update_cells(cells_after_delete)

        # Remove last row
        self.resize(rows=self.row_count - 1)

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
        return list(self._finder(filter, query))

    def export(self, format='csv'):
        """Export the worksheet in specified format.

        :param format: A format of the output.
        """
        export_link = self._get_link(
            'http://schemas.google.com/spreadsheets/2006#exportcsv',
            self._element).get('href')

        url, qs = export_link.split('?')
        params = dict(param.split('=') for param in qs.split('&'))

        params['format'] = format

        params = urlencode(params)
        export_link = '%s?%s' % (url, params)

        return self.client.session.get(export_link).content

    def clear(self):
        """Clears all cells in the worksheet.
        """
        cells = self.range(1, 1, self.row_count, self.col_count)
        for cell in cells:
            cell.value = ''
        self.update_cells(cells)


class Cell(object):
    """An instance of this class represents a single cell
    in a :class:`worksheet <Worksheet>`.

    """

    def __init__(self, worksheet, element):
        self.element = element
        cell_elem = element.find(_ns1('cell'))
        self._row = int(cell_elem.get('row'))
        self._col = int(cell_elem.get('col'))
        self.input_value = cell_elem.get('inputValue')
        numeric_value = cell_elem.get('numericValue')
        self.numeric_value = float(numeric_value) if numeric_value else None

        #: Value of the cell.
        self.value = cell_elem.text or ''

    @property
    def row(self):
        """Row number of the cell."""
        return self._row

    @property
    def col(self):
        """Column number of the cell."""
        return self._col

    def __repr__(self):
        return '<%s R%sC%s %s>' % (self.__class__.__name__,
                                   self.row,
                                   self.col,
                                   repr(self.value))
