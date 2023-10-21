"""
gspread.utils
~~~~~~~~~~~~~

This module contains utility functions.

"""

import os
import re
import warnings
from collections import defaultdict, namedtuple
from collections.abc import Sequence
from functools import wraps
from itertools import chain
from math import inf
from typing import Mapping
from urllib.parse import quote as uquote

from google.auth.credentials import Credentials as Credentials
from google.oauth2.credentials import Credentials as UserCredentials
from google.oauth2.service_account import Credentials as ServiceAccountCredentials

from .exceptions import IncorrectCellLabel, InvalidInputValue, NoValidUrlKeyFound

MAGIC_NUMBER = 64
CELL_ADDR_RE = re.compile(r"([A-Za-z]+)([1-9]\d*)")
A1_ADDR_ROW_COL_RE = re.compile(r"([A-Za-z]+)?([1-9]\d*)?$")
A1_ADDR_FULL_RE = re.compile(r"[A-Za-z]+\d+:[A-Za-z]+\d+")  # e.g. A1:B2 not A1:B

URL_KEY_V1_RE = re.compile(r"key=([^&#]+)")
URL_KEY_V2_RE = re.compile(r"/spreadsheets/d/([a-zA-Z0-9-_]+)")

Dimension = namedtuple("Dimension", ["rows", "cols"])("ROWS", "COLUMNS")
ValueRenderOption = namedtuple(
    "ValueRenderOption", ["formatted", "unformatted", "formula"]
)("FORMATTED_VALUE", "UNFORMATTED_VALUE", "FORMULA")
ValueInputOption = namedtuple("ValueInputOption", ["raw", "user_entered"])(
    "RAW", "USER_ENTERED"
)
DateTimeOption = namedtuple(
    "DateTimeOption", ["serial_number", "formatted_string", "formated_string"]
)("SERIAL_NUMBER", "FORMATTED_STRING", "FORMATTED_STRING")
MimeType = namedtuple(
    "MimeType",
    ["google_sheets", "pdf", "excel", "csv", "open_office_sheet", "tsv", "zip"],
)(
    "application/vnd.google-apps.spreadsheet",
    "application/pdf",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    "text/csv",
    "application/vnd.oasis.opendocument.spreadsheet",
    "text/tab-separated-values",
    "application/zip",
)
ExportFormat = namedtuple(
    "ExportFormat", ["PDF", "EXCEL", "CSV", "OPEN_OFFICE_SHEET", "TSV", "ZIPPED_HTML"]
)(
    MimeType.pdf,
    MimeType.excel,
    MimeType.csv,
    MimeType.open_office_sheet,
    MimeType.tsv,
    MimeType.zip,
)

PasteType = namedtuple(
    "PasteType",
    [
        "normal",
        "values",
        "format",
        "no_borders",
        "formula",
        "data_validation",
        "conditional_formating",
    ],
)(
    "PASTE_NORMAL",
    "PASTE_VALUES",
    "PASTE_FORMAT",
    "PASTE_NO_BORDERS",
    "PASTE_FORMULA",
    "PASTE_DATA_VALIDATION",
    "PASTE_CONDITIONAL_FORMATTING",
)

PasteOrientation = namedtuple("PasteOrientation", ["normal", "transpose"])(
    "NORMAL", "TRANSPOSE"
)

DEPRECATION_WARNING_TEMPLATE = (
    "[Deprecated][in version {v_deprecated}]: {msg_deprecated}"
)

REQUIRED_KWARGS = "required"

SILENCE_WARNINGS_ENV_KEY = "GSPREAD_SILENCE_WARNINGS"


def convert_credentials(credentials):
    module = credentials.__module__
    cls = credentials.__class__.__name__
    if "oauth2client" in module and cls == "ServiceAccountCredentials":
        return _convert_service_account(credentials)
    elif "oauth2client" in module and cls in (
        "OAuth2Credentials",
        "AccessTokenCredentials",
        "GoogleCredentials",
    ):
        return _convert_oauth(credentials)
    elif isinstance(credentials, Credentials):
        return credentials

    raise TypeError(
        "Credentials need to be from either oauth2client or from google-auth."
    )


def _convert_oauth(credentials):
    return UserCredentials(
        credentials.access_token,
        credentials.refresh_token,
        credentials.id_token,
        credentials.token_uri,
        credentials.client_id,
        credentials.client_secret,
        credentials.scopes,
    )


