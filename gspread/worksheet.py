"""
gspread.worksheet
~~~~~~~~~~~~~~~~~

This module contains common worksheets' models.

"""

import warnings

from .cell import Cell
from .exceptions import GSpreadException
from .urls import SPREADSHEET_URL, WORKSHEET_DRIVE_URL
from .utils import (
    DEPRECATION_WARNING_TEMPLATE,
    Dimension,
    PasteOrientation,
    PasteType,
    ValueInputOption,
    ValueRenderOption,
    a1_range_to_grid_range,
    a1_to_rowcol,
    absolute_range_name,
    accepted_kwargs,
    cast_to_a1_notation,
    cell_list_to_rect,
    combined_merge_values,
    fill_gaps,
    filter_dict_values,
    finditem,
    is_scalar,
    numericise_all,
    rowcol_to_a1,
)


class ValueRange(list):
    """The class holds the returned values.

    This class inherit the :const:`list` object type.
    It behaves exactly like a list.

    The values are stored in a matrix.

    The property :meth:`gspread.worksheet.ValueRange.major_dimension`
    holds the major dimension of the first list level.

    The inner lists will contain the actual values.

    Examples::

        >>> worksheet.get("A1:B2")
        [
            [
                "A1 value",
                "B1 values",
            ],
            [
                "A2 value",
                "B2 value",
            ]
        ]

        >>> worksheet.get("A1:B2").major_dimension
        ROW

    .. note::

       This class should never be instantiated manually.
       It will be instantiated using the response from the sheet API.
    """

    @classmethod
    def from_json(cls, json):
        values = json.get("values", [])
        new_obj = cls(values)
        new_obj._json = {
            "range": json["range"],
            "majorDimension": json["majorDimension"],
        }

        return new_obj

    @property
    def range(self):
        """The range of the values"""
        return self._json["range"]

    @property
    def major_dimension(self):
        """The major dimension of this range

        Can be one of:

        * ``ROW``: the first list level holds rows of values
        * ``COLUMNS``: the first list level holds columns of values
        """
        return self._json["majorDimension"]

    def first(self, default=None):
        """Returns the value of a first cell in a range.

        If the range is empty, return the default value.
        """
        try:
            return self[0][0]
        except IndexError:
            return default


