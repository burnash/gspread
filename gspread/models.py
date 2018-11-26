# -*- coding: utf-8 -*-

"""
gspread.models
~~~~~~~~~~~~~~

This module contains common spreadsheets' models.

"""

from .exceptions import WorksheetNotFound, CellNotFound

from .utils import (
    a1_to_rowcol,
    rowcol_to_a1,
    cast_to_a1_notation,
    numericise_all,
    finditem,
    fill_gaps,
    cell_list_to_rect,
    quote
)

from .urls import (
    SPREADSHEET_URL,
    SPREADSHEET_VALUES_URL,
    SPREADSHEET_BATCH_UPDATE_URL,
    SPREADSHEET_VALUES_APPEND_URL,
    SPREADSHEET_VALUES_CLEAR_URL
)

try:
    unicode
except NameError:
    basestring = unicode = str


class Spreadsheet(object):
    """The class that represents a spreadsheet."""
    def __init__(self, client, properties):
        self.client = client
        self._properties = properties

    @property
    def id(self):
        """Spreadsheet ID."""
        return self._properties['id']

    @property
    def title(self):
        """Spreadsheet title."""
        try:
            return self._properties['title']
        except KeyError:
            metadata = self.fetch_sheet_metadata()
            self._properties.update(metadata['properties'])
            return self._properties['title']

    @property
    def updated(self):
        """.. deprecated:: 2.0

        This feature is not supported in Sheets API v4.
        """
        import warnings
        warnings.warn(
            "Spreadsheet.updated() is deprecated, "
            "this feature is not supported in Sheets API v4",
            DeprecationWarning,
            stacklevel=2
        )

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

    def batch_update(self, body):
        """Lower-level method that directly calls `spreadsheets.batchUpdate <https://developers.google.com/sheets/api/reference/rest/v4/spreadsheets/batchUpdate>`_.

        :param dict body: `Request body <https://developers.google.com/sheets/api/reference/rest/v4/spreadsheets/batchUpdate#request-body>`_.
        :returns: `Response body <https://developers.google.com/sheets/api/reference/rest/v4/spreadsheets/batchUpdate#response-body>`_.
        :rtype: dict

        .. versionadded:: 3.0

        """
        r = self.client.request(
            'post',
            SPREADSHEET_BATCH_UPDATE_URL % self.id,
            json=body
        )

        return r.json()

    def values_append(self, range, params, body):
        """Lower-level method that directly calls `spreadsheets.values.append <https://developers.google.com/sheets/api/reference/rest/v4/spreadsheets.values/append>`_.

        :param str range: The `A1 notation <https://developers.google.com/sheets/api/guides/concepts#a1_notation>`_
                          of a range to search for a logical table of data. Values will be appended after the last row of the table.
        :param dict params: `Query parameters <https://developers.google.com/sheets/api/reference/rest/v4/spreadsheets.values/append#query-parameters>`_.
        :param dict body: `Request body <https://developers.google.com/sheets/api/reference/rest/v4/spreadsheets.values/append#request-body>`_.
        :returns: `Response body <https://developers.google.com/sheets/api/reference/rest/v4/spreadsheets.values/append#response-body>`_.
        :rtype: dict

        .. versionadded:: 3.0

        """
        url = SPREADSHEET_VALUES_APPEND_URL % (self.id, quote(range))
        r = self.client.request('post', url, params=params, json=body)
        return r.json()

    def values_clear(self, range):
        """Lower-level method that directly calls `spreadsheets.values.clear <https://developers.google.com/sheets/api/reference/rest/v4/spreadsheets.values/clear>`_.

        :param str range: The `A1 notation <https://developers.google.com/sheets/api/guides/concepts#a1_notation>`_ of the values to clear.
        :returns: `Response body <https://developers.google.com/sheets/api/reference/rest/v4/spreadsheets.values/clear#response-body>`_.
        :rtype: dict

        .. versionadded:: 3.0

        """
        url = SPREADSHEET_VALUES_CLEAR_URL % (self.id, quote(range))
        r = self.client.request('post', url)
        return r.json()

    def values_get(self, range, params=None):
        """Lower-level method that directly calls `spreadsheets.values.get <https://developers.google.com/sheets/api/reference/rest/v4/spreadsheets.values/get>`_.

        :param str range: The `A1 notation <https://developers.google.com/sheets/api/guides/concepts#a1_notation>`_ of the values to retrieve.
        :param dict params: (optional) `Query parameters <https://developers.google.com/sheets/api/reference/rest/v4/spreadsheets.values/get#query-parameters>`_.
        :returns: `Response body <https://developers.google.com/sheets/api/reference/rest/v4/spreadsheets.values/get#response-body>`_.
        :rtype: dict

        .. versionadded:: 3.0

        """
        url = SPREADSHEET_VALUES_URL % (self.id, quote(range))
        r = self.client.request('get', url, params=params)
        return r.json()

    def values_update(self, range, params=None, body=None):
        """Lower-level method that directly calls `spreadsheets.values.update <https://developers.google.com/sheets/api/reference/rest/v4/spreadsheets.values/update>`_.

        :param str range: The `A1 notation <https://developers.google.com/sheets/api/guides/concepts#a1_notation>`_ of the values to update.
        :param dict params: (optional) `Query parameters <https://developers.google.com/sheets/api/reference/rest/v4/spreadsheets.values/update#query-parameters>`_.
        :param dict body: (optional) `Request body <https://developers.google.com/sheets/api/reference/rest/v4/spreadsheets.values/update#request-body>`_.
        :returns: `Response body <https://developers.google.com/sheets/api/reference/rest/v4/spreadsheets.values/update#response-body>`_.
        :rtype: dict

        Example::

            sh.values_update(
                'Sheet1!A2',
                params={
                    'valueInputOption': 'USER_ENTERED'
                },
                body={
                    'values': [[1, 2, 3]]
                }
            )

        .. versionadded:: 3.0

        """
        url = SPREADSHEET_VALUES_URL % (self.id, quote(range))
        r = self.client.request('put', url, params=params, json=body)
        return r.json()

    def fetch_sheet_metadata(self):
        params = {'includeGridData': 'false'}

        url = SPREADSHEET_URL % self.id

        r = self.client.request('get', url, params=params)

        return r.json()

    def get_worksheet(self, index):
        """Returns a worksheet with specified `index`.

        :param index: An index of a worksheet. Indexes start from zero.
        :type index: int

        :returns: an instance of :class:`gsperad.models.Worksheet`
                  or `None` if the worksheet is not found.

        Example. To get first worksheet of a spreadsheet:

        >>> sht = client.open('My fancy spreadsheet')
        >>> worksheet = sht.get_worksheet(0)

        """
        sheet_data = self.fetch_sheet_metadata()

        try:
            properties = sheet_data['sheets'][index]['properties']
            return Worksheet(self, properties)
        except (KeyError, IndexError):
            return None

    def worksheets(self):
        """Returns a list of all :class:`worksheets <gsperad.models.Worksheet>`
        in a spreadsheet.

        """
        sheet_data = self.fetch_sheet_metadata()
        return [Worksheet(self, x['properties']) for x in sheet_data['sheets']]

    def worksheet(self, title):
        """Returns a worksheet with specified `title`.

        :param title: A title of a worksheet. If there're multiple
                      worksheets with the same title, first one will
                      be returned.
        :type title: int

        :returns: an instance of :class:`gsperad.models.Worksheet`.

        Example. Getting worksheet named 'Annual bonuses'

        >>> sht = client.open('Sample one')
        >>> worksheet = sht.worksheet('Annual bonuses')

        """
        sheet_data = self.fetch_sheet_metadata()
        try:
            item = finditem(
                lambda x: x['properties']['title'] == title,
                sheet_data['sheets']
            )
            return Worksheet(self, item['properties'])
        except (StopIteration, KeyError):
            raise WorksheetNotFound(title)

    def add_worksheet(self, title, rows, cols):
        """Adds a new worksheet to a spreadsheet.

        :param title: A title of a new worksheet.
        :type title: str
        :param rows: Number of rows.
        :type rows: int
        :param cols: Number of columns.
        :type cols: int

        :returns: a newly created :class:`worksheets <gsperad.models.Worksheet>`.
        """
        body = {
            'requests': [{
                'addSheet': {
                    'properties': {
                        'title': title,
                        'sheetType': 'GRID',
                        'gridProperties': {
                            'rowCount': rows,
                            'columnCount': cols
                        }
                    }
                }
            }]
        }

        data = self.batch_update(body)

        properties = data['replies'][0]['addSheet']['properties']

        worksheet = Worksheet(self, properties)

        return worksheet

    def duplicate_sheet(
        self,
        source_sheet_id,
        insert_sheet_index=None,
        new_sheet_id=None,
        new_sheet_name=None
    ):
        """Duplicates the contents of a sheet.

        :param int source_sheet_id: The sheet ID to duplicate.
        :param int insert_sheet_index: (optional) The zero-based index
                                       where the new sheet should be inserted.
                                       The index of all sheets after this are
                                       incremented.
        :param int new_sheet_id: (optional) The ID of the new sheet.
                                 If not set, an ID is chosen. If set, the ID
                                 must not conflict with any existing sheet ID.
                                 If set, it must be non-negative.
        :param str new_sheet_name: (optional) The name of the new sheet.
                                   If empty, a new name is chosen for you.

        :returns: a newly created :class:`<gspread.models.Worksheet>`.

        .. versionadded:: 3.1.0

        """
        body = {
            'requests': [{
                'duplicateSheet': {
                    'sourceSheetId': source_sheet_id,
                    'insertSheetIndex': insert_sheet_index,
                    'newSheetId': new_sheet_id,
                    'newSheetName': new_sheet_name
                }
            }]
        }

        data = self.batch_update(body)

        properties = data['replies'][0]['duplicateSheet']['properties']

        worksheet = Worksheet(self, properties)

        return worksheet

    def del_worksheet(self, worksheet):
        """Deletes a worksheet from a spreadsheet.

        :param worksheet: The worksheet to be deleted.
        :type worksheet: :class:`~gspread.Worksheet`

        """
        body = {
            'requests': [{
                'deleteSheet': {'sheetId': worksheet._properties['sheetId']}
            }]
        }

        return self.batch_update(body)

    def share(self, value, perm_type, role, notify=True, email_message=None, with_link=False):
        """Share the spreadsheet with other accounts.

        :param value: user or group e-mail address, domain name
                      or None for 'default' type.
        :type value: str, None
        :param perm_type: The account type.
               Allowed values are: ``user``, ``group``, ``domain``,
               ``anyone``.
        :type perm_type: str
        :param role: The primary role for this user.
               Allowed values are: ``owner``, ``writer``, ``reader``.
        :type role: str
        :param notify: (optional) Whether to send an email to the target user/domain.
        :type notify: str
        :param email_message: (optional) The email to be sent if notify=True
        :type email_message: str

        :param with_link: (optional) Whether the link is required for this permission
        :type with_link: bool

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
            email_message=email_message,
            with_link=with_link
        )

    def list_permissions(self):
        """Lists the spreadsheet's permissions.
        """
        return self.client.list_permissions(self.id)

    def remove_permissions(self, value, role='any'):
        """Remove permissions from a user or domain.

        :param value: User or domain to remove permissions from
        :type value: str
        :param role: (optional) Permission to remove. Defaults to all
                     permissions.
        :type role: str

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
    """The class that represents a single sheet in a spreadsheet
    (aka "worksheet").

    """

    def __init__(self, spreadsheet, properties):
        self.spreadsheet = spreadsheet
        self.client = spreadsheet.client
        self._properties = properties

    def __repr__(self):
        return '<%s %s id:%s>' % (self.__class__.__name__,
                                  repr(self.title),
                                  self.id)

    @property
    def id(self):
        """Worksheet ID."""
        return self._properties['sheetId']

    @property
    def title(self):
        """Worksheet title."""
        return self._properties['title']

    @property
    def updated(self):
        """.. deprecated:: 2.0

        This feature is not supported in Sheets API v4.
        """
        import warnings
        warnings.warn(
            "Worksheet.updated() is deprecated, "
            "this feature is not supported in Sheets API v4",
            DeprecationWarning,
            stacklevel=2
        )

    @property
    def row_count(self):
        """Number of rows."""
        return self._properties['gridProperties']['rowCount']

    @property
    def col_count(self):
        """Number of columns."""
        return self._properties['gridProperties']['columnCount']

    def acell(self, label, value_render_option='FORMATTED_VALUE'):
        """Returns an instance of a :class:`gspread.models.Cell`.

        :param label: Cell label in A1 notation
                      Letter case is ignored.
        :type label: str
        :param value_render_option: (optional) Determines how values should be
                                    rendered in the the output. See
                                    `ValueRenderOption`_ in the Sheets API.
        :type value_render_option: str

        .. _ValueRenderOption: https://developers.google.com/sheets/api/reference/rest/v4/ValueRenderOption

        Example:

        >>> worksheet.acell('A1')
        <Cell R1C1 "I'm cell A1">

        """

        return self.cell(
            *(a1_to_rowcol(label)),
            value_render_option=value_render_option
        )

    def cell(self, row, col, value_render_option='FORMATTED_VALUE'):
        """Returns an instance of a :class:`gspread.models.Cell` located at
        `row` and `col` column.

        :param row: Row number.
        :type row: int
        :param col: Column number.
        :type col: int
        :param value_render_option: (optional) Determines how values should be
                                    rendered in the the output. See
                                    `ValueRenderOption`_ in the Sheets API.
        :type value_render_option: str

        .. _ValueRenderOption: https://developers.google.com/sheets/api/reference/rest/v4/ValueRenderOption

        Example:

        >>> worksheet.cell(1, 1)
        <Cell R1C1 "I'm cell A1">

        """

        range_label = '%s!%s' % (self.title, rowcol_to_a1(row, col))
        data = self.spreadsheet.values_get(
            range_label,
            params={'valueRenderOption': value_render_option}
        )

        try:
            value = data['values'][0][0]
        except KeyError:
            value = ''

        return Cell(row, col, value)

    @cast_to_a1_notation
    def range(self, name):
        """Returns a list of :class:`Cell` objects from a specified range.

        :param name: A string with range value in A1 notation, e.g. 'A1:A5'.
        :type name: str

        Alternatively, you may specify numeric boundaries. All values
        index from 1 (one):

        :param first_row: Row number
        :type first_row: int
        :param first_col: Row number
        :type first_col: int
        :param last_row: Row number
        :type last_row: int
        :param last_col: Row number
        :type last_col: int

        Example::

            >>> # Using A1 notation
            >>> worksheet.range('A1:B7')
            [<Cell R1C1 "42">, ...]

            >>> # Same with numeric boundaries
            >>> worksheet.range(1, 1, 7, 2)
            [<Cell R1C1 "42">, ...]

        """

        range_label = '%s!%s' % (self.title, name)

        data = self.spreadsheet.values_get(range_label)

        start, end = name.split(':')
        (row_offset, column_offset) = a1_to_rowcol(start)
        (last_row, last_column) = a1_to_rowcol(end)

        values = data.get('values', [])

        rect_values = fill_gaps(
            values,
            rows=last_row - row_offset + 1,
            cols=last_column - column_offset + 1
        )

        return [
            Cell(row=i + row_offset, col=j + column_offset, value=value)
            for i, row in enumerate(rect_values)
            for j, value in enumerate(row)
        ]

    def get_all_values(self):
        """Returns a list of lists containing all cells' values as strings.

        .. note::

            Empty trailing rows and columns will not be included.
        """

        data = self.spreadsheet.values_get(self.title)

        try:
            return fill_gaps(data['values'])
        except KeyError:
            return []

    def get_all_records(
        self,
        empty2zero=False,
        head=1,
        default_blank="",
        allow_underscores_in_numeric_literals=False,
    ):
        """Returns a list of dictionaries, all of them having the contents
            of the spreadsheet with the head row as keys and each of these
            dictionaries holding the contents of subsequent rows of cells
            as values.

            Cell values are numericised (strings that can be read as ints
            or floats are converted).

            :param empty2zero: (optional) Determines whether empty cells are
                               converted to zeros.
            :type empty2zero: bool
            :param head: (optional) Determines wich row to use as keys, starting
                         from 1 following the numeration of the spreadsheet.
            :type head: int
            :param default_blank: (optional) Determines whether empty cells are
                                  converted to something else except empty string
                                  or zero.
            :type default_blank: str
            :param allow_underscores_in_numeric_literals: (optional) Allow underscores
                                                          in numeric literals,
                                                          as introduced in PEP 515
            :type allow_underscores_in_numeric_literals: bool
            """

        idx = head - 1

        data = self.get_all_values()
        keys = data[idx]
        values = [
            numericise_all(
                row,
                empty2zero,
                default_blank,
                allow_underscores_in_numeric_literals,
            )
            for row in data[idx + 1:]
        ]

        return [dict(zip(keys, row)) for row in values]

    def row_values(self, row, value_render_option='FORMATTED_VALUE'):
        """Returns a list of all values in a `row`.

        Empty cells in this list will be rendered as :const:`None`.

        :param row: Row number.
        :type row: int
        :param value_render_option: (optional) Determines how values should be
                                    rendered in the the output. See
                                    `ValueRenderOption`_ in the Sheets API.
        :type value_render_option: str

        .. _ValueRenderOption: https://developers.google.com/sheets/api/reference/rest/v4/ValueRenderOption

        """

        range_label = '%s!A%s:%s' % (self.title, row, row)

        data = self.spreadsheet.values_get(
            range_label,
            params={'valueRenderOption': value_render_option}
        )

        try:
            return data['values'][0]
        except KeyError:
            return []

    def col_values(self, col, value_render_option='FORMATTED_VALUE'):
        """Returns a list of all values in column `col`.

        Empty cells in this list will be rendered as :const:`None`.

        :param col: Column number.
        :type col: int
        :param value_render_option: (optional) Determines how values should be
                                    rendered in the the output. See
                                    `ValueRenderOption`_ in the Sheets API.
        :type value_render_option: str

        .. _ValueRenderOption: https://developers.google.com/sheets/api/reference/rest/v4/ValueRenderOption

        """

        start_label = rowcol_to_a1(1, col)
        range_label = '%s!%s:%s' % (self.title, start_label, start_label[:-1])

        data = self.spreadsheet.values_get(
            range_label,
            params={
                'valueRenderOption': value_render_option,
                'majorDimension': 'COLUMNS'
            }
        )

        try:
            return data['values'][0]
        except KeyError:
            return []

    def update_acell(self, label, value):
        """Updates the value of a cell.

        :param label: Cell label in A1 notation.
                      Letter case is ignored.
        :type label: str
        :param value: New value.

        Example::

            worksheet.update_acell('A1', '42')

        """
        return self.update_cell(*(a1_to_rowcol(label)), value=value)

    def update_cell(self, row, col, value):
        """Updates the value of a cell.

        :param row: Row number.
        :type row: int
        :param col: Column number.
        :type col: int
        :param value: New value.

        Example::

            worksheet.update_cell(1, 1, '42')

        """
        range_label = '%s!%s' % (self.title, rowcol_to_a1(row, col))

        data = self.spreadsheet.values_update(
            range_label,
            params={
                'valueInputOption': 'USER_ENTERED'
            },
            body={
                'values': [[value]]
            }
        )

        return data

    def update_cells(self, cell_list, value_input_option='RAW'):
        """Updates many cells at once.

        :param cell_list: List of :class:`Cell` objects to update.
        :param value_input_option: (optional) Determines how input data should
                                    be interpreted. See `ValueInputOption`_ in
                                    the Sheets API.
        :type value_input_option: str

        .. _ValueInputOption: https://developers.google.com/sheets/api/reference/rest/v4/ValueInputOption

        Example::

            # Select a range
            cell_list = worksheet.range('A1:C7')

            for cell in cell_list:
                cell.value = 'O_o'

            # Update in batch
            worksheet.update_cells(cell_list)

        """

        values_rect = cell_list_to_rect(cell_list)

        start = rowcol_to_a1(min(c.row for c in cell_list), min(c.col for c in cell_list))
        end = rowcol_to_a1(max(c.row for c in cell_list), max(c.col for c in cell_list))

        range_label = '%s!%s:%s' % (self.title, start, end)

        data = self.spreadsheet.values_update(
            range_label,
            params={
                'valueInputOption': value_input_option
            },
            body={
                'values': values_rect
            }
        )

        return data

    def resize(self, rows=None, cols=None):
        """Resizes the worksheet. Specify one of ``rows`` or ``cols``.

        :param rows: (optional) New number of rows.
        :type rows: int
        :param cols: (optional) New number columns.
        :type cols: int
        """
        grid_properties = {}

        if rows is not None:
            grid_properties['rowCount'] = rows

        if cols is not None:
            grid_properties['columnCount'] = cols

        if not grid_properties:
            raise TypeError("Either 'rows' or 'cols' should be specified.")

        fields = ','.join(
            'gridProperties/%s' % p for p in grid_properties.keys()
        )

        body = {
            'requests': [{
                'updateSheetProperties': {
                    'properties': {
                        'sheetId': self.id,
                        'gridProperties': grid_properties
                    },
                    'fields': fields
                }
            }]
        }

        return self.spreadsheet.batch_update(body)

    def update_title(self, title):
        """Renames the worksheet.

        :param title: A new title.
        :type title: str

        """

        body = {
            'requests': [{
                'updateSheetProperties': {
                    'properties': {
                        'sheetId': self.id,
                        'title': title
                    },
                    'fields': 'title'
                }
            }]
        }

        response = self.spreadsheet.batch_update(body)
        self._properties['title'] = title
        return response

    def add_rows(self, rows):
        """Adds rows to worksheet.

        :param rows: Number of new rows to add.
        :type rows: int

        """
        self.resize(rows=self.row_count + rows)

    def add_cols(self, cols):
        """Adds colums to worksheet.

        :param cols: Number of new columns to add.
        :type cols: int

        """
        self.resize(cols=self.col_count + cols)

    def append_row(self, values, value_input_option='RAW'):
        """Adds a row to the worksheet and populates it with values.
        Widens the worksheet if there are more values than columns.

        :param values: List of values for the new row.
        :param value_input_option: (optional) Determines how input data should
                                    be interpreted. See `ValueInputOption`_ in
                                    the Sheets API.
        :type value_input_option: str

        .. _ValueInputOption: https://developers.google.com/sheets/api/reference/rest/v4/ValueInputOption

        """
        params = {
            'valueInputOption': value_input_option
        }

        body = {
            'values': [values]
        }

        return self.spreadsheet.values_append(self.title, params, body)

    def insert_row(
        self,
        values,
        index=1,
        value_input_option='RAW'
    ):
        """Adds a row to the worksheet at the specified index
        and populates it with values.

        Widens the worksheet if there are more values than columns.

        :param values: List of values for the new row.
        :param index: (optional) Offset for the newly inserted row.
        :type index: int
        :param value_input_option: (optional) Determines how input data should
                                    be interpreted. See `ValueInputOption`_ in
                                    the Sheets API.
        :type value_input_option: str

        .. _ValueInputOption: https://developers.google.com/sheets/api/reference/rest/v4/ValueInputOption

        """

        body = {
            "requests": [{
                "insertDimension": {
                    "range": {
                      "sheetId": self.id,
                      "dimension": "ROWS",
                      "startIndex": index - 1,
                      "endIndex": index
                    }
                }
            }]
        }

        self.spreadsheet.batch_update(body)

        range_label = '%s!%s' % (self.title, 'A%s' % index)

        data = self.spreadsheet.values_update(
            range_label,
            params={
                'valueInputOption': value_input_option
            },
            body={
                'values': [values]
            }
        )

        return data

    def delete_row(self, index):
        """"Deletes the row from the worksheet at the specified index.

        :param index: Index of a row for deletion.
        :type index: int
        """
        body = {
            "requests": [{
                "deleteDimension": {
                    "range": {
                      "sheetId": self.id,
                      "dimension": "ROWS",
                      "startIndex": index - 1,
                      "endIndex": index
                    }
                }
            }]
        }

        return self.spreadsheet.batch_update(body)

    def clear(self):
        """Clears all cells in the worksheet.
        """
        return self.spreadsheet.values_clear(self.title)

    def _finder(self, func, query):
        data = self.spreadsheet.values_get(self.title)

        try:
            values = fill_gaps(data['values'])
        except KeyError:
            values = []

        cells = [
            Cell(row=i + 1, col=j + 1, value=value)
            for i, row in enumerate(values)
            for j, value in enumerate(row)
        ]

        if isinstance(query, basestring):
            match = lambda x: x.value == query
        else:
            match = lambda x: query.search(x.value)

        return func(match, cells)

    def find(self, query):
        """Finds the first cell matching the query.

        :param query: A literal string to match or compiled regular expression.
        :type query: str, :py:class:`re.RegexObject`

        """
        try:
            return self._finder(finditem, query)
        except StopIteration:
            raise CellNotFound(query)

    def findall(self, query):
        """Finds all cells matching the query.

        :param query: A literal string to match or compiled regular expression.
        :type query: str, :py:class:`re.RegexObject`

        """
        return list(self._finder(filter, query))

    def export(self, format):
        """.. deprecated:: 2.0

        This feature is not supported in Sheets API v4.
        """
        import warnings
        warnings.warn(
            "Worksheet.export() is deprecated, "
            "this feature is not supported in Sheets API v4",
            DeprecationWarning,
            stacklevel=2
        )

    def duplicate(
        self,
        insert_sheet_index=None,
        new_sheet_id=None,
        new_sheet_name=None
    ):
        """Duplicate the sheet.

        :param int insert_sheet_index: (optional) The zero-based index
                                       where the new sheet should be inserted.
                                       The index of all sheets after this are
                                       incremented.
        :param int new_sheet_id: (optional) The ID of the new sheet.
                                 If not set, an ID is chosen. If set, the ID
                                 must not conflict with any existing sheet ID.
                                 If set, it must be non-negative.
        :param str new_sheet_name: (optional) The name of the new sheet.
                                   If empty, a new name is chosen for you.

        :returns: a newly created :class:`<gspread.models.Worksheet>`.

        .. versionadded:: 3.1.0

        """
        return self.spreadsheet.duplicate_sheet(
            self.id,
            insert_sheet_index,
            new_sheet_id,
            new_sheet_name
        )


class Cell(object):
    """An instance of this class represents a single cell
    in a :class:`worksheet <gspread.models.Worksheet>`.

    """

    def __init__(self, row, col, value=''):
        self._row = row
        self._col = col

        #: Value of the cell.
        self.value = value

    def __repr__(self):
        return '<%s R%sC%s %s>' % (self.__class__.__name__,
                                   self.row,
                                   self.col,
                                   repr(self.value))

    @property
    def row(self):
        """Row number of the cell."""
        return self._row

    @property
    def col(self):
        """Column number of the cell."""
        return self._col

    @property
    def numeric_value(self):
        try:
            return float(self.value)
        except ValueError:
            return None

    @property
    def input_value(self):
        """.. deprecated:: 2.0

        This feature is not supported in Sheets API v4.
        """
        import warnings
        warnings.warn(
            "Cell.input_value is deprecated, "
            "this feature is not supported in Sheets API v4. "
            "Please use `value_render_option` when you "
            "Retrieve `Cell` objects (e.g. in `Worksheet.range()` method).",
            DeprecationWarning,
            stacklevel=2
        )