def _convert_service_account(credentials):
    data = credentials.serialization_data
    data["token_uri"] = credentials.token_uri
    scopes = credentials._scopes.split() or [
        "https://www.googleapis.com/auth/drive",
        "https://spreadsheets.google.com/feeds",
    ]

    return ServiceAccountCredentials.from_service_account_info(data, scopes=scopes)


def finditem(func, seq):
    """Finds and returns first item in iterable for which func(item) is True."""
    return next(item for item in seq if func(item))


def numericise(
    value,
    empty2zero=False,
    default_blank="",
    allow_underscores_in_numeric_literals=False,
):
    """Returns a value that depends on the input:

        - Float if input is a string that can be converted to Float
        - Integer if input is a string that can be converted to integer
        - Zero if the input is a string that is empty and empty2zero flag is set
        - The unmodified input value, otherwise.

    Examples::

        >>> numericise("faa")
        'faa'

    >>> numericise("3")
    3

    >>> numericise("3_2", allow_underscores_in_numeric_literals=False)
    '3_2'

    >>> numericise("3_2", allow_underscores_in_numeric_literals=True)
    32

    >>> numericise("3.1")
    3.1

    >>> numericise("2,000.1")
    2000.1

    >>> numericise("", empty2zero=True)
    0

    >>> numericise("", empty2zero=False)
    ''

    >>> numericise("", default_blank=None)
    >>>

    >>> numericise("", default_blank="foo")
    'foo'

    >>> numericise("")
    ''

    >>> numericise(None)
    >>>
    """
    if isinstance(value, str):
        if "_" in value:
            if not allow_underscores_in_numeric_literals:
                return value
            value = value.replace("_", "")

        # replace comma separating thousands to match python format
        cleaned_value = value.replace(",", "")
        try:
            int_value = int(cleaned_value)
            return int_value
        except ValueError:
            try:
                float_value = float(cleaned_value)
                return float_value
            except ValueError:
                if value == "":
                    if empty2zero:
                        value = 0
                    else:
                        value = default_blank

    return value


def numericise_all(
    values,
    empty2zero=False,
    default_blank="",
    allow_underscores_in_numeric_literals=False,
    ignore=[],
):
    """Returns a list of numericised values from strings except those from the
    row specified as ignore.

    :param list values: Input row
    :param bool empty2zero: (optional) Whether or not to return empty cells
        as 0 (zero). Defaults to ``False``.
    :param str default_blank: Which value to use for blank cells,
        defaults to empty string.
    :param bool allow_underscores_in_numeric_literals: Whether or not to allow
        visual underscores in numeric literals
    :param list ignore: List of ints of indices of the row (index 1) to ignore
        numericising.
    """
    # in case someone explicitly passes `None` as ignored list
    ignore = ignore or []

    numericised_list = [
        values[index]
        if index + 1 in ignore
        else numericise(
            values[index],
            empty2zero=empty2zero,
            default_blank=default_blank,
            allow_underscores_in_numeric_literals=allow_underscores_in_numeric_literals,
        )
        for index in range(len(values))
    ]

    return numericised_list


def rowcol_to_a1(row, col):
    """Translates a row and column cell address to A1 notation.

    :param row: The row of the cell to be converted.
        Rows start at index 1.
    :type row: int, str

    :param col: The column of the cell to be converted.
        Columns start at index 1.
    :type row: int, str

    :returns: a string containing the cell's coordinates in A1 notation.

    Example:

    >>> rowcol_to_a1(1, 1)
    A1

    """
    row = int(row)
    col = int(col)

    if row < 1 or col < 1:
        raise IncorrectCellLabel("({}, {})".format(row, col))

    div = col
    column_label = ""

    while div:
        (div, mod) = divmod(div, 26)
        if mod == 0:
            mod = 26
            div -= 1
        column_label = chr(mod + MAGIC_NUMBER) + column_label

    label = "{}{}".format(column_label, row)

    return label


def a1_to_rowcol(label):
    """Translates a cell's address in A1 notation to a tuple of integers.

    :param str label: A cell label in A1 notation, e.g. 'B1'.
        Letter case is ignored.
    :returns: a tuple containing `row` and `column` numbers. Both indexed
              from 1 (one).
    :rtype: tuple

    Example:

    >>> a1_to_rowcol('A1')
    (1, 1)

    """
    m = CELL_ADDR_RE.match(label)
    if m:
        column_label = m.group(1).upper()
        row = int(m.group(2))

        col = 0
        for i, c in enumerate(reversed(column_label)):
            col += (ord(c) - MAGIC_NUMBER) * (26**i)
    else:
        raise IncorrectCellLabel(label)

    return (row, col)