class Worksheet:
    """The class that represents a single sheet in a spreadsheet
    (aka "worksheet").
    """

    def __init__(self, spreadsheet, properties):
        self.spreadsheet = spreadsheet
        self.client = spreadsheet.client
        self._properties = properties

    def __repr__(self):
        return "<{} {} id:{}>".format(
            self.__class__.__name__,
            repr(self.title),
            self.id,
        )

    @property
    def id(self):
        """Worksheet ID."""
        return self._properties["sheetId"]

    @property
    def title(self):
        """Worksheet title."""
        return self._properties["title"]

    @property
    def url(self):
        """Worksheet URL."""
        return WORKSHEET_DRIVE_URL % (self.spreadsheet.id, self.id)

    @property
    def index(self):
        """Worksheet index."""
        return self._properties["index"]

    @property
    def isSheetHidden(self):
        """Worksheet hidden status."""
        # if the property is not set then hidden=False
        return self._properties.get("hidden", False)

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
            stacklevel=2,
        )

    @property
    def row_count(self):
        """Number of rows."""
        return self._properties["gridProperties"]["rowCount"]

    @property
    def col_count(self):
        """Number of columns.

        .. warning::

           This value is fetched when opening the worksheet.
           This is not dynamically updated when adding columns, yet.
        """
        return self._properties["gridProperties"]["columnCount"]

    @property
    def frozen_row_count(self):
        """Number of frozen rows."""
        return self._properties["gridProperties"].get("frozenRowCount", 0)

    @property
    def frozen_col_count(self):
        """Number of frozen columns."""
        return self._properties["gridProperties"].get("frozenColumnCount", 0)

    @property
    def is_gridlines_hidden(self):
        """Whether or not gridlines hidden. Boolean.
        True if hidden. False if shown.
        """
        return self._properties["gridProperties"].get("hideGridlines", False)

    @property
    def tab_color(self):
        """Tab color style. Dict with RGB color values.
        If any of R, G, B are 0, they will not be present in the dict.
        """
        return self._properties.get("tabColorStyle", {}).get("rgbColor", None)

    def _get_sheet_property(self, property, default_value):
        """return a property of this worksheet or default value if not found"""
        meta = self.spreadsheet.fetch_sheet_metadata()
        sheet = finditem(
            lambda x: x["properties"]["sheetId"] == self.id, meta["sheets"]
        )

        return sheet.get(property, default_value)

    def acell(self, label, value_render_option=ValueRenderOption.formatted):
        """Returns an instance of a :class:`gspread.cell.Cell`.

        :param label: Cell label in A1 notation
                      Letter case is ignored.
        :type label: str
        :param value_render_option: (optional) Determines how values should be
                                    rendered in the output. See
                                    `ValueRenderOption`_ in the Sheets API.
        :type value_render_option: :namedtuple:`~gspread.utils.ValueRenderOption`

        .. _ValueRenderOption: https://developers.google.com/sheets/api/reference/rest/v4/ValueRenderOption

        Example:

        >>> worksheet.acell('A1')
        <Cell R1C1 "I'm cell A1">
        """
        return self.cell(
            *(a1_to_rowcol(label)), value_render_option=value_render_option
        )

    def cell(self, row, col, value_render_option=ValueRenderOption.formatted):
        """Returns an instance of a :class:`gspread.cell.Cell` located at
        `row` and `col` column.

        :param row: Row number.
        :type row: int
        :param col: Column number.
        :type col: int
        :param value_render_option: (optional) Determines how values should be
                                    rendered in the output. See
                                    `ValueRenderOption`_ in the Sheets API.
        :type value_render_option: :namedtuple:`~gspread.utils.ValueRenderOption`

        .. _ValueRenderOption: https://developers.google.com/sheets/api/reference/rest/v4/ValueRenderOption

        Example:

        >>> worksheet.cell(1, 1)
        <Cell R1C1 "I'm cell A1">

        :rtype: :class:`gspread.cell.Cell`
        """
        try:
            data = self.get(
                rowcol_to_a1(row, col), value_render_option=value_render_option
            )

            value = data.first()
        except KeyError:
            value = ""

        return Cell(row, col, value)

    @cast_to_a1_notation
    def range(self, name=""):
        """Returns a list of :class:`gspread.cell.Cell` objects from a specified range.

        :param name: A string with range value in A1 notation (e.g. 'A1:A5')
                     or the named range to fetch.
        :type name: str

        Alternatively, you may specify numeric boundaries. All values
        index from 1 (one):

        :param int first_row: First row number
        :param int first_col: First column number
        :param int last_row: Last row number
        :param int last_col: Last column number

        :rtype: list

        Example::

            >>> # Using A1 notation
            >>> worksheet.range('A1:B7')
            [<Cell R1C1 "42">, ...]

            >>> # Same with numeric boundaries
            >>> worksheet.range(1, 1, 7, 2)
            [<Cell R1C1 "42">, ...]

            >>> # Named ranges work as well
            >>> worksheet.range('NamedRange')
            [<Cell R1C1 "42">, ...]

            >>> # All values in a single API call
            >>> worksheet.range()
            [<Cell R1C1 'Hi mom'>, ...]

        """
        range_label = absolute_range_name(self.title, name)

        data = self.spreadsheet.values_get(range_label)

        if ":" not in name:
            name = data.get("range", "")
            if "!" in name:
                name = name.split("!")[1]

        grid_range = a1_range_to_grid_range(name)

        values = data.get("values", [])

        row_offset = grid_range.get("startRowIndex", 0)
        column_offset = grid_range.get("startColumnIndex", 0)
        last_row = grid_range.get("endRowIndex", self.row_count)
        last_column = grid_range.get("endColumnIndex", self.col_count)

        if last_row is not None:
            last_row -= row_offset

        if last_column is not None:
            last_column -= column_offset

        rect_values = fill_gaps(
            values,
            rows=last_row,
            cols=last_column,
        )

        return [
            Cell(row=i + row_offset + 1, col=j + column_offset + 1, value=value)
            for i, row in enumerate(rect_values)
            for j, value in enumerate(row)
        ]

    @accepted_kwargs(
        major_dimension=None,
        combine_merged_cells=False,
        value_render_option=None,
        date_time_render_option=None,
    )
    def get_values(self, range_name=None, combine_merged_cells=False, **kwargs):
        """Returns a list of lists containing all values from specified range.

        By default values are returned as strings. See ``value_render_option``
        to change the default format.

        :param str range_name: (optional) Cell range in the A1 notation or
            a named range. If not specified the method returns values from all
            non empty cells.

        :param str major_dimension: (optional) The major dimension of the
            values. `Dimension.rows` ("ROWS") or `Dimension.cols` ("COLUMNS").
            Defaults to Dimension.rows
        :type major_dimension: :namedtuple:`~gspread.utils.Dimension`

        :param bool combine_merged_cells: (optional) If True, then all cells that
            are part of a merged cell will have the same value as the top-left
            cell of the merged cell. Defaults to False.

            .. warning::

                Setting this to True will cause an additional API request to be
                made to retrieve the values of all merged cells.


        :param str value_render_option: (optional) Determines how values should
            be rendered in the output. See `ValueRenderOption`_ in
            the Sheets API.

            Possible values are:

            ``ValueRenderOption.formatted``
                (default) Values will be calculated and formatted according
                to the cell's formatting. Formatting is based on the
                spreadsheet's locale, not the requesting user's locale.

            ``ValueRenderOption.unformatted``
                Values will be calculated, but not formatted in the reply.
                For example, if A1 is 1.23 and A2 is =A1 and formatted as
                currency, then A2 would return the number 1.23.

            ``ValueRenderOption.formula``
                Values will not be calculated. The reply will include
                the formulas. For example, if A1 is 1.23 and A2 is =A1 and
                formatted as currency, then A2 would return "=A1".

            .. _ValueRenderOption: https://developers.google.com/sheets/api/reference/rest/v4/ValueRenderOption
        :type value_render_option: :namedtuple:`~gspread.utils.ValueRenderOption`


        :param str date_time_render_option: (optional) How dates, times, and
            durations should be represented in the output.

            Possible values are:

            ``DateTimeOption.serial_number``
                (default) Instructs date, time, datetime, and duration fields
                to be output as doubles in "serial number" format,
                as popularized by Lotus 1-2-3.

            ``DateTimeOption.formatted_string``
                Instructs date, time, datetime, and duration fields to be output
                as strings in their given number format
                (which depends on the spreadsheet locale).

            .. note::

                This is ignored if ``value_render_option`` is ``ValueRenderOption.formatted``.

            The default ``date_time_render_option`` is ``DateTimeOption.serial_number``.
        :type date_time_render_option: :namedtuple:`~gspread.utils.DateTimeOption`

        .. note::

            Empty trailing rows and columns will not be included.

        Examples::

            # Return all values from the sheet
            worksheet.get_values()

            # Return all values from columns "A" and "B"
            worksheet.get_values('A:B')

            # Return values from range "A2:C10"
            worksheet.get_values('A2:C10')

            # Return values from named range "my_range"
            worksheet.get_values('my_range')

            # Return unformatted values (e.g. numbers as numbers)
            worksheet.get_values('A2:B4', value_render_option=ValueRenderOption.unformatted)

            # Return cell values without calculating formulas
            worksheet.get_values('A2:B4', value_render_option=ValueRenderOption.formula)
        """
        try:
            vals = fill_gaps(self.get(range_name, **kwargs))
            if combine_merged_cells is True:
                spreadsheet_meta = self.spreadsheet.fetch_sheet_metadata()
                worksheet_meta = finditem(
                    lambda x: x["properties"]["title"] == self.title,
                    spreadsheet_meta["sheets"],
                )
                return combined_merge_values(worksheet_meta, vals)
            return vals
        except KeyError:
            return []

    @accepted_kwargs(
        major_dimension=None,
        value_render_option=None,
        date_time_render_option=None,
    )
    def get_all_values(self, **kwargs):
        """Returns a list of lists containing all cells' values as strings.

        This is an alias to :meth:`~gspread.worksheet.Worksheet.get_values`

        .. note::

            This is a legacy method.
            Use :meth:`~gspread.worksheet.Worksheet.get_values` instead.

        Examples::

            # Return all values from the sheet
            worksheet.get_all_values()

            # Is equivalent to
            worksheet.get_values()
        """
        return self.get_values(**kwargs)

    def get_all_records(
        self,
        empty2zero=False,
        head=1,
        default_blank="",
        allow_underscores_in_numeric_literals=False,
        numericise_ignore=[],
        value_render_option=None,
        expected_headers=None,
    ):
        """Returns a list of dictionaries, all of them having the contents of
        the spreadsheet with the head row as keys and each of these
        dictionaries holding the contents of subsequent rows of cells as
        values.

        Cell values are numericised (strings that can be read as ints or floats
        are converted), unless specified in numericise_ignore

        :param bool empty2zero: (optional) Determines whether empty cells are
            converted to zeros.
        :param int head: (optional) Determines which row to use as keys,
            starting from 1 following the numeration of the spreadsheet.
        :param str default_blank: (optional) Determines which value to use for
            blank cells, defaults to empty string.
        :param bool allow_underscores_in_numeric_literals: (optional) Allow
            underscores in numeric literals, as introduced in PEP 515
        :param list numericise_ignore: (optional) List of ints of indices of
            the columns (starting at 1) to ignore numericising, special use
            of ['all'] to ignore numericising on all columns.
        :param value_render_option: (optional) Determines how values should
            be rendered in the output. See `ValueRenderOption`_ in
            the Sheets API.
        :type value_render_option: :namedtuple:`~gspread.utils.ValueRenderOption`

        :param list expected_headers: (optional) List of expected headers, they must be unique.

            .. note::

                returned dictionaries will contain all headers even if not included in this list

        """
        idx = head - 1

        data = self.get_all_values(value_render_option=value_render_option)

        # Return an empty list if the sheet doesn't have enough rows
        if len(data) <= idx:
            return []

        keys = data[idx]

        # if no given expected headers, expect all of them
        if expected_headers is None:
            expected_headers = keys

        # keys must:
        # - be uniques
        # - be part of the complete header list
        # - not contain extra headers
        expected = set(expected_headers)
        headers = set(keys)

        # make sure they are uniques
        if len(expected) != len(expected_headers):
            raise GSpreadException("the given 'expected_headers' are not uniques")

        if not expected & headers == expected:
            raise GSpreadException(
                "the given 'expected_headers' contains unknown headers: {}".format(
                    expected - headers
                )
            )

        if numericise_ignore == ["all"]:
            values = data[idx + 1 :]
        else:
            values = [
                numericise_all(
                    row,
                    empty2zero,
                    default_blank,
                    allow_underscores_in_numeric_literals,
                    numericise_ignore,
                )
                for row in data[idx + 1 :]
            ]

        return [dict(zip(keys, row)) for row in values]

    def get_all_cells(self):
        """Returns a list of all `Cell` of the current sheet."""

        return self.range()

    @accepted_kwargs(
        major_dimension=None,
        value_render_option=None,
        date_time_render_option=None,
    )
    def row_values(self, row, **kwargs):
        """Returns a list of all values in a `row`.

        Empty cells in this list will be rendered as :const:`None`.

        :param int row: Row number (one-based).
        :param value_render_option: (optional) Determines how values should
            be rendered in the output. See `ValueRenderOption`_ in
            the Sheets API.

            Possible values are:

            ``ValueRenderOption.formatted``
                (default) Values will be calculated and formatted according
                to the cell's formatting. Formatting is based on the
                spreadsheet's locale, not the requesting user's locale.

            ``ValueRenderOption.unformatted``
                Values will be calculated, but not formatted in the reply.
                For example, if A1 is 1.23 and A2 is =A1 and formatted as
                currency, then A2 would return the number 1.23.

            ``ValueRenderOption.formula``
                Values will not be calculated. The reply will include
                the formulas. For example, if A1 is 1.23 and A2 is =A1 and
                formatted as currency, then A2 would return "=A1".

            .. _ValueRenderOption: https://developers.google.com/sheets/api/reference/rest/v4/ValueRenderOption

        :type value_render_option: :namedtuple:`~gspread.utils.ValueRenderOption`

        :param date_time_render_option: (optional) How dates, times, and
            durations should be represented in the output.

            Possible values are:

            ``DateTimeOption.serial_number``
                (default) Instructs date, time, datetime, and duration fields
                to be output as doubles in "serial number" format,
                as popularized by Lotus 1-2-3.

            ``DateTimeOption.formatted_string``
                Instructs date, time, datetime, and duration fields to be output
                as strings in their given number format
                (which depends on the spreadsheet locale).

            .. note::

                This is ignored if ``value_render_option`` is ``ValueRenderOption.formatted``.

            The default ``date_time_render_option`` is ``DateTimeOption.serial_number``.
        :type date_time_render_option: :namedtuple:`~gspread.utils.DateTimeOption`
        """
        try:
            data = self.get("A{}:{}".format(row, row), **kwargs)
            return data[0] if data else []
        except KeyError:
            return []

    def col_values(self, col, value_render_option=ValueRenderOption.formatted):
        """Returns a list of all values in column `col`.

        Empty cells in this list will be rendered as :const:`None`.

        :param int col: Column number (one-based).
        :param str value_render_option: (optional) Determines how values should
            be rendered in the output. See `ValueRenderOption`_ in
            the Sheets API.
        :type value_render_option: :namedtuple:`~gspread.utils.ValueRenderOption`

        .. _ValueRenderOption: https://developers.google.com/sheets/api/reference/rest/v4/ValueRenderOption
        """

        start_label = rowcol_to_a1(1, col)
        range_label = "{}:{}".format(start_label, start_label[:-1])

        range_name = absolute_range_name(self.title, range_label)

        data = self.spreadsheet.values_get(
            range_name,
            params={
                "valueRenderOption": value_render_option,
                "majorDimension": Dimension.cols,
            },
        )

        try:
            return data["values"][0]
        except KeyError:
            return []

    def update_acell(self, label, value):
        """Updates the value of a cell.

        :param str label: Cell label in A1 notation.
        :param value: New value.

        Example::

            worksheet.update_acell('A1', '42')
        """
        return self.update_cell(*(a1_to_rowcol(label)), value=value)

    def update_cell(self, row, col, value):
        """Updates the value of a cell.

        :param int row: Row number.
        :param int col: Column number.
        :param value: New value.

        Example::

            worksheet.update_cell(1, 1, '42')
        """
        range_name = absolute_range_name(self.title, rowcol_to_a1(row, col))

        data = self.spreadsheet.values_update(
            range_name,
            params={"valueInputOption": ValueInputOption.user_entered},
            body={"values": [[value]]},
        )

        return data

    def update_cells(self, cell_list, value_input_option=ValueInputOption.raw):
        """Updates many cells at once.

        :param list cell_list: List of :class:`gspread.cell.Cell` objects to update.
        :param  value_input_option: (optional) How the input data should be
            interpreted. Possible values are:

            ``ValueInputOption.raw``
                The values the user has entered will not be parsed and will be
                stored as-is.

            ``ValueInputOption.user_entered``
                The values will be parsed as if the user typed them into the
                UI. Numbers will stay as numbers, but strings may be converted
                to numbers, dates, etc. following the same rules that are
                applied when entering text into a cell via
                the Google Sheets UI.

            See `ValueInputOption`_ in the Sheets API.

        :type value_input_option: :namedtuple:`~gspread.utils.ValueInputOption`

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

        start = rowcol_to_a1(
            min(c.row for c in cell_list), min(c.col for c in cell_list)
        )
        end = rowcol_to_a1(max(c.row for c in cell_list), max(c.col for c in cell_list))

        range_name = absolute_range_name(self.title, "{}:{}".format(start, end))

        data = self.spreadsheet.values_update(
            range_name,
            params={"valueInputOption": value_input_option},
            body={"values": values_rect},
        )

        return data

    @accepted_kwargs(
        major_dimension=None,
        value_render_option=None,
        date_time_render_option=None,
    )
    def get(self, range_name=None, **kwargs):
        """Reads values of a single range or a cell of a sheet.

         :param str range_name: (optional) Cell range in the A1 notation or
             a named range.

         :param str major_dimension: (optional) The major dimension that results
             should use. Either ``ROWS`` or ``COLUMNS``.

         :param value_render_option: (optional) Determines how values should
             be rendered in the output. See `ValueRenderOption`_ in
             the Sheets API.

             Possible values are:

             ``ValueRenderOption.formatted``
                 (default) Values will be calculated and formatted according
                 to the cell's formatting. Formatting is based on the
                 spreadsheet's locale, not the requesting user's locale.

             ``ValueRenderOption.unformatted``
                 Values will be calculated, but not formatted in the reply.
                 For example, if A1 is 1.23 and A2 is =A1 and formatted as
                 currency, then A2 would return the number 1.23.

             ``ValueRenderOption.formula``
                 Values will not be calculated. The reply will include
                 the formulas. For example, if A1 is 1.23 and A2 is =A1 and
                 formatted as currency, then A2 would return "=A1".

             .. _ValueRenderOption: https://developers.google.com/sheets/api/reference/rest/v4/ValueRenderOption

        :type value_render_option: :namedtuple:`~gspread.utils.ValueRenderOption`

        :param str date_time_render_option: (optional) How dates, times, and
             durations should be represented in the output.

             Possible values are:

             ``DateTimeOption.serial_number``
                 (default) Instructs date, time, datetime, and duration fields
                 to be output as doubles in "serial number" format,
                 as popularized by Lotus 1-2-3.

             ``DateTimeOption.formatted_string``
                 Instructs date, time, datetime, and duration fields to be output
                 as strings in their given number format
                 (which depends on the spreadsheet locale).

            .. note::

                This is ignored if ``value_render_option`` is ``ValueRenderOption.formatted``.

             The default ``date_time_render_option`` is ``DateTimeOption.serial_number``.
        :type date_time_render_option: :namedtuple:`~gspread.utils.DateTimeOption`

         :rtype: :class:`gspread.worksheet.ValueRange`

         Examples::

             # Return all values from the sheet
             worksheet.get()

             # Return value of 'A1' cell
             worksheet.get('A1')

             # Return values of 'A1:B2' range
             worksheet.get('A1:B2')

             # Return values of 'my_range' named range
             worksheet.get('my_range')

         .. versionadded:: 3.3
        """
        range_name = absolute_range_name(self.title, range_name)

        params = filter_dict_values(
            {
                "majorDimension": kwargs["major_dimension"],
                "valueRenderOption": kwargs["value_render_option"],
                "dateTimeRenderOption": kwargs["date_time_render_option"],
            }
        )

        response = self.spreadsheet.values_get(range_name, params=params)

        return ValueRange.from_json(response)

    @accepted_kwargs(
        major_dimension=None,
        value_render_option=None,
        date_time_render_option=None,
    )
    def batch_get(self, ranges, **kwargs):
        """Returns one or more ranges of values from the sheet.

        :param list ranges: List of cell ranges in the A1 notation or named
            ranges.

        :param str major_dimension: (optional) The major dimension that results
            should use. Either ``ROWS`` or ``COLUMNS``.

        :param value_render_option: (optional) Determines how values should
            be rendered in the output. See `ValueRenderOption`_ in
            the Sheets API.

            Possible values are:

            ``ValueRenderOption.formatted``
                (default) Values will be calculated and formatted according
                to the cell's formatting. Formatting is based on the
                spreadsheet's locale, not the requesting user's locale.

            ``ValueRenderOption.unformatted``
                Values will be calculated, but not formatted in the reply.
                For example, if A1 is 1.23 and A2 is =A1 and formatted as
                currency, then A2 would return the number 1.23.

            ``ValueRenderOption.formula``
                Values will not be calculated. The reply will include
                the formulas. For example, if A1 is 1.23 and A2 is =A1 and
                formatted as currency, then A2 would return "=A1".

            .. _ValueRenderOption: https://developers.google.com/sheets/api/reference/rest/v4/ValueRenderOption

        :type value_render_option: :namedtuple:`~gspread.utils.ValueRenderOption`

        :param str date_time_render_option: (optional) How dates, times, and
            durations should be represented in the output.

            Possible values are:

            ``DateTimeOption.serial_number``
                (default) Instructs date, time, datetime, and duration fields
                to be output as doubles in "serial number" format,
                as popularized by Lotus 1-2-3.

            ``DateTimeOption.formatted_string``
                Instructs date, time, datetime, and duration fields to be output
                as strings in their given number format
                (which depends on the spreadsheet locale).

            .. note::

                This is ignored if ``value_render_option`` is ``ValueRenderOption.formatted``.

            The default ``date_time_render_option`` is ``DateTimeOption.serial_number``.
        :type date_time_render_option: :namedtuple:`~gspread.utils.DateTimeOption`

        .. versionadded:: 3.3

        Examples::

            # Read values from 'A1:B2' range and 'F12' cell
            worksheet.batch_get(['A1:B2', 'F12'])
        """
        ranges = [absolute_range_name(self.title, r) for r in ranges if r]

        params = filter_dict_values(
            {
                "majorDimension": kwargs["major_dimension"],
                "valueRenderOption": kwargs["value_render_option"],
                "dateTimeRenderOption": kwargs["date_time_render_option"],
            }
        )

        response = self.spreadsheet.values_batch_get(ranges=ranges, params=params)

        return [ValueRange.from_json(x) for x in response["valueRanges"]]

    @accepted_kwargs(
        raw=True,
        major_dimension=None,
        value_input_option=None,
        include_values_in_response=None,
        response_value_render_option=None,
        response_date_time_render_option=None,
    )
    def update(self, range_name, values=None, **kwargs):
        """Sets values in a cell range of the sheet.

        :param str range_name: The A1 notation of the values
            to update.
        :param list values: The data to be written.

        :param bool raw: The values will not be parsed by Sheets API and will
            be stored as-is. For example, formulas will be rendered as plain
            strings. Defaults to ``True``. This is a shortcut for
            the ``value_input_option`` parameter.

        :param str major_dimension: (optional) The major dimension of the
            values. Either ``ROWS`` or ``COLUMNS``.

        :param str value_input_option: (optional) How the input data should be
            interpreted. Possible values are:

            ``ValueInputOption.raw``
                The values the user has entered will not be parsed and will be
                stored as-is.

            ``ValueInputOption.user_entered``
                The values will be parsed as if the user typed them into the
                UI. Numbers will stay as numbers, but strings may be converted
                to numbers, dates, etc. following the same rules that are
                applied when entering text into a cell via
                the Google Sheets UI.

        :type value_input_option: :namedtuple:`~gspread.utils.ValueInputOption`

        :param response_value_render_option: (optional) Determines how values should
            be rendered in the output. See `ValueRenderOption`_ in
            the Sheets API.

            Possible values are:

            ``ValueRenderOption.formatted``
                (default) Values will be calculated and formatted according
                to the cell's formatting. Formatting is based on the
                spreadsheet's locale, not the requesting user's locale.

            ``ValueRenderOption.unformatted``
                Values will be calculated, but not formatted in the reply.
                For example, if A1 is 1.23 and A2 is =A1 and formatted as
                currency, then A2 would return the number 1.23.

            ``ValueRenderOption.formula``
                Values will not be calculated. The reply will include
                the formulas. For example, if A1 is 1.23 and A2 is =A1 and
                formatted as currency, then A2 would return "=A1".

            .. _ValueRenderOption: https://developers.google.com/sheets/api/reference/rest/v4/ValueRenderOption

        :type response_value_render_option: :namedtuple:`~gspread.utils.ValueRenderOption`

        :param str response_date_time_render_option: (optional) How dates, times, and
            durations should be represented in the output.

            Possible values are:

            ``DateTimeOption.serial_number``
                (default) Instructs date, time, datetime, and duration fields
                to be output as doubles in "serial number" format,
                as popularized by Lotus 1-2-3.

            ``DateTimeOption.formatted_string``
                Instructs date, time, datetime, and duration fields to be output
                as strings in their given number format
                (which depends on the spreadsheet locale).

            .. note::

                This is ignored if ``value_render_option`` is ``ValueRenderOption.formatted``.

            The default ``date_time_render_option`` is ``DateTimeOption.serial_number``.
        :type date_time_render_option: :namedtuple:`~gspread.utils.DateTimeOption`

        Examples::

            # Sets 'Hello world' in 'A2' cell
            worksheet.update('A2', 'Hello world')

            # Updates cells A1, B1, C1 with values 42, 43, 44 respectively
            worksheet.update([42, 43, 44])

            # Updates A2 and A3 with values 42 and 43
            # Note that update range can be bigger than values array
            worksheet.update('A2:B4', [[42], [43]])

            # Add a formula
            worksheet.update('A5', '=SUM(A1:A4)', raw=False)

            # Update 'my_range' named range with values 42 and 43
            worksheet.update('my_range', [[42], [43]])

            # Note: named ranges are defined in the scope of
            # a spreadsheet, so even if `my_range` does not belong to
            # this sheet it is still updated

        .. versionadded:: 3.3
        """
        warnings.warn(
            DEPRECATION_WARNING_TEMPLATE.format(
                v_deprecated="6.0.0",
                msg_deprecated="method signature will change to: 'Worksheet.update(value = [[]], range_name=)'"
                " arguments 'range_name' and 'values' will swap, values will be mandatory of type: 'list(list(...))'",
            )
        )
        if is_scalar(range_name):
            range_name = absolute_range_name(self.title, range_name)
        else:
            values = range_name
            range_name = absolute_range_name(self.title)

        if is_scalar(values):
            values = [[values]]

        if not kwargs["value_input_option"]:
            kwargs["value_input_option"] = (
                ValueInputOption.raw if kwargs["raw"] else ValueInputOption.user_entered
            )

        params = filter_dict_values(
            {
                "valueInputOption": kwargs["value_input_option"],
                "includeValuesInResponse": kwargs["include_values_in_response"],
                "responseValueRenderOption": kwargs["response_value_render_option"],
                "responseDateTimeRenderOption": kwargs[
                    "response_date_time_render_option"
                ],
            }
        )

        response = self.spreadsheet.values_update(
            range_name,
            params=params,
            body=filter_dict_values(
                {"values": values, "majorDimension": kwargs["major_dimension"]}
            ),
        )

        return response

    @accepted_kwargs(
        raw=True,
        value_input_option=None,
        include_values_in_response=None,
        response_value_render_option=None,
        response_date_time_render_option=None,
    )
    def batch_update(self, data, **kwargs):
        """Sets values in one or more cell ranges of the sheet at once.

        :param list data: List of dictionaries in the form of
            `{'range': '...', 'values': [[.., ..], ...]}` where `range`
            is a target range to update in A1 notation or a named range,
            and `values` is a list of lists containing new values.

        :param str value_input_option: (optional) How the input data should be
            interpreted. Possible values are:

            * ``ValueInputOption.raw``

              The values the user has entered will not be parsed and will be
              stored as-is.

            * ``ValueInputOption.user_entered``

              The values will be parsed as if the user typed them into the
              UI. Numbers will stay as numbers, but strings may be converted
              to numbers, dates, etc. following the same rules that are
              applied when entering text into a cell via
              the Google Sheets UI.

        :type value_input_option: :namedtuple:`~gspread.utils.ValueInputOption`

        :param response_value_render_option: (optional) Determines how values should
            be rendered in the output. See `ValueRenderOption`_ in
            the Sheets API.

            Possible values are:

            ``ValueRenderOption.formatted``
                (default) Values will be calculated and formatted according
                to the cell's formatting. Formatting is based on the
                spreadsheet's locale, not the requesting user's locale.

            ``ValueRenderOption.unformatted``
                Values will be calculated, but not formatted in the reply.
                For example, if A1 is 1.23 and A2 is =A1 and formatted as
                currency, then A2 would return the number 1.23.

            ``ValueRenderOption.formula``
                Values will not be calculated. The reply will include
                the formulas. For example, if A1 is 1.23 and A2 is =A1 and
                formatted as currency, then A2 would return "=A1".

            .. _ValueRenderOption: https://developers.google.com/sheets/api/reference/rest/v4/ValueRenderOption

        :type response_value_render_option: :namedtuple:`~gspread.utils.ValueRenderOption`

        :param str response_date_time_render_option: (optional) How dates, times, and
            durations should be represented in the output.

            Possible values are:

            ``DateTimeOption.serial_number``
                (default) Instructs date, time, datetime, and duration fields
                to be output as doubles in "serial number" format,
                as popularized by Lotus 1-2-3.

            ``DateTimeOption.formatted_string``
                Instructs date, time, datetime, and duration fields to be output
                as strings in their given number format
                (which depends on the spreadsheet locale).

            .. note::

                This is ignored if ``value_render_option`` is ``ValueRenderOption.formatted``.

            The default ``date_time_render_option`` is ``DateTimeOption.serial_number``.
        :type date_time_render_option: :namedtuple:`~gspread.utils.DateTimeOption`

        Examples::

            worksheet.batch_update([{
                'range': 'A1:B1',
                'values': [['42', '43']],
            }, {
                'range': 'my_range',
                'values': [['44', '45']],
            }])

            # Note: named ranges are defined in the scope of
            # a spreadsheet, so even if `my_range` does not belong to
            # this sheet it is still updated

        .. versionadded:: 3.3
        """
        if not kwargs["value_input_option"]:
            kwargs["value_input_option"] = (
                ValueInputOption.raw if kwargs["raw"] else ValueInputOption.user_entered
            )

        data = [
            dict(vr, range=absolute_range_name(self.title, vr["range"])) for vr in data
        ]

        body = filter_dict_values(
            {
                "valueInputOption": kwargs["value_input_option"],
                "includeValuesInResponse": kwargs["include_values_in_response"],
                "responseValueRenderOption": kwargs["response_value_render_option"],
                "responseDateTimeRenderOption": kwargs[
                    "response_date_time_render_option"
                ],
                "data": data,
            }
        )

        response = self.spreadsheet.values_batch_update(body=body)

        return response

    def batch_format(self, formats):
        """Formats cells in batch.

        :param list formats: List of ranges to format and the new format to apply
            to each range.

            The list is composed of dict objects with the following keys/values:

            * range : A1 range notation
            * format : a valid dict object with the format to apply
              for that range see `CellFormat`_ in the Sheets API for available fields.

        .. _CellFormat: https://developers.google.com/sheets/api/reference/rest/v4/spreadsheets/cells#cellformat

        Examples::

            # Format the range ``A1:C1`` with bold text
            # and format the range ``A2:C2`` a font size of 16

            formats = [
                {
                    "range": "A1:C1",
                    "format": {
                        "textFormat": {
                            "bold": True,
                        },
                    },
                },
                {
                    "range": "A2:C2",
                    "format": {
                        "textFormat": {
                            "fontSize": 16,
                        },
                    },
                },
            ]
            worksheet.batch_format(formats)

        .. versionadded:: 5.4
        """

        body = {
            "requests": [],
        }

        for format in formats:
            range_name = format["range"]
            cell_format = format["format"]

            grid_range = a1_range_to_grid_range(range_name, self.id)

            fields = "userEnteredFormat(%s)" % ",".join(cell_format.keys())

            body["requests"].append(
                {
                    "repeatCell": {
                        "range": grid_range,
                        "cell": {"userEnteredFormat": cell_format},
                        "fields": fields,
                    }
                }
            )

        return self.spreadsheet.batch_update(body)

    def format(self, ranges, format):
        """Format a list of ranges with the given format.

        :param str|list ranges: Target ranges in the A1 notation.
        :param dict format: Dictionary containing the fields to update.
            See `CellFormat`_ in the Sheets API for available fields.

        Examples::

            # Set 'A4' cell's text format to bold
            worksheet.format("A4", {"textFormat": {"bold": True}})

            # Set 'A1:D4' and 'A10:D10' cells's text format to bold
            worksheet.format(["A1:D4", "A10:D10"], {"textFormat": {"bold": True}})

            # Color the background of 'A2:B2' cell range in black,
            # change horizontal alignment, text color and font size
            worksheet.format("A2:B2", {
                "backgroundColor": {
                  "red": 0.0,
                  "green": 0.0,
                  "blue": 0.0
                },
                "horizontalAlignment": "CENTER",
                "textFormat": {
                  "foregroundColor": {
                    "red": 1.0,
                    "green": 1.0,
                    "blue": 1.0
                  },
                  "fontSize": 12,
                  "bold": True
                }
            })

        .. versionadded:: 3.3
        """

        if is_scalar(ranges):
            ranges = [ranges]

        formats = [{"range": range, "format": format} for range in ranges]

        return self.batch_format(formats)

    def resize(self, rows=None, cols=None):
        """Resizes the worksheet. Specify one of ``rows`` or ``cols``.

        :param int rows: (optional) New number of rows.
        :param int cols: (optional) New number columns.
        """
        grid_properties = {}

        if rows is not None:
            grid_properties["rowCount"] = rows

        if cols is not None:
            grid_properties["columnCount"] = cols

        if not grid_properties:
            raise TypeError("Either 'rows' or 'cols' should be specified.")

        fields = ",".join("gridProperties/%s" % p for p in grid_properties.keys())

        body = {
            "requests": [
                {
                    "updateSheetProperties": {
                        "properties": {
                            "sheetId": self.id,
                            "gridProperties": grid_properties,
                        },
                        "fields": fields,
                    }
                }
            ]
        }

        res = self.spreadsheet.batch_update(body)
        if rows is not None:
            self._properties["gridProperties"]["rowCount"] = rows
        if cols is not None:
            self._properties["gridProperties"]["columnCount"] = cols
        return res

    # TODO(post Python 2): replace the method signature with
    # def sort(self, *specs, range=None):
    def sort(self, *specs, **kwargs):
        """Sorts worksheet using given sort orders.

        :param list specs: The sort order per column. Each sort order
            represented by a tuple where the first element is a column index
            and the second element is the order itself: 'asc' or 'des'.
        :param str range: The range to sort in A1 notation. By default sorts
            the whole sheet excluding frozen rows.

        Example::

            # Sort sheet A -> Z by column 'B'
            wks.sort((2, 'asc'))

            # Sort range A2:G8 basing on column 'G' A -> Z
            # and column 'B' Z -> A
            wks.sort((7, 'asc'), (2, 'des'), range='A2:G8')

        Warning::

            This function signature will change, arguments will swap places:  sort(range, specs)

        .. versionadded:: 3.4
        """
        warnings.warn(
            DEPRECATION_WARNING_TEMPLATE.format(
                v_deprecated="6.0.0",
                msg_deprecated="This function signature will change, arguments will swap places:  sort(range, specs)",
            ),
            DeprecationWarning,
        )
        range_name = kwargs.pop("range", None)

        if range_name:
            start_a1, end_a1 = range_name.split(":")
            start_row, start_col = a1_to_rowcol(start_a1)
            end_row, end_col = a1_to_rowcol(end_a1)
        else:
            start_row = self._properties["gridProperties"].get("frozenRowCount", 0) + 1
            start_col = 1
            end_row = self.row_count
            end_col = self.col_count

        request_range = {
            "sheetId": self.id,
            "startRowIndex": start_row - 1,
            "endRowIndex": end_row,
            "startColumnIndex": start_col - 1,
            "endColumnIndex": end_col,
        }

        request_sort_specs = list()
        for col, order in specs:
            if order == "asc":
                request_order = "ASCENDING"
            elif order == "des":
                request_order = "DESCENDING"
            else:
                raise ValueError(
                    "Either 'asc' or 'des' should be specified as sort order."
                )
            request_sort_spec = {
                "dimensionIndex": col - 1,
                "sortOrder": request_order,
            }
            request_sort_specs.append(request_sort_spec)

        body = {
            "requests": [
                {
                    "sortRange": {
                        "range": request_range,
                        "sortSpecs": request_sort_specs,
                    }
                }
            ]
        }

        response = self.spreadsheet.batch_update(body)
        return response

    def update_title(self, title):
        """Renames the worksheet.

        :param str title: A new title.
        """
        body = {
            "requests": [
                {
                    "updateSheetProperties": {
                        "properties": {"sheetId": self.id, "title": title},
                        "fields": "title",
                    }
                }
            ]
        }

        response = self.spreadsheet.batch_update(body)
        self._properties["title"] = title
        return response

    def update_tab_color(self, color: dict):
        """Changes the worksheet's tab color.
        Use clear_tab_color() to remove the color.

        :param dict color: The red, green and blue values of the color, between 0 and 1.
        """
        red, green, blue = color["red"], color["green"], color["blue"]
        body = {
            "requests": [
                {
                    "updateSheetProperties": {
                        "properties": {
                            "sheetId": self.id,
                            "tabColorStyle": {
                                "rgbColor": {
                                    "red": red,
                                    "green": green,
                                    "blue": blue,
                                }
                            },
                        },
                        "fields": "tabColorStyle",
                    }
                }
            ]
        }

        response = self.spreadsheet.batch_update(body)

        sheet_color = {
            "red": red,
            "green": green,
            "blue": blue,
        }

        self._properties["tabColorStyle"] = {"rgbColor": sheet_color}
        return response

    def clear_tab_color(self):
        """Clears the worksheet's tab color.
        Use update_tab_color() to set the color.
        """
        body = {
            "requests": [
                {
                    "updateSheetProperties": {
                        "properties": {
                            "sheetId": self.id,
                            "tabColorStyle": {
                                "rgbColor": None,
                            },
                        },
                        "fields": "tabColorStyle",
                    },
                },
            ],
        }
        response = self.spreadsheet.batch_update(body)
        self._properties.pop("tabColorStyle")
        return response

    def update_index(self, index):
        """Updates the ``index`` property for the worksheet.

        See the `Sheets API documentation
        <https://developers.google.com/sheets/api/reference/rest/v4/spreadsheets#sheetproperties>`_
        for information on how updating the index property affects the order of worksheets
        in a spreadsheet.

        To reorder all worksheets in a spreadsheet, see `Spreadsheet.reorder_worksheets`.

        .. versionadded:: 3.4
        """
        body = {
            "requests": [
                {
                    "updateSheetProperties": {
                        "properties": {"sheetId": self.id, "index": index},
                        "fields": "index",
                    }
                }
            ]
        }

        res = self.spreadsheet.batch_update(body)
        self._properties["index"] = index
        return res

    def _auto_resize(self, start_index, end_index, dimension):
        """Updates the size of rows or columns in the  worksheet.

        Index start from 0

        :param start_index: The index (inclusive) to begin resizing
        :param end_index: The index (exclusive) to finish resizing
        :param dimension: Specifies whether to resize the row or column


        .. versionadded:: 5.3.3
        """
        body = {
            "requests": [
                {
                    "autoResizeDimensions": {
                        "dimensions": {
                            "sheetId": self.id,
                            "dimension": dimension,
                            "startIndex": int(start_index),
                            "endIndex": int(end_index),
                        }
                    }
                }
            ]
        }

        return self.spreadsheet.batch_update(body)

    def columns_auto_resize(self, start_column_index, end_column_index):
        """Updates the size of rows or columns in the  worksheet.

        Index start from 0

        :param start_column_index: The index (inclusive) to begin resizing
        :param end_column_index: The index (exclusive) to finish resizing


        .. versionadded:: 3.4
        .. versionchanged:: 5.3.3
        """
        return self._auto_resize(start_column_index, end_column_index, Dimension.cols)

    def rows_auto_resize(self, start_row_index, end_row_index):
        """Updates the size of rows or columns in the  worksheet.

        Index start from 0

        :param start_row_index: The index (inclusive) to begin resizing
        :param end_row_index: The index (exclusive) to finish resizing


        .. versionadded:: 5.3.3
        """
        return self._auto_resize(start_row_index, end_row_index, Dimension.rows)

    def add_rows(self, rows):
        """Adds rows to worksheet.

        :param rows: Number of new rows to add.
        :type rows: int

        """
        self.resize(rows=self.row_count + rows)

    def add_cols(self, cols):
        """Adds columns to worksheet.

        :param cols: Number of new columns to add.
        :type cols: int

        """
        self.resize(cols=self.col_count + cols)

    def append_row(
        self,
        values,
        value_input_option=ValueInputOption.raw,
        insert_data_option=None,
        table_range=None,
        include_values_in_response=False,
    ):
        """Adds a row to the worksheet and populates it with values.

        Widens the worksheet if there are more values than columns.

        :param list values: List of values for the new row.
        :param value_input_option: (optional) Determines how the input data
            should be interpreted. See `ValueInputOption`_ in the Sheets API
            reference.
        :type value_input_option: :namedtuple:`~gspread.utils.ValueInputOption`
        :param str insert_data_option: (optional) Determines how the input data
            should be inserted. See `InsertDataOption`_ in the Sheets API
            reference.
        :param str table_range: (optional) The A1 notation of a range to search
            for a logical table of data. Values are appended after the last row
            of the table. Examples: ``A1`` or ``B2:D4``
        :param bool include_values_in_response: (optional) Determines if the
            update response should include the values of the cells that were
            appended. By default, responses do not include the updated values.

        .. _ValueInputOption: https://developers.google.com/sheets/api/reference/rest/v4/ValueInputOption
        .. _InsertDataOption: https://developers.google.com/sheets/api/reference/rest/v4/spreadsheets.values/append#InsertDataOption

        """
        return self.append_rows(
            [values],
            value_input_option=value_input_option,
            insert_data_option=insert_data_option,
            table_range=table_range,
            include_values_in_response=include_values_in_response,
        )

    def append_rows(
        self,
        values,
        value_input_option=ValueInputOption.raw,
        insert_data_option=None,
        table_range=None,
        include_values_in_response=False,
    ):
        """Adds multiple rows to the worksheet and populates them with values.

        Widens the worksheet if there are more values than columns.

        :param list values: List of rows each row is List of values for
            the new row.
        :param str value_input_option: (optional) Determines how input data
            should be interpreted. Possible values are ``ValueInputOption.raw``
            or ``ValueInputOption.user_entered``.
            See `ValueInputOption`_ in the Sheets API.
        :type value_input_option: :namedtuple:`~gspread.utils.ValueInputOption`
        :param str insert_data_option: (optional) Determines how the input data
            should be inserted. See `InsertDataOption`_ in the Sheets API
            reference.
        :param str table_range: (optional) The A1 notation of a range to search
            for a logical table of data. Values are appended after the last row
            of the table. Examples: ``A1`` or ``B2:D4``
        :param bool include_values_in_response: (optional) Determines if the
            update response should include the values of the cells that were
            appended. By default, responses do not include the updated values.

        .. _ValueInputOption: https://developers.google.com/sheets/api/reference/rest/v4/ValueInputOption
        .. _InsertDataOption: https://developers.google.com/sheets/api/reference/rest/v4/spreadsheets.values/append#InsertDataOption
        """
        range_label = absolute_range_name(self.title, table_range)

        params = {
            "valueInputOption": value_input_option,
            "insertDataOption": insert_data_option,
            "includeValuesInResponse": include_values_in_response,
        }

        body = {"values": values}

        res = self.spreadsheet.values_append(range_label, params, body)
        num_new_rows = len(values)
        self._properties["gridProperties"]["rowCount"] += num_new_rows
        return res

    def insert_row(
        self,
        values,
        index=1,
        value_input_option=ValueInputOption.raw,
        inherit_from_before=False,
    ):
        """Adds a row to the worksheet at the specified index and populates it
        with values.

        Widens the worksheet if there are more values than columns.

        :param list values: List of values for the new row.
        :param int index: (optional) Offset for the newly inserted row.
        :param str value_input_option: (optional) Determines how input data
            should be interpreted. Possible values are ``ValueInputOption.raw``
            or ``ValueInputOption.user_entered``.
            See `ValueInputOption`_ in the Sheets API.
        :type value_input_option: :namedtuple:`~gspread.utils.ValueInputOption`
        :param bool inherit_from_before: (optional) If True, the new row will
            inherit its properties from the previous row. Defaults to False,
            meaning that the new row acquires the properties of the row
            immediately after it.

            .. warning::

               `inherit_from_before` must be False when adding a row to the top
               of a spreadsheet (`index=1`), and must be True when adding to
               the bottom of the spreadsheet.

        .. _ValueInputOption: https://developers.google.com/sheets/api/reference/rest/v4/ValueInputOption
        """
        return self.insert_rows(
            [values],
            index,
            value_input_option=value_input_option,
            inherit_from_before=inherit_from_before,
        )

    def insert_rows(
        self,
        values,
        row=1,
        value_input_option=ValueInputOption.raw,
        inherit_from_before=False,
    ):
        """Adds multiple rows to the worksheet at the specified index and
        populates them with values.

        :param list values: List of row lists. a list of lists, with the lists
            each containing one row's values. Widens the worksheet if there are
            more values than columns.
        :param int row: Start row to update (one-based). Defaults to 1 (one).
        :param str value_input_option: (optional) Determines how input data
            should be interpreted. Possible values are ``ValueInputOption.raw``
            or ``ValueInputOption.user_entered``.
            See `ValueInputOption`_ in the Sheets API.
        :type value_input_option: :namedtuple:`~gspread.utils.ValueInputOption`
        :param bool inherit_from_before: (optional) If true, new rows will
            inherit their properties from the previous row. Defaults to False,
            meaning that new rows acquire the properties of the row immediately
            after them.

            .. warning::

               `inherit_from_before` must be False when adding rows to the top
               of a spreadsheet (`row=1`), and must be True when adding to
               the bottom of the spreadsheet.
        """

        # can't insert row on sheet with colon ':'
        # in its name, see issue: https://issuetracker.google.com/issues/36761154
        if ":" in self.title:
            raise GSpreadException(
                "can't insert row in worksheet with colon ':' in its name. See issue: https://issuetracker.google.com/issues/36761154"
            )

        if inherit_from_before and row == 1:
            raise GSpreadException(
                "inherit_from_before cannot be used when inserting row(s) at the top of a spreadsheet"
            )

        body = {
            "requests": [
                {
                    "insertDimension": {
                        "range": {
                            "sheetId": self.id,
                            "dimension": Dimension.rows,
                            "startIndex": row - 1,
                            "endIndex": len(values) + row - 1,
                        },
                        "inheritFromBefore": inherit_from_before,
                    }
                }
            ]
        }

        self.spreadsheet.batch_update(body)

        range_label = absolute_range_name(self.title, "A%s" % row)

        params = {"valueInputOption": value_input_option}

        body = {"majorDimension": Dimension.rows, "values": values}

        res = self.spreadsheet.values_append(range_label, params, body)
        num_new_rows = len(values)
        self._properties["gridProperties"]["rowCount"] += num_new_rows
        return res

    def insert_cols(
        self,
        values,
        col=1,
        value_input_option=ValueInputOption.raw,
        inherit_from_before=False,
    ):
        """Adds multiple new cols to the worksheet at specified index and
        populates them with values.

        :param list values: List of col lists. a list of lists, with the lists
            each containing one col's values. Increases the number of rows
            if there are more values than columns.
        :param int col: Start col to update (one-based). Defaults to 1 (one).
        :param str value_input_option: (optional) Determines how input data
            should be interpreted. Possible values are ``ValueInputOption.raw``
            or ``ValueInputOption.user_entered``.
            See `ValueInputOption`_ in the Sheets API.
        :type value_input_option: :namedtuple:`~gspread.utils.ValueInputOption`
        :param bool inherit_from_before: (optional) If True, new columns will
            inherit their properties from the previous column. Defaults to
            False, meaning that new columns acquire the properties of the
            column immediately after them.

            .. warning::

               `inherit_from_before` must be False if adding at the left edge
               of a spreadsheet (`col=1`), and must be True if adding at the
               right edge of the spreadsheet.
        """

        if inherit_from_before and col == 1:
            raise GSpreadException(
                "inherit_from_before cannot be used when inserting column(s) at the left edge of a spreadsheet"
            )

        body = {
            "requests": [
                {
                    "insertDimension": {
                        "range": {
                            "sheetId": self.id,
                            "dimension": Dimension.cols,
                            "startIndex": col - 1,
                            "endIndex": len(values) + col - 1,
                        },
                        "inheritFromBefore": inherit_from_before,
                    }
                }
            ]
        }

        self.spreadsheet.batch_update(body)

        range_label = absolute_range_name(self.title, rowcol_to_a1(1, col))

        params = {"valueInputOption": value_input_option}

        body = {"majorDimension": Dimension.cols, "values": values}

        res = self.spreadsheet.values_append(range_label, params, body)
        num_new_cols = len(values)
        self._properties["gridProperties"]["columnCount"] += num_new_cols
        return res

    def delete_row(self, index):
        """.. deprecated:: 5.0

        Deletes the row from the worksheet at the specified index.

        :param int index: Index of a row for deletion.
        """
        import warnings

        warnings.warn(
            "Worksheet.delete_row() is deprecated, "
            "Please use `Worksheet.delete_rows()` instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        return self.delete_rows(index)

    @cast_to_a1_notation
    def add_protected_range(
        self,
        name,
        editor_users_emails,
        editor_groups_emails=[],
        description=None,
        warning_only=False,
        requesting_user_can_edit=False,
    ):
        """Add protected range to the sheet. Only the editors can edit
        the protected range.

        Google API will automatically add the owner of this SpreadSheet.
        The list ``editor_users_emails`` must at least contain the e-mail
        address used to open that SpreadSheet.

        ``editor_users_emails`` must only contain e-mail addresses
        who already have a write access to the spreadsheet.

        :param str name: A string with range value in A1 notation,
            e.g. 'A1:A5'.

        Alternatively, you may specify numeric boundaries. All values
        index from 1 (one):

        :param int first_row: First row number
        :param int first_col: First column number
        :param int last_row: Last row number
        :param int last_col: Last column number

        For both A1 and numeric notation:

        :param list editor_users_emails: The email addresses of
            users with edit access to the protected range.
            This must include your e-mail address at least.
        :param list editor_groups_emails: (optional) The email addresses of
            groups with edit access to the protected range.
        :param str description: (optional) Description for the protected
            ranges.
        :param boolean warning_only: (optional) When true this protected range
            will show a warning when editing. Defaults to ``False``.
        :param boolean requesting_user_can_edit: (optional) True if the user
            who requested this protected range can edit the protected cells.
            Defaults to ``False``.
        """

        grid_range = a1_range_to_grid_range(name, self.id)

        body = {
            "requests": [
                {
                    "addProtectedRange": {
                        "protectedRange": {
                            "range": grid_range,
                            "description": description,
                            "warningOnly": warning_only,
                            "requestingUserCanEdit": requesting_user_can_edit,
                            "editors": {
                                "users": editor_users_emails,
                                "groups": editor_groups_emails,
                            },
                        }
                    }
                }
            ]
        }

        return self.spreadsheet.batch_update(body)

    def delete_protected_range(self, id):
        """Delete protected range identified by the ID ``id``.

        To retrieve the ID of a protected range use the following method
        to list them all: :func:`~gspread.Spreadsheet.list_protected_ranges`
        """

        body = {
            "requests": [
                {
                    "deleteProtectedRange": {
                        "protectedRangeId": id,
                    }
                }
            ]
        }

        return self.spreadsheet.batch_update(body)

    def delete_dimension(self, dimension, start_index, end_index=None):
        """Deletes multi rows from the worksheet at the specified index.

        :param dimension: A dimension to delete. ``Dimension.rows`` or ``Dimension.cols``.
        :type dimension: :namedtuple:`~gspread.utils.Dimension`
        :param int start_index: Index of a first row for deletion.
        :param int end_index: Index of a last row for deletion. When
            ``end_index`` is not specified this method only deletes a single
            row at ``start_index``.
        """
        if end_index is None:
            end_index = start_index

        body = {
            "requests": [
                {
                    "deleteDimension": {
                        "range": {
                            "sheetId": self.id,
                            "dimension": dimension,
                            "startIndex": start_index - 1,
                            "endIndex": end_index,
                        }
                    }
                }
            ]
        }

        res = self.spreadsheet.batch_update(body)
        if end_index is None:
            end_index = start_index
        num_deleted = end_index - start_index + 1
        if dimension == Dimension.rows:
            self._properties["gridProperties"]["rowCount"] -= num_deleted
        elif dimension == Dimension.cols:
            self._properties["gridProperties"]["columnCount"] -= num_deleted
        return res

    def delete_rows(self, start_index, end_index=None):
        """Deletes multiple rows from the worksheet at the specified index.

        :param int start_index: Index of a first row for deletion.
        :param int end_index: Index of a last row for deletion.
            When end_index is not specified this method only deletes a single
            row at ``start_index``.

        Example::

            # Delete rows 5 to 10 (inclusive)
            worksheet.delete_rows(5, 10)

            # Delete only the second row
            worksheet.delete_rows(2)

        """
        return self.delete_dimension(Dimension.rows, start_index, end_index)

    def delete_columns(self, start_index, end_index=None):
        """Deletes multiple columns from the worksheet at the specified index.

        :param int start_index: Index of a first column for deletion.
        :param int end_index: Index of a last column for deletion.
            When end_index is not specified this method only deletes a single
            column at ``start_index``.
        """
        return self.delete_dimension(Dimension.cols, start_index, end_index)

    def clear(self):
        """Clears all cells in the worksheet."""
        return self.spreadsheet.values_clear(absolute_range_name(self.title))

    def batch_clear(self, ranges):
        """Clears multiple ranges of cells with 1 API call.

        `Batch Clear`_

        .. _Batch Clear: https://developers.google.com/sheets/api/reference/rest/v4/spreadsheets.values/batchClear

        Examples::

            worksheet.batch_clear(['A1:B1','my_range'])

            # Note: named ranges are defined in the scope of
            # a spreadsheet, so even if `my_range` does not belong to
            # this sheet it is still updated

        .. versionadded:: 3.8.0

        """
        ranges = [absolute_range_name(self.title, rng) for rng in ranges]

        body = {"ranges": ranges}

        response = self.spreadsheet.values_batch_clear(body=body)

        return response

    def _finder(self, func, query, case_sensitive, in_row=None, in_column=None):
        data = self.spreadsheet.values_get(absolute_range_name(self.title))

        try:
            values = fill_gaps(data["values"])
        except KeyError:
            values = []

        cells = self._list_cells(values, in_row, in_column)

        if isinstance(query, str):

            def match(x):
                if case_sensitive:
                    return x.value == query
                else:
                    return x.value.casefold() == query.casefold()

        else:

            def match(x):
                return query.search(x.value)

        return func(match, cells)

    def _list_cells(self, values, in_row=None, in_column=None):
        """Returns a list of ``Cell`` instances scoped by optional
        ``in_row``` or ``in_column`` values (both one-based).
        """
        if in_row and in_column:
            raise TypeError("Either 'in_row' or 'in_column' should be specified.")

        if in_column:
            return [
                Cell(row=i + 1, col=in_column, value=row[in_column - 1])
                for i, row in enumerate(values)
            ]
        elif in_row:
            return [
                Cell(row=in_row, col=j + 1, value=value)
                for j, value in enumerate(values[in_row - 1])
            ]
        else:
            return [
                Cell(row=i + 1, col=j + 1, value=value)
                for i, row in enumerate(values)
                for j, value in enumerate(row)
            ]

    def find(self, query, in_row=None, in_column=None, case_sensitive=True):
        """Finds the first cell matching the query.

        :param query: A literal string to match or compiled regular expression.
        :type query: str, :py:class:`re.RegexObject`
        :param int in_row: (optional) One-based row number to scope the search.
        :param int in_column: (optional) One-based column number to scope
            the search.
        :param bool case_sensitive: (optional) comparison is case sensitive if
            set to True, case insensitive otherwise. Default is True.
            Does not apply to regular expressions.
        :returns: the first matching cell or None otherwise
        :rtype: :class:`gspread.cell.Cell`
        """
        try:
            return self._finder(finditem, query, case_sensitive, in_row, in_column)
        except StopIteration:
            return None

    def findall(self, query, in_row=None, in_column=None, case_sensitive=True):
        """Finds all cells matching the query.

        Returns a list of :class:`gspread.cell.Cell`.

        :param query: A literal string to match or compiled regular expression.
        :type query: str, :py:class:`re.RegexObject`
        :param int in_row: (optional) One-based row number to scope the search.
        :param int in_column: (optional) One-based column number to scope
            the search.
        :param bool case_sensitive: (optional) comparison is case sensitive if
            set to True, case insensitive otherwise. Default is True.
            Does not apply to regular expressions.
        :returns: the list of all matching cells or empty list otherwise
        :rtype: list
        """
        return list(self._finder(filter, query, case_sensitive, in_row, in_column))

    def freeze(self, rows=None, cols=None):
        """Freeze rows and/or columns on the worksheet.

        :param rows: Number of rows to freeze.
        :param cols: Number of columns to freeze.
        """
        grid_properties = {}

        if rows is not None:
            grid_properties["frozenRowCount"] = rows

        if cols is not None:
            grid_properties["frozenColumnCount"] = cols

        if not grid_properties:
            raise TypeError("Either 'rows' or 'cols' should be specified.")

        fields = ",".join("gridProperties/%s" % p for p in grid_properties.keys())

        body = {
            "requests": [
                {
                    "updateSheetProperties": {
                        "properties": {
                            "sheetId": self.id,
                            "gridProperties": grid_properties,
                        },
                        "fields": fields,
                    }
                }
            ]
        }

        res = self.spreadsheet.batch_update(body)
        if rows is not None:
            self._properties["gridProperties"]["frozenRowCount"] = rows
        if cols is not None:
            self._properties["gridProperties"]["frozenColumnCount"] = cols
        return res

    @cast_to_a1_notation
    def set_basic_filter(self, name=None):
        """Add a basic filter to the worksheet. If a range or boundaries
        are passed, the filter will be limited to the given range.

        :param str name: A string with range value in A1 notation,
            e.g. ``A1:A5``.

        Alternatively, you may specify numeric boundaries. All values
        index from 1 (one):

        :param int first_row: First row number
        :param int first_col: First column number
        :param int last_row: Last row number
        :param int last_col: Last column number

        .. versionadded:: 3.4
        """
        grid_range = (
            a1_range_to_grid_range(name, self.id)
            if name is not None
            else {"sheetId": self.id}
        )

        body = {"requests": [{"setBasicFilter": {"filter": {"range": grid_range}}}]}

        return self.spreadsheet.batch_update(body)

    def clear_basic_filter(self):
        """Remove the basic filter from a worksheet.

        .. versionadded:: 3.4
        """
        body = {
            "requests": [
                {
                    "clearBasicFilter": {
                        "sheetId": self.id,
                    }
                }
            ]
        }

        return self.spreadsheet.batch_update(body)

    def export(self, format):
        """.. deprecated:: 2.0

        This feature is not supported in Sheets API v4.
        """
        import warnings

        warnings.warn(
            "Worksheet.export() is deprecated, "
            "this feature is not supported in Sheets API v4",
            DeprecationWarning,
            stacklevel=2,
        )

    def duplicate(
        self, insert_sheet_index=None, new_sheet_id=None, new_sheet_name=None
    ):
        """Duplicate the sheet.

        :param int insert_sheet_index: (optional) The zero-based index
            where the new sheet should be inserted. The index of all sheets
            after this are incremented.
        :param int new_sheet_id: (optional) The ID of the new sheet.
            If not set, an ID is chosen. If set, the ID must not conflict with
            any existing sheet ID. If set, it must be non-negative.
        :param str new_sheet_name: (optional) The name of the new sheet.
            If empty, a new name is chosen for you.

        :returns: a newly created :class:`gspread.worksheet.Worksheet`.

        .. versionadded:: 3.1
        """
        return self.spreadsheet.duplicate_sheet(
            self.id, insert_sheet_index, new_sheet_id, new_sheet_name
        )

    def copy_to(
        self,
        spreadsheet_id,
    ):
        """Copies this sheet to another spreadsheet.

        :param str spreadsheet_id: The ID of the spreadsheet to copy
            the sheet to.
        :returns: a dict with the response containing information about
            the newly created sheet.
        :rtype: dict
        """
        return self.spreadsheet._spreadsheets_sheets_copy_to(self.id, spreadsheet_id)

    @cast_to_a1_notation
    def merge_cells(self, name, merge_type="MERGE_ALL"):
        """Merge cells. There are 3 merge types: ``MERGE_ALL``, ``MERGE_COLUMNS``,
        and ``MERGE_ROWS``.

        :param str name: Range name in A1 notation, e.g. 'A1:A5'.
        :param str merge_type: (optional) one of ``MERGE_ALL``,
            ``MERGE_COLUMNS``, or ``MERGE_ROWS``. Defaults to ``MERGE_ROWS``.
            See `MergeType`_ in the Sheets API reference.

        Alternatively, you may specify numeric boundaries. All values
        index from 1 (one):

        :param int first_row: First row number
        :param int first_col: First column number
        :param int last_row: Last row number
        :param int last_col: Last column number

        :returns: the response body from the request
        :rtype: dict

        .. _MergeType: https://developers.google.com/sheets/api/reference/rest/v4/spreadsheets/request#MergeType

        """
        grid_range = a1_range_to_grid_range(name, self.id)

        body = {
            "requests": [{"mergeCells": {"mergeType": merge_type, "range": grid_range}}]
        }

        return self.spreadsheet.batch_update(body)

    @cast_to_a1_notation
    def unmerge_cells(self, name):
        """Unmerge cells.

        Unmerge previously merged cells.

        :param str name: Range name in A1 notation, e.g. 'A1:A5'.

        Alternatively, you may specify numeric boundaries. All values
        index from 1 (one):

        :param int first_row: First row number
        :param int first_col: First column number
        :param int last_row: Last row number
        :param int last_col: Last column number

        :returns: the response body from the request
        :rtype: dict
        """

        grid_range = a1_range_to_grid_range(name, self.id)

        body = {
            "requests": [
                {
                    "unmergeCells": {
                        "range": grid_range,
                    },
                },
            ]
        }

        return self.spreadsheet.batch_update(body)

    def get_note(self, cell):
        """Get the content of the note located at `cell`, or the empty string if the
        cell does not have a note.

        :param str cell: A string with cell coordinates in A1 notation,
            e.g. 'D7'.
        """
        absolute_cell = absolute_range_name(self.title, cell)
        url = SPREADSHEET_URL % (self.spreadsheet.id)
        params = {"ranges": absolute_cell, "fields": "sheets/data/rowData/values/note"}
        response = self.client.request("get", url, params=params)
        response.raise_for_status()
        response_json = response.json()

        try:
            note = response_json["sheets"][0]["data"][0]["rowData"][0]["values"][0][
                "note"
            ]
        except (IndexError, KeyError):
            note = ""

        return note

    def update_notes(self, notes):
        """update multiple notes. The notes are attached to a certain cell.

        :param notes dict: A dict of notes with their cells coordinates and respective content

            dict format is:

            * key: the cell coordinates as A1 range format
            * value: the string content of the cell

            Example::

                {
                    "D7": "Please read my notes",
                    "GH42": "this one is too far",
                }

        .. versionadded:: 5.9
        """

        body = {"requests": []}

        for range, content in notes.items():
            if not isinstance(content, str):
                raise TypeError(
                    "Only string allowed as content for a note: '{} - {}'".format(
                        range, content
                    )
                )

            req = {
                "updateCells": {
                    "range": a1_range_to_grid_range(range, self.id),
                    "fields": "note",
                    "rows": [
                        {
                            "values": [
                                {
                                    "note": content,
                                },
                            ],
                        },
                    ],
                },
            }

            body["requests"].append(req)

        self.spreadsheet.batch_update(body)

    @cast_to_a1_notation
    def update_note(self, cell, content):
        """Update the content of the note located at `cell`.

        :param str cell: A string with cell coordinates in A1 notation,
            e.g. 'D7'.
        :param str note: The text note to insert.

        .. versionadded:: 3.7
        """
        self.update_notes({cell: content})

    @cast_to_a1_notation
    def insert_note(self, cell, content):
        """Insert a note. The note is attached to a certain cell.

        :param str cell: A string with cell coordinates in A1 notation,
            e.g. 'D7'.
        :param str content: The text note to insert.

        Alternatively, you may specify numeric boundaries. All values
        index from 1 (one):

        :param int first_row: First row number
        :param int first_col: First column number
        :param int last_row: Last row number
        :param int last_col: Last column number

        .. versionadded:: 3.7
        """
        self.update_notes({cell: content})

    def insert_notes(self, notes):
        """insert multiple notes. The notes are attached to a certain cell.

        :param notes dict: A dict of notes with their cells coordinates and respective content

            dict format is:

            * key: the cell coordinates as A1 range format
            * value: the string content of the cell

            Example::

                {
                    "D7": "Please read my notes",
                    "GH42": "this one is too far",
                }

        .. versionadded:: 5.9
        """
        self.update_notes(notes)

    def clear_notes(self, ranges):
        """Clear all notes located at the at the coordinates
        pointed to by ``ranges``.

        :param ranges list: List of A1 coordinates where to clear the notes.
            e.g. ``["A1", "GH42", "D7"]``
        """
        notes = {range: "" for range in ranges}
        self.update_notes(notes)

    @cast_to_a1_notation
    def clear_note(self, cell):
        """Clear a note. The note is attached to a certain cell.

        :param str cell: A string with cell coordinates in A1 notation,
            e.g. 'D7'.

        Alternatively, you may specify numeric boundaries. All values
        index from 1 (one):

        :param int first_row: First row number
        :param int first_col: First column number
        :param int last_row: Last row number
        :param int last_col: Last column number

        .. versionadded:: 3.7
        """
        # set the note to <empty string> will clear it
        self.update_notes({cell: ""})

    @cast_to_a1_notation
    def define_named_range(self, name, range_name):
        """
        :param str name: A string with range value in A1 notation,
            e.g. 'A1:A5'.

        Alternatively, you may specify numeric boundaries. All values
        index from 1 (one):

        :param int first_row: First row number
        :param int first_col: First column number
        :param int last_row: Last row number
        :param int last_col: Last column number

        :param range_name: The name to assign to the range of cells

        :returns: the response body from the request
        :rtype: dict
        """
        body = {
            "requests": [
                {
                    "addNamedRange": {
                        "namedRange": {
                            "name": range_name,
                            "range": a1_range_to_grid_range(name, self.id),
                        }
                    }
                }
            ]
        }
        return self.spreadsheet.batch_update(body)

    def delete_named_range(self, named_range_id):
        """
        :param str named_range_id: The ID of the named range to delete.
            Can be obtained with Spreadsheet.list_named_ranges()

        :returns: the response body from the request
        :rtype: dict
        """
        body = {
            "requests": [
                {
                    "deleteNamedRange": {
                        "namedRangeId": named_range_id,
                    }
                }
            ]
        }
        return self.spreadsheet.batch_update(body)

    def _add_dimension_group(self, start, end, dimension):
        """
        update this sheet by grouping 'dimension'

        :param int start: The start (inclusive) of the group
        :param int end: The end (exclusive) of the grou
        :param str dimension: The dimension to group, can be one of
            ``ROWS`` or ``COLUMNS``.
        """
        body = {
            "requests": [
                {
                    "addDimensionGroup": {
                        "range": {
                            "sheetId": self.id,
                            "dimension": dimension,
                            "startIndex": start,
                            "endIndex": end,
                        },
                    }
                }
            ]
        }

        return self.spreadsheet.batch_update(body)

    def add_dimension_group_columns(self, start, end):
        """
        Group columns in order to hide them in the UI.

        .. note::

            API behavior with nested groups and non-matching ``[start:end)``
            range can be found here: `Add Dimension Group Request`_

            .. _Add Dimension Group Request: https://developers.google.com/sheets/api/reference/rest/v4/spreadsheets/request#AddDimensionGroupRequest

        :param int start: The start (inclusive) of the group
        :param int end: The end (exclusive) of the group
        """
        return self._add_dimension_group(start, end, Dimension.cols)

    def add_dimension_group_rows(self, start, end):
        """
        Group rows in order to hide them in the UI.

        .. note::

            API behavior with nested groups and non-matching ``[start:end)``
            range can be found here `Add Dimension Group Request`_

        :param int start: The start (inclusive) of the group
        :param int end: The end (exclusive) of the group
        """
        return self._add_dimension_group(start, end, Dimension.rows)

    def _delete_dimension_group(self, start, end, dimension):
        """delete a dimension group in this sheet"""
        body = {
            "requests": [
                {
                    "deleteDimensionGroup": {
                        "range": {
                            "sheetId": self.id,
                            "dimension": dimension,
                            "startIndex": start,
                            "endIndex": end,
                        }
                    }
                }
            ]
        }

        return self.spreadsheet.batch_update(body)

    def delete_dimension_group_columns(self, start, end):
        """
        Remove the grouping of a set of columns.

        .. note::

            API behavior with nested groups and non-matching ``[start:end)``
            range can be found here `Delete Dimension Group Request`_

            .. _Delete Dimension Group Request: https://developers.google.com/sheets/api/reference/rest/v4/spreadsheets/request#DeleteDimensionGroupRequest

        :param int start: The start (inclusive) of the group
        :param int end: The end (exclusive) of the group
        """
        return self._delete_dimension_group(start, end, Dimension.cols)

    def delete_dimension_group_rows(self, start, end):
        """
        Remove the grouping of a set of rows.

        .. note::
            API behavior with nested groups and non-matching ``[start:end)``
            range can be found here `Delete Dimension Group Request`_

        :param int start: The start (inclusive) of the group
        :param int end: The end (exclusive) of the group
        """
        return self._delete_dimension_group(start, end, Dimension.rows)

    def list_dimension_group_columns(self):
        """
        List all the grouped columns in this worksheet.

        :returns: list of the grouped columns
        :rtype: list
        """
        return self._get_sheet_property("columnGroups", [])

    def list_dimension_group_rows(self):
        """
        List all the grouped rows in this worksheet.

        :returns: list of the grouped rows
        :rtype: list
        """
        return self._get_sheet_property("rowGroups", [])

    def _hide_dimension(self, start, end, dimension):
        """
        Update this sheet by hiding the given 'dimension'

        Index starts from 0.

        :param int start: The (inclusive) start of the dimension to hide
        :param int end: The (exclusive) end of the dimension to hide
        :param str dimension: The dimension to hide, can be one of
            ``ROWS`` or ``COLUMNS``.
        :type diension: :namedtuple:`~gspread.utils.Dimension`
        """
        body = {
            "requests": [
                {
                    "updateDimensionProperties": {
                        "range": {
                            "sheetId": self.id,
                            "dimension": dimension,
                            "startIndex": start,
                            "endIndex": end,
                        },
                        "properties": {
                            "hiddenByUser": True,
                        },
                        "fields": "hiddenByUser",
                    }
                }
            ]
        }

        return self.spreadsheet.batch_update(body)

    def hide_columns(self, start, end):
        """
        Explicitly hide the given column index range.

        Index starts from 0.

        :param int start: The (inclusive) starting column to hide
        :param int end: The (exclusive) end column to hide
        """
        return self._hide_dimension(start, end, Dimension.cols)

    def hide_rows(self, start, end):
        """
        Explicitly hide the given row index range.

        Index starts from 0.

        :param int start: The (inclusive) starting row to hide
        :param int end: The (exclusive) end row to hide
        """
        return self._hide_dimension(start, end, Dimension.rows)

    def _unhide_dimension(self, start, end, dimension):
        """
        Update this sheet by unhiding the given 'dimension'

        Index starts from 0.

        :param int start: The (inclusive) start of the dimension to unhide
        :param int end: The (inclusive) end of the dimension to unhide
        :param str dimension: The dimension to hide, can be one of
            ``ROWS`` or ``COLUMNS``.
        :type dimension: :namedtuple:`~gspread.utils.Dimension`
        """
        body = {
            "requests": [
                {
                    "updateDimensionProperties": {
                        "range": {
                            "sheetId": self.id,
                            "dimension": dimension,
                            "startIndex": start,
                            "endIndex": end,
                        },
                        "properties": {
                            "hiddenByUser": False,
                        },
                        "fields": "hiddenByUser",
                    }
                }
            ]
        }

        return self.spreadsheet.batch_update(body)

    def unhide_columns(self, start, end):
        """
        Explicitly unhide the given column index range.

        Index start from 0.

        :param int start: The (inclusive) starting column to hide
        :param int end: The (exclusive) end column to hide
        """
        return self._unhide_dimension(start, end, Dimension.cols)

    def unhide_rows(self, start, end):
        """
        Explicitly unhide the given row index range.

        Index start from 0.

        :param int start: The (inclusive) starting row to hide
        :param int end: The (exclusive) end row to hide
        """
        return self._unhide_dimension(start, end, Dimension.rows)

    def _set_hidden_flag(self, hidden):
        """Send the appropriate request to hide/show the current worksheet"""

        body = {
            "requests": [
                {
                    "updateSheetProperties": {
                        "properties": {
                            "sheetId": self.id,
                            "hidden": hidden,
                        },
                        "fields": "hidden",
                    }
                }
            ]
        }

        res = self.spreadsheet.batch_update(body)
        self._properties["hidden"] = hidden
        return res

    def hide(self):
        """Hides the current worksheet from the UI."""
        return self._set_hidden_flag(True)

    def show(self):
        """Show the current worksheet in the UI."""
        return self._set_hidden_flag(False)

    def _set_gridlines_hidden_flag(self, hidden):
        """Hide/show gridlines on the current worksheet"""

        body = {
            "requests": [
                {
                    "updateSheetProperties": {
                        "properties": {
                            "sheetId": self.id,
                            "gridProperties": {
                                "hideGridlines": hidden,
                            },
                        },
                        "fields": "gridProperties.hideGridlines",
                    }
                }
            ]
        }

        res = self.spreadsheet.batch_update(body)
        self._properties["gridProperties"]["hideGridlines"] = hidden
        return res

    def hide_gridlines(self):
        """Hide gridlines on the current worksheet"""
        return self._set_gridlines_hidden_flag(True)

    def show_gridlines(self):
        """Show gridlines on the current worksheet"""
        return self._set_gridlines_hidden_flag(False)

    def copy_range(
        self,
        source,
        dest,
        paste_type=PasteType.normal,
        paste_orientation=PasteOrientation.normal,
    ):
        """Copies a range of data from source to dest

        .. note::

           ``paste_type`` values are explained here: `Paste Types`_

           .. _Paste Types: https://developers.google.com/sheets/api/reference/rest/v4/spreadsheets/request#pastetype

        :param str source: The A1 notation of the source range to copy
        :param str dest: The A1 notation of the destination where to paste the data
            Can be the A1 notation of the top left corner where the range must be paste
            ex: G16, or a complete range notation ex: G16:I20.
            The dimensions of the destination range is not checked and has no effect,
            if the destination range does not match the source range dimension, the entire
            source range is copies anyway.
        :param paste_type: the paste type to apply. Many paste type are available from
            the Sheet API, see above note for detailed values for all values and their effects.
            Defaults to ``PasteType.normal``
        :type paste_type: :namedtuple:`~gspread.utils.PasteType`
        :param paste_orientation: The paste orient to apply.
            Possible values are: ``normal`` to keep the same orientation, ``transpose`` where all rows become columns and vice versa.
        :type paste_orientation: :namedtuple:`~gspread.utils.PasteOrientation`
        """
        body = {
            "requests": [
                {
                    "copyPaste": {
                        "source": a1_range_to_grid_range(source, self.id),
                        "destination": a1_range_to_grid_range(dest, self.id),
                        "pasteType": paste_type,
                        "pasteOrientation": paste_orientation,
                    }
                }
            ]
        }

        return self.spreadsheet.batch_update(body)

    def cut_range(
        self,
        source,
        dest,
        paste_type=PasteType.normal,
    ):
        """Moves a range of data form source to dest

        .. note::

           ``paste_type`` values are explained here: `Paste Types`_

           .. _Paste Types: https://developers.google.com/sheets/api/reference/rest/v4/spreadsheets/request#pastetype

        :param str source: The A1 notation of the source range to move
        :param str dest: The A1 notation of the destination where to paste the data
            **it must be a single cell** in the A1 notation. ex: G16
        :param paste_type: the paste type to apply. Many paste type are available from
            the Sheet API, see above note for detailed values for all values and their effects.
            Defaults to ``PasteType.normal``
        :type paste_type: :namedtuple:`~gspread.utils.PasteType`
        """

        # in the cut/paste request, the destination object
        # is a `gridCoordinate` and not a `gridRang`
        # it has different object keys
        grid_dest = a1_range_to_grid_range(dest, self.id)

        body = {
            "requests": [
                {
                    "cutPaste": {
                        "source": a1_range_to_grid_range(source, self.id),
                        "destination": {
                            "sheetId": grid_dest["sheetId"],
                            "rowIndex": grid_dest["startRowIndex"],
                            "columnIndex": grid_dest["startColumnIndex"],
                        },
                        "pasteType": paste_type,
                    }
                }
            ]
        }

        return self.spreadsheet.batch_update(body)
