"""
gspread.utils
~~~~~~~~~~~~~

This module contains utility functions.

"""

import re
from collections import defaultdict, namedtuple
from collections.abc import Sequence
from functools import wraps
from itertools import chain
from typing import (
    TYPE_CHECKING,
    Any,
    AnyStr,
    Callable,
    Dict,
    Iterable,
    List,
    Optional,
    Tuple,
    TypeVar,
    Union,
)
from urllib.parse import quote as uquote

from google.auth.credentials import Credentials as Credentials
from google.oauth2.credentials import Credentials as UserCredentials
from google.oauth2.service_account import Credentials as ServiceAccountCredentials

from .exceptions import IncorrectCellLabel, InvalidInputValue, NoValidUrlKeyFound

if TYPE_CHECKING:
    from .cell import Cell


MAGIC_NUMBER = 64
CELL_ADDR_RE = re.compile(r"([A-Za-z]+)([1-9]\d*)")
A1_ADDR_ROW_COL_RE = re.compile(r"([A-Za-z]+)?([1-9]\d*)?$")

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
MimeTypeType = namedtuple(
    "MimeType",
    ["google_sheets", "pdf", "excel", "csv", "open_office_sheet", "tsv", "zip"],
)
MimeType = MimeTypeType(
    "application/vnd.google-apps.spreadsheet",
    "application/pdf",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    "text/csv",
    "application/vnd.oasis.opendocument.spreadsheet",
    "text/tab-separated-values",
    "application/zip",
)
ExportFormatType = namedtuple(
    "ExportFormat", ["PDF", "EXCEL", "CSV", "OPEN_OFFICE_SHEET", "TSV", "ZIPPED_HTML"]
)
ExportFormat = ExportFormatType(
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


def convert_credentials(credentials: Credentials) -> Credentials:
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


def _convert_oauth(credentials: Any) -> Credentials:
    return UserCredentials(
        credentials.access_token,
        credentials.refresh_token,
        credentials.id_token,
        credentials.token_uri,
        credentials.client_id,
        credentials.client_secret,
        credentials.scopes,
    )


def _convert_service_account(credentials: Any) -> Credentials:
    data = credentials.serialization_data
    data["token_uri"] = credentials.token_uri
    scopes = credentials._scopes.split() or [
        "https://www.googleapis.com/auth/drive",
        "https://spreadsheets.google.com/feeds",
    ]

    return ServiceAccountCredentials.from_service_account_info(data, scopes=scopes)


T = TypeVar("T")


def finditem(func: Callable[[T], bool], seq: Iterable[T]) -> T:
    """Finds and returns first item in iterable for which func(item) is True."""
    return next(item for item in seq if func(item))


def numericise(
    value: Optional[AnyStr],
    empty2zero: bool = False,
    default_blank: Optional[AnyStr] = "",
    allow_underscores_in_numeric_literals: bool = False,
) -> Optional[Union[int, float, AnyStr]]:
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
    numericised: Optional[Union[int, float, AnyStr]] = value
    if isinstance(value, str):
        if "_" in value:
            if not allow_underscores_in_numeric_literals:
                return value
            value = value.replace("_", "")

        # replace comma separating thousands to match python format
        cleaned_value = value.replace(",", "")
        try:
            numericised = int(cleaned_value)
        except ValueError:
            try:
                numericised = float(cleaned_value)
            except ValueError:
                if value == "":
                    if empty2zero:
                        numericised = 0
                    else:
                        numericised = default_blank

    return numericised


def numericise_all(
    values: List[Optional[AnyStr]],
    empty2zero: bool = False,
    default_blank: Optional[AnyStr] = "",
    allow_underscores_in_numeric_literals: bool = False,
    ignore: List[int] = [],
) -> List[Optional[Union[int, float, AnyStr]]]:
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


def rowcol_to_a1(row: int, col: int) -> str:
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


def a1_to_rowcol(label: str) -> Tuple[int, int]:
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


IntOrInf = Union[int, float]


def _a1_to_rowcol_unbounded(label: str) -> Tuple[IntOrInf, IntOrInf]:
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

        col: IntOrInf
        if column_label:
            col = 0
            for i, c in enumerate(reversed(column_label.upper())):
                col += (ord(c) - MAGIC_NUMBER) * (26**i)
        else:
            col = float("inf")

        if row:
            row = int(row)
        else:
            row = float("inf")
    else:
        raise IncorrectCellLabel(label)

    return (row, col)


def a1_range_to_grid_range(name: str, sheet_id: Optional[int] = None) -> Dict[str, int]:
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

    filtered_grid_range: Dict[str, int] = {
        key: value for (key, value) in grid_range.items() if isinstance(value, int)
    }

    if sheet_id is not None:
        filtered_grid_range["sheetId"] = sheet_id

    return filtered_grid_range


def column_letter_to_index(column: str) -> int:
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

    if not isinstance(index, int):
        raise InvalidInputValue(
            "invalid value: {}, must be a column letter".format(column)
        )

    return index


def cast_to_a1_notation(method: Callable[..., Any]) -> Callable[..., Any]:
    """Decorator function casts wrapped arguments to A1 notation in range
    method calls.
    """

    @wraps(method)
    def wrapper(self: Any, *args: Any, **kwargs: Any) -> Any:
        try:
            if len(args):
                int(args[0])

                # Convert to A1 notation
                # Assuming rowcol_to_a1 has appropriate typing
                range_start = rowcol_to_a1(*args[:2])
                # Assuming rowcol_to_a1 has appropriate typing
                range_end = rowcol_to_a1(*args[-2:])
                range_name = ":".join((range_start, range_end))

                args = (range_name,) + args[4:]
        except ValueError:
            pass

        return method(self, *args, **kwargs)

    return wrapper


def extract_id_from_url(url: str) -> str:
    m2 = URL_KEY_V2_RE.search(url)
    if m2:
        return m2.group(1)

    m1 = URL_KEY_V1_RE.search(url)
    if m1:
        return m1.group(1)

    raise NoValidUrlKeyFound


def wid_to_gid(wid: str) -> str:
    """Calculate gid of a worksheet from its wid."""
    widval = wid[1:] if len(wid) > 3 else wid
    xorval = 474 if len(wid) > 3 else 31578
    return str(int(widval, 36) ^ xorval)


def rightpad(row: List[Any], max_len: int) -> List[Any]:
    pad_len = max_len - len(row)
    return row + ([""] * pad_len) if pad_len != 0 else row


def fill_gaps(
    L: List[List[Any]], rows: Optional[int] = None, cols: Optional[int] = None
) -> List[List[Any]]:
    try:
        max_cols = max(len(row) for row in L) if cols is None else cols
        max_rows = len(L) if rows is None else rows

        pad_rows = max_rows - len(L)

        if pad_rows:
            L = L + ([[]] * pad_rows)

        return [rightpad(row, max_cols) for row in L]
    except ValueError:
        return [[]]


def cell_list_to_rect(cell_list: List["Cell"]) -> List[List[Optional[str]]]:
    if not cell_list:
        return []

    rows: Dict[int, Dict[int, str]] = defaultdict(lambda: {})

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


def quote(value: str, safe: str = "", encoding: str = "utf-8") -> str:
    return uquote(value.encode(encoding), safe)


def absolute_range_name(sheet_name: str, range_name: Optional[str] = None) -> str:
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


def is_scalar(x: Any) -> bool:
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

    :param worksheet_metadata: The metadata returned by the Google API for the worksheet. Should have a "merges" key.

    :param values: The values returned by the Google API for the worksheet. 2D array.
    """
    merges = worksheet_metadata.get("merges", [])
    # each merge has "startRowIndex", "endRowIndex", "startColumnIndex", "endColumnIndex
    new_values = [[v for v in row] for row in values]

    for merge in merges:
        start_row, end_row = merge["startRowIndex"], merge["endRowIndex"]
        start_col, end_col = merge["startColumnIndex"], merge["endColumnIndex"]
        top_left_value = values[start_row][start_col]
        row_indices = range(start_row, end_row)
        col_indices = range(start_col, end_col)
        for row_index in row_indices:
            for col_index in col_indices:
                new_values[row_index][col_index] = top_left_value

    return new_values


if __name__ == "__main__":
    import doctest

    doctest.testmod()