def _a1_to_rowcol_unbounded(label):
    """Translates a cell's address in A1 notation to a tuple of integers.

    Same as `a1_to_rowcol()` but allows for missing row or column part
    (e.g. "A" for the first column)

    :returns: a tuple containing `row` and `column` numbers. Both indexed
        from 1 (one).
    :rtype: tuple

    Example:

    >>> _a1_to_rowcol_unbounded('A1')
    (1, 1)

    >>> _a1_to_rowcol_unbounded('A')
    (inf, 1)

    >>> _a1_to_rowcol_unbounded('1')
    (1, inf)

    >>> _a1_to_rowcol_unbounded('ABC123')
    (123, 731)

    >>> _a1_to_rowcol_unbounded('ABC')
    (inf, 731)

    >>> _a1_to_rowcol_unbounded('123')
    (123, inf)

    >>> _a1_to_rowcol_unbounded('1A')
    Traceback (most recent call last):
        ...
    gspread.exceptions.IncorrectCellLabel: 1A

    >>> _a1_to_rowcol_unbounded('')
    (inf, inf)

    """
    m = A1_ADDR_ROW_COL_RE.match(label)
    if m:
        column_label, row = m.groups()

        if column_label:
            col = 0
            for i, c in enumerate(reversed(column_label.upper())):
                col += (ord(c) - MAGIC_NUMBER) * (26**i)
        else:
            col = inf

        if row:
            row = int(row)
        else:
            row = inf
    else:
        raise IncorrectCellLabel(label)

    return (row, col)


def a1_range_to_grid_range(name, sheet_id=None):
    """Converts a range defined in A1 notation to a dict representing
    a `GridRange`_.

    All indexes are zero-based. Indexes are half open, e.g the start
    index is inclusive and the end index is exclusive: [startIndex, endIndex).

    Missing indexes indicate the range is unbounded on that side.

    .. _GridRange: https://developers.google.com/sheets/api/reference/rest/v4/spreadsheets/other#GridRange

    Examples::

        >>> a1_range_to_grid_range('A1:A1')
        {'startRowIndex': 0, 'endRowIndex': 1, 'startColumnIndex': 0, 'endColumnIndex': 1}

    >>> a1_range_to_grid_range('A3:B4')
    {'startRowIndex': 2, 'endRowIndex': 4, 'startColumnIndex': 0, 'endColumnIndex': 2}

    >>> a1_range_to_grid_range('A:B')
    {'startColumnIndex': 0, 'endColumnIndex': 2}

    >>> a1_range_to_grid_range('A5:B')
    {'startRowIndex': 4, 'startColumnIndex': 0, 'endColumnIndex': 2}

    >>> a1_range_to_grid_range('A1')
    {'startRowIndex': 0, 'endRowIndex': 1, 'startColumnIndex': 0, 'endColumnIndex': 1}

    >>> a1_range_to_grid_range('A')
    {'startColumnIndex': 0, 'endColumnIndex': 1}

    >>> a1_range_to_grid_range('1')
    {'startRowIndex': 0, 'endRowIndex': 1}

    >>> a1_range_to_grid_range('A1', sheet_id=0)
    {'sheetId': 0, 'startRowIndex': 0, 'endRowIndex': 1, 'startColumnIndex': 0, 'endColumnIndex': 1}
    """
    start_label, _, end_label = name.partition(":")

    start_row_index, start_column_index = _a1_to_rowcol_unbounded(start_label)

    end_row_index, end_column_index = _a1_to_rowcol_unbounded(end_label or start_label)

    if start_row_index > end_row_index:
        start_row_index, end_row_index = end_row_index, start_row_index

    if start_column_index > end_column_index:
        start_column_index, end_column_index = end_column_index, start_column_index

    grid_range = {
        "startRowIndex": start_row_index - 1,
        "endRowIndex": end_row_index,
        "startColumnIndex": start_column_index - 1,
        "endColumnIndex": end_column_index,
    }

    grid_range = {key: value for (key, value) in grid_range.items() if value != inf}

    if sheet_id is not None:
        grid_range["sheetId"] = sheet_id

    return grid_range


