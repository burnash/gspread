from ..base import BaseCell, BaseSpreadsheet

from ..exceptions import WorksheetNotFound, CellNotFound

from ..utils import (
    a1_to_rowcol,
    rowcol_to_a1,
    cast_to_a1_notation,
    numericise_all,
    finditem
)

from .utils import fill_gaps, cell_list_to_rect

from .urls import (
    SPREADSHEET_URL,
    SPREADSHEET_VALUES_URL,
    SPREADSHEET_BATCH_UPDATE_URL,
    SPREADSHEET_APPEND_URL,
    SPREADSHEET_CLEAR_URL
)

try:
    unicode
except NameError:
    basestring = unicode = str


class Spreadsheet(BaseSpreadsheet):
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
        import warnings
        warnings.warn(
            "Spreadsheet.updated() is deprecated, "
            "this feature is not supported in Sheets API v4",
            DeprecationWarning
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

    def fetch_sheet_metadata(self):
        query_parameters = 'includeGridData=false'

        spreadsheet_url = SPREADSHEET_URL % self.id

        url = '%s?%s' % (spreadsheet_url, query_parameters)

        r = self.client.request('get', url)

        return r.json()

    def get_worksheet(self, index):
        sheet_data = self.fetch_sheet_metadata()

        try:
            properties = sheet_data['sheets'][index]['properties']
            return Worksheet(self, properties)
        except (KeyError, IndexError):
            return None

    def worksheets(self):
        """Returns a list of all :class:`worksheets <Worksheet>`
        in a spreadsheet.

        """
        sheet_data = self.fetch_sheet_metadata()
        return [Worksheet(self, x['properties']) for x in sheet_data['sheets']]

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
        payload = {
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

        r = self.client.request(
            'post',
            SPREADSHEET_BATCH_UPDATE_URL % self.id,
            json=payload
        )

        properties = r.json()['replies'][0]['addSheet']['properties']

        worksheet = Worksheet(self, properties)

        return worksheet

    def del_worksheet(self, worksheet):
        """Deletes a worksheet from a spreadsheet.

        :param worksheet: The worksheet to be deleted.

        """
        payload = {
            'requests': [{
                'deleteSheet': {'sheetId': worksheet._properties['sheetId']}
            }]
        }

        r = self.client.request(
            'post',
            SPREADSHEET_BATCH_UPDATE_URL % self.id,
            json=payload
        )

        return r.json()


class Worksheet(object):

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
        return self._properties['sheetId']

    @property
    def title(self):
        """Title of a worksheet."""
        return self._properties['title']

    @property
    def updated(self):
        import warnings
        warnings.warn(
            "Worksheet.updated() is deprecated, "
            "this feature is not supported in Sheets API v4",
            DeprecationWarning
        )

    @property
    def row_count(self):
        """Number of rows"""
        return self._properties['gridProperties']['rowCount']

    @property
    def col_count(self):
        """Number of columns"""
        return self._properties['gridProperties']['columnCount']

    def acell(self, label, value_render_option='FORMATTED_VALUE'):
        return self.cell(*(a1_to_rowcol(label)), value_render_option)

    def cell(self, row, col, value_render_option='FORMATTED_VALUE'):
        query_parameters = 'valueRenderOption=%s' % value_render_option
        label = '%s!%s' % (self.title, rowcol_to_a1(row, col))

        values_url = SPREADSHEET_VALUES_URL % (
            self.spreadsheet.id,
            label
        )

        url = '%s?%s' % (values_url, query_parameters)

        r = self.client.request('get', url)

        try:
            value = r.json()['values'][0][0]
        except KeyError:
            value = ''

        return Cell(row, col, value)

    @cast_to_a1_notation
    def range(self, name):
        label = '%s!%s' % (self.title, name)

        r = self.client.request(
            'get', SPREADSHEET_VALUES_URL % (self.spreadsheet.id, label))

        start, end = name.split(':')
        (row_offset, column_offset) = a1_to_rowcol(start)
        (last_row, last_column) = a1_to_rowcol(end)

        values = r.json().get('values', [])

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
        r = self.client.request(
            'get', SPREADSHEET_VALUES_URL % (self.spreadsheet.id, self.title))

        try:
            return fill_gaps(r.json()['values'])
        except KeyError:
            return []

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

    def row_values(self, row, value_render_option='FORMATTED_VALUE'):
        query_parameters = 'valueRenderOption=%s' % value_render_option

        label = '%s!A%s:%s' % (self.title, row, row)

        values_url = SPREADSHEET_VALUES_URL % (
            self.spreadsheet.id,
            label
        )

        url = '%s?%s' % (values_url, query_parameters)

        r = self.client.request('get', url)

        try:
            return r.json()['values'][0]
        except KeyError:
            return []

    def col_values(self, col, value_render_option='FORMATTED_VALUE'):
        query_parameters = (
            'valueRenderOption=%s&majorDimension=COLUMNS' % value_render_option
        )

        start_label = rowcol_to_a1(1, col)
        label = '%s!%s:%s' % (self.title, start_label, start_label[:-1])

        values_url = SPREADSHEET_VALUES_URL % (
            self.spreadsheet.id,
            label
        )

        url = '%s?%s' % (values_url, query_parameters)

        r = self.client.request('get', url)

        return r.json()['values'][0]

    def update_acell(self, label, value):
        """Sets the new value to a cell.

        :param label: String with cell label in common format, e.g. 'B1'.
                      Letter case is ignored.
        :param value: New value.

        Example:

            worksheet.update_acell('A1', '42') # this could be 'a1' as well

        """
        return self.update_cell(*(a1_to_rowcol(label)), value=value)

    def update_cell(self, row, col, value):
        """Sets the new value to a cell.

        :param row: Row number.
        :param col: Column number.
        :param value: New value.

        Example::

            worksheet.update_cell(1, 1, '42')

        """
        query_parameters = 'valueInputOption=USER_ENTERED'

        label = '%s!%s' % (self.title, rowcol_to_a1(row, col))

        values_url = SPREADSHEET_VALUES_URL % (
            self.spreadsheet.id,
            label
        )

        url = '%s?%s' % (values_url, query_parameters)

        payload = {"values": [[value]]}

        r = self.client.request('put', url, json=payload)

        return r.json()

    def update_cells(self, cell_list, value_input_option='RAW'):
        query_parameters = 'valueInputOption=%s' % value_input_option

        values_rect = cell_list_to_rect(cell_list)

        payload = {
            'values': values_rect
        }

        start = rowcol_to_a1(cell_list[0].row, cell_list[0].col)
        end = rowcol_to_a1(cell_list[-1].row, cell_list[-1].col)

        label = '%s!%s:%s' % (self.title, start, end)

        values_url = SPREADSHEET_VALUES_URL % (
            self.spreadsheet.id,
            label
        )

        url = '%s?%s' % (values_url, query_parameters)

        r = self.client.request(
            'put',
            url,
            json=payload
        )

        return r.json()

    def resize(self, rows=None, cols=None):
        """Resizes the worksheet.

        :param rows: New rows number.
        :param cols: New columns number.
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

        payload = {
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

        r = self.client.request(
            'post',
            SPREADSHEET_BATCH_UPDATE_URL % self.spreadsheet.id,
            json=payload
        )

        return r.json()

    def update_title(self, title):
        payload = {
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

        r = self.client.request(
            'post',
            SPREADSHEET_BATCH_UPDATE_URL % self.spreadsheet.id,
            json=payload
        )

        return r.json()

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

    def append_row(self, values, value_input_option='RAW'):
        """Adds a row to the worksheet and populates it with values.
        Widens the worksheet if there are more values than columns.

        :param values: List of values for the new row.
        """
        query_parameters = 'valueInputOption=%s' % value_input_option

        payload = {
            'values': [values]
        }

        append_url = SPREADSHEET_APPEND_URL % (
            self.spreadsheet.id,
            self.title
        )

        url = '%s?%s' % (append_url, query_parameters)

        r = self.client.request(
            'post',
            url,
            json=payload
        )

        return r.json()

    def insert_row(
        self,
        values,
        index=1,
        value_input_option='RAW',
        inheritFromBefore=False
    ):
        payload = {
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

        r = self.client.request(
            'post',
            SPREADSHEET_BATCH_UPDATE_URL % self.spreadsheet.id,
            json=payload
        )

        query_parameters = 'valueInputOption=%s' % value_input_option
        label = '%s!%s' % (self.title, 'A%s' % index)

        values_url = SPREADSHEET_VALUES_URL % (
            self.spreadsheet.id,
            label
        )

        url = '%s?%s' % (values_url, query_parameters)

        payload = {'values': [values]}

        r = self.client.request('put', url, json=payload)

        return r.json()

    def delete_row(self, index):
        """"Deletes a row from the worksheet at the specified index

        :param index: Index of a row for deletion
        """
        payload = {
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

        r = self.client.request(
            'post',
            SPREADSHEET_BATCH_UPDATE_URL % self.spreadsheet.id,
            json=payload
        )

        return r.json()

    def clear(self):
        """Clears all cells in the worksheet.
        """
        url = SPREADSHEET_CLEAR_URL % (
            self.spreadsheet.id,
            self.title
        )

        r = self.client.request(
            'post',
            url
        )

        return r.json()

    def _finder(self, func, query):
        r = self.client.request(
            'get', SPREADSHEET_VALUES_URL % (self.spreadsheet.id, self.title))

        values = fill_gaps(r.json().get('values', []))

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

    def export(self, format):
        import warnings
        warnings.warn(
            "Worksheet.export() is deprecated, "
            "this feature is not supported in Sheets API v4",
            DeprecationWarning
        )


class Cell(BaseCell):
    def __init__(self, row, col, value=''):
        self._row = row
        self._col = col

        self.value = value

    @property
    def numeric_value(self):
        try:
            return float(self.value)
        except ValueError:
            return None