def column_letter_to_index(column):
    """Converts a column letter to its numerical index.

    This is useful when using the method :meth:`gspread.worksheet.Worksheet.col_values`.
    Which requires a column index.

    This function is case-insensitive.

    Raises :exc:`gspread.exceptions.InvalidInputValue` in case of invalid input.

    Examples::

        >>> column_letter_to_index("a")
        1

    >>> column_letter_to_index("A")
    1

    >>> column_letter_to_index("AZ")
    52

    >>> column_letter_to_index("!@#$%^&")
    ...
    gspread.exceptions.InvalidInputValue: invalid value: !@#$%^&, must be a column letter
    """
    try:
        (_, index) = _a1_to_rowcol_unbounded(column)
    except IncorrectCellLabel:
        # make it coherent and raise the same exception in case of any error
        # from user input value
        raise InvalidInputValue(
            "invalid value: {}, must be a column letter".format(column)
        )

    if index is inf:
        raise InvalidInputValue(
            "invalid value: {}, must be a column letter".format(column)
        )

    return index


def cast_to_a1_notation(method):
    """Decorator function casts wrapped arguments to A1 notation in range
    method calls.
    """

    @wraps(method)
    def wrapper(self, *args, **kwargs):
        try:
            if len(args):
                int(args[0])

                # Convert to A1 notation
                range_start = rowcol_to_a1(*args[:2])
                range_end = rowcol_to_a1(*args[-2:])
                range_name = ":".join((range_start, range_end))

                args = (range_name,) + args[4:]
        except ValueError:
            pass

        return method(self, *args, **kwargs)

    return wrapper


def extract_id_from_url(url):
    m2 = URL_KEY_V2_RE.search(url)
    if m2:
        return m2.group(1)

    m1 = URL_KEY_V1_RE.search(url)
    if m1:
        return m1.group(1)

    raise NoValidUrlKeyFound


def wid_to_gid(wid):
    """Calculate gid of a worksheet from its wid."""
    widval = wid[1:] if len(wid) > 3 else wid
    xorval = 474 if len(wid) > 3 else 31578
    return str(int(widval, 36) ^ xorval)


def rightpad(row, max_len, padding_value=""):
    pad_len = max_len - len(row)
    return row + ([padding_value] * pad_len) if pad_len != 0 else row


def fill_gaps(L, rows=None, cols=None, padding_value=""):
    """Fill gaps in a list of lists.
    e.g.,::

        >>> L = [
        ... [1, 2, 3],
        ... ]
        >>> fill_gaps(L, 2, 4)
        [
            [1, 2, 3, ""],
            ["", "", "", ""]
        ]

    :param L: List of lists to fill gaps in.
    :param rows: Number of rows to fill.
    :param cols: Number of columns to fill.
    :param padding_value: Default value to fill gaps with.

    :type L: list[list[T]]
    :type rows: int
    :type cols: int
    :type padding_value: T

    :return: List of lists with gaps filled.
    :rtype: list[list[T]]:
    """
    try:
        max_cols = max(len(row) for row in L) if cols is None else cols
        max_rows = len(L) if rows is None else rows

        pad_rows = max_rows - len(L)

        if pad_rows:
            L = L + ([[]] * pad_rows)

        return [rightpad(row, max_cols, padding_value=padding_value) for row in L]
    except ValueError:
        return []


def cell_list_to_rect(cell_list):
    if not cell_list:
        return []

    rows = defaultdict(dict)

    row_offset = min(c.row for c in cell_list)
    col_offset = min(c.col for c in cell_list)

    for cell in cell_list:
        row = rows.setdefault(int(cell.row) - row_offset, {})
        row[cell.col - col_offset] = cell.value

    if not rows:
        return []

    all_row_keys = chain.from_iterable(row.keys() for row in rows.values())
    rect_cols = range(max(all_row_keys) + 1)
    rect_rows = range(max(rows.keys()) + 1)

    # Return the values of the cells as a list of lists where each sublist
    # contains all of the values for one row. The Google API requires a rectangle
    # of updates, so if a cell isn't present in the input cell_list, then the
    # value will be None and will not be updated.
    return [[rows[i].get(j) for j in rect_cols] for i in rect_rows]


def quote(value, safe="", encoding="utf-8"):
    return uquote(value.encode(encoding), safe)


def absolute_range_name(sheet_name, range_name=None):
    """Return an absolutized path of a range.

    >>> absolute_range_name("Sheet1", "A1:B1")
    "'Sheet1'!A1:B1"

    >>> absolute_range_name("Sheet1", "A1")
    "'Sheet1'!A1"

    >>> absolute_range_name("Sheet1")
    "'Sheet1'"

    >>> absolute_range_name("Sheet'1")
    "'Sheet''1'"

    >>> absolute_range_name("Sheet''1")
    "'Sheet''''1'"

    >>> absolute_range_name("''sheet12''", "A1:B2")
    "'''''sheet12'''''!A1:B2"
    """
    sheet_name = "'{}'".format(sheet_name.replace("'", "''"))

    if range_name:
        return "{}!{}".format(sheet_name, range_name)
    else:
        return sheet_name


def is_scalar(x):
    """Return True if the value is scalar.

    A scalar is not a sequence but can be a string.

    >>> is_scalar([])
    False

    >>> is_scalar([1, 2])
    False

    >>> is_scalar(42)
    True

    >>> is_scalar('nice string')
    True

    >>> is_scalar({})
    True

    >>> is_scalar(set())
    True
    """
    return isinstance(x, str) or not isinstance(x, Sequence)


def filter_dict_values(D):
    """Return a shallow copy of D with all `None` values excluded.

    >>> filter_dict_values({'a': 1, 'b': 2, 'c': None})
    {'a': 1, 'b': 2}

    >>> filter_dict_values({'a': 1, 'b': 2, 'c': 0})
    {'a': 1, 'b': 2, 'c': 0}

    >>> filter_dict_values({})
    {}

    >>> filter_dict_values({'imnone': None})
    {}
    """
    return {k: v for k, v in D.items() if v is not None}


def accepted_kwargs(**default_kwargs):
    """
    >>> @accepted_kwargs(d='d', e=None)
    ... def foo(a, b, c='c', **kwargs):
    ...     return {
    ...         'a': a,
    ...         'b': b,
    ...         'c': c,
    ...         'd': kwargs['d'],
    ...         'e': kwargs['e'],
    ...     }
    ...

    >>> foo('a', 'b')
    {'a': 'a', 'b': 'b', 'c': 'c', 'd': 'd', 'e': None}

    >>> foo('a', 'b', 'NEW C')
    {'a': 'a', 'b': 'b', 'c': 'NEW C', 'd': 'd', 'e': None}

    >>> foo('a', 'b', e='Not None')
    {'a': 'a', 'b': 'b', 'c': 'c', 'd': 'd', 'e': 'Not None'}

    >>> foo('a', 'b', d='NEW D')
    {'a': 'a', 'b': 'b', 'c': 'c', 'd': 'NEW D', 'e': None}

    >>> foo('a', 'b', a_typo='IS DETECTED')
    Traceback (most recent call last):
    ...
    TypeError: foo got unexpected keyword arguments: ['a_typo']

    >>> foo('a', 'b', d='NEW D', c='THIS DOES NOT WORK BECAUSE OF d')
    Traceback (most recent call last):
    ...
    TypeError: foo got unexpected keyword arguments: ['c']

    """

    def decorate(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            unexpected_kwargs = set(kwargs) - set(default_kwargs)
            if unexpected_kwargs:
                err = "%s got unexpected keyword arguments: %s"
                raise TypeError(err % (f.__name__, list(unexpected_kwargs)))

            for k, v in default_kwargs.items():
                if v != REQUIRED_KWARGS:
                    kwargs.setdefault(k, v)

            return f(*args, **kwargs)

        return wrapper

    return decorate


def combined_merge_values(worksheet_metadata, values):
    """For each merged region, replace all values with the value of the top-left cell of the region.
    e.g., replaces
    [
    [1, None, None],
    [None, None, None],
    ]
    with
    [
    [1, 1, None],
    [1, 1, None],
    ]
    if the top-left four cells are merged.

    :param worksheet_metadata: The metadata returned by the Google API for the worksheet.
        Should have a "merges" key.

    :param values: The values returned by the Google API for the worksheet. 2D array.
    """
    merges = worksheet_metadata.get("merges", [])
    # each merge has "startRowIndex", "endRowIndex", "startColumnIndex", "endColumnIndex
    new_values = [list(row) for row in values]

    # max row and column indices
    max_row_index = len(values) - 1
    max_col_index = len(values[0]) - 1

    for merge in merges:
        start_row, end_row = merge["startRowIndex"], merge["endRowIndex"]
        start_col, end_col = merge["startColumnIndex"], merge["endColumnIndex"]
        # if out of bounds, ignore
        if start_row > max_row_index or start_col > max_col_index:
            continue
        top_left_value = values[start_row][start_col]
        row_indices = range(start_row, end_row)
        col_indices = range(start_col, end_col)
        for row_index in row_indices:
            for col_index in col_indices:
                # if out of bounds, ignore
                if row_index > max_row_index or col_index > max_col_index:
                    continue
                new_values[row_index][col_index] = top_left_value

    return new_values


def convert_hex_to_colors_dict(hex_color: str) -> Mapping[str, float]:
    """Convert a hex color code to RGB color values.

    :param str hex_color: Hex color code in the format "#RRGGBB".

    :returns: Dict containing the color's red, green and blue values between 0 and 1.
    :rtype: dict

    :raises:
        ValueError: If the input hex string is not in the correct format or length.

    Examples:
        >>> convert_hex_to_colors_dict("#3300CC")
        {'red': 0.2, 'green': 0.0, 'blue': 0.8}

        >>> convert_hex_to_colors_dict("#30C")
        {'red': 0.2, 'green': 0.0, 'blue': 0.8}

    """
    hex_color = hex_color.lstrip("#")

    # Google API ColorStyle Reference:
    # "The alpha value in the Color object isn't generally supported."
    # https://developers.google.com/sheets/api/reference/rest/v4/spreadsheets/other#colorstyle
    if len(hex_color) == 8:
        hex_color = hex_color[:-2]

    # Expand 3 character hex.
    if len(hex_color) == 3:
        hex_color = "".join([char * 2 for char in hex_color])

    if len(hex_color) != 6:
        raise ValueError("Hex color code must be in the format '#RRGGBB'.")

    try:
        rgb_color = {
            "red": int(hex_color[0:2], 16) / 255,
            "green": int(hex_color[2:4], 16) / 255,
            "blue": int(hex_color[4:6], 16) / 255,
        }

        return rgb_color
    except ValueError as ex:
        raise ValueError(f"Invalid character in hex color string: #{hex_color}") from ex


def convert_colors_to_hex_value(
    red: float = 0.0, green: float = 0.0, blue: float = 0.0
) -> str:
    """Convert RGB color values to a hex color code.

    :param float red: Red color value (0-1).
    :param float green: Green color value (0-1).
    :param float blue: Blue color value (0-1).

    :returns: Hex color code in the format "#RRGGBB".
    :rtype: str

    :raises:
        ValueError: If any color value is out of the accepted range (0-1).

    Example:

        >>> convert_colors_to_hex_value(0.2, 0, 0.8)
        '#3300CC'

        >>> convert_colors_to_hex_value(green=0.5)
        '#008000'
    """

    def to_hex(value: float) -> str:
        """
        Convert an integer to a 2-digit uppercase hex string.
        """
        hex_value = hex(round(value * 255))[2:]
        return hex_value.upper().zfill(2)

    if any(value < 0 or value > 1 for value in (red, green, blue)):
        raise ValueError("Color value out of accepted range 0-1.")

    return f"#{to_hex(red)}{to_hex(green)}{to_hex(blue)}"


def is_full_a1_notation(range_name: str) -> bool:
    """Check if the range name is a full A1 notation.
    "A1:B2", "Sheet1!A1:B2" are full A1 notations
    "A1:B", "A1" are not

    Args:
        range_name (str): The range name to check.

    Returns:
        bool: True if the range name is a full A1 notation, False otherwise.

    Examples:

        >>> is_full_a1_notation("A1:B2")
        True

        >>> is_full_a1_notation("A1:B")
        False
    """
    return A1_ADDR_FULL_RE.search(range_name) is not None


def get_a1_from_absolute_range(range_name: str) -> str:
    """Get the A1 notation from an absolute range name.
    "Sheet1!A1:B2" -> "A1:B2"
    "A1:B2" -> "A1:B2"

    Args:
        range_name (str): The range name to check.

    Returns:
        str: The A1 notation of the range name stripped of the sheet.
    """
    if "!" in range_name:
        return range_name.split("!")[1]
    return range_name


def deprecation_warning(version: str, msg: str) -> None:
    """Emit a deprecation warning.

    ..note::

        This warning can be silenced by setting the environment variable:
        GSPREAD_SILENCE_WARNINGS=1
    """

    # do not emit warning if env variable is set specifically to 1
    if os.getenv(SILENCE_WARNINGS_ENV_KEY, "0") == "1":
        return

    warnings.warn(
        DEPRECATION_WARNING_TEMPLATE.format(v_deprecated=version, msg_deprecated=msg),
        DeprecationWarning,
        4,  # showd the 4th stack: [1]:current->[2]:deprecation_warning->[3]:<gspread method/function>->[4]:<user's code>
    )


if __name__ == "__main__":
    import doctest

    doctest.testmod()
