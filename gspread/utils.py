# -*- coding: utf-8 -*-

"""
gspread.utils
~~~~~~~~~~~~~

This module contains utility functions.

"""

import sys
import re
from functools import wraps
from collections import defaultdict

try:
    from collections.abc import Sequence
except ImportError:
    from collections import Sequence
from itertools import chain

from google.auth.credentials import Credentials as Credentials
from google.oauth2.credentials import Credentials as UserCredentials
from google.oauth2.service_account import (
    Credentials as ServiceAccountCredentials,
)

from .exceptions import IncorrectCellLabel, NoValidUrlKeyFound
from urllib.parse import quote as uquote


MAGIC_NUMBER = 64
CELL_ADDR_RE = re.compile(r'([A-Za-z]+)([1-9]\d*)')
A1_ADDR_ROW_COL_RE = re.compile(r'([A-Za-z]+)?([1-9]\d*)?$')

URL_KEY_V1_RE = re.compile(r'key=([^&#]+)')
URL_KEY_V2_RE = re.compile(r'/spreadsheets/d/([a-zA-Z0-9-_]+)')


def convert_credentials(credentials):
    module = credentials.__module__
    cls = credentials.__class__.__name__
    if 'oauth2client' in module and cls == 'ServiceAccountCredentials':
        return _convert_service_account(credentials)
    elif 'oauth2client' in module and cls in (
        'OAuth2Credentials',
        'AccessTokenCredentials',
        'GoogleCredentials',
    ):
        return _convert_oauth(credentials)
    elif isinstance(credentials, Credentials):
        return credentials

    raise TypeError(
        'Credentials need to be from either oauth2client or from google-auth.'
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
    data['token_uri'] = credentials.token_uri
    scopes = credentials._scopes.split() or [
        'https://www.googleapis.com/auth/drive',
        'https://spreadsheets.google.com/feeds',
    ]

    return ServiceAccountCredentials.from_service_account_info(
        data, scopes=scopes
    )


def finditem(func, seq):
    """Finds and returns first item in iterable for which func(item) is True.

    """
    return next((item for item in seq if func(item)))


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
    '32'
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

        # replace coma separating thousands to match python format
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
    input,
    empty2zero=False,
    default_blank="",
    allow_underscores_in_numeric_literals=False,
    ignore=None,
):
    """Returns a list of numericised values from strings except those from the
    row specified as ignore.

    :param list input: Input row
    :param bool empty2zero: (optional) Whether or not to return empty cells
        as 0 (zero). Defaults to ``False``.
    :param str default_blank: Which value to use for blank cells,
        defaults to empty string.
    :param bool allow_underscores_in_numeric_literals: Whether or not to allow
        visual underscores in numeric literals
    :param list ignore: List of ints of indices of the row (index 1) to ignore
        numericising.
    """
    ignored_rows = [input[x - 1] for x in (ignore or [])]
    numericised_list = [
        s
        if s in ignored_rows
        else numericise(
            s,
            empty2zero=empty2zero,
            default_blank=default_blank,
            allow_underscores_in_numeric_literals=allow_underscores_in_numeric_literals,
        )
        for s in input
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
        raise IncorrectCellLabel('(%s, %s)' % (row, col))

    div = col
    column_label = ''

    while div:
        (div, mod) = divmod(div, 26)
        if mod == 0:
            mod = 26
            div -= 1
        column_label = chr(mod + MAGIC_NUMBER) + column_label

    label = '%s%s' % (column_label, row)

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
            col += (ord(c) - MAGIC_NUMBER) * (26 ** i)
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
    (None, 1)

    >>> _a1_to_rowcol_unbounded('1')
    (1, None)

    >>> _a1_to_rowcol_unbounded('ABC123')
    (123, 731)

    >>> _a1_to_rowcol_unbounded('ABC')
    (None, 731)

    >>> _a1_to_rowcol_unbounded('123')
    (123, None)

    >>> _a1_to_rowcol_unbounded('1A')
    Traceback (most recent call last):
        ...
    gspread.exceptions.IncorrectCellLabel: 1A

    >>> _a1_to_rowcol_unbounded('')
    (None, None)

    """
    m = A1_ADDR_ROW_COL_RE.match(label)
    if m:
        column_label, row = m.groups()

        col = None
        if column_label:
            col = 0
            for i, c in enumerate(reversed(column_label)):
                col += (ord(c) - MAGIC_NUMBER) * (26 ** i)

        if row:
            row = int(row)
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
    start_label, _, end_label = name.partition(':')

    start_indices = _a1_to_rowcol_unbounded(start_label)

    start_row_index, start_column_index = [
        x - 1 if x is not None else x for x in start_indices
    ]

    end_row_index, end_column_index = (
        _a1_to_rowcol_unbounded(end_label) if end_label else start_indices
    )

    return filter_dict_values(
        {
            'sheetId': sheet_id,
            'startRowIndex': start_row_index,
            'endRowIndex': end_row_index,
            'startColumnIndex': start_column_index,
            'endColumnIndex': end_column_index,
        }
    )


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
                range_name = ':'.join((range_start, range_end))

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


def rightpad(row, max_len):
    pad_len = max_len - len(row)
    return row + ([''] * pad_len) if pad_len != 0 else row


def fill_gaps(L, rows=None, cols=None):

    try:
        max_cols = max(len(row) for row in L) if cols is None else cols
        max_rows = len(L) if rows is None else rows

        pad_rows = max_rows - len(L)

        if pad_rows:
            L = L + ([[]] * pad_rows)

        return [rightpad(row, max_cols) for row in L]
    except ValueError:
        return []


def cell_list_to_rect(cell_list):
    if not cell_list:
        return []

    rows = defaultdict(lambda: {})

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


def quote(value, safe='', encoding='utf-8'):
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
        return '{}!{}'.format(sheet_name, range_name)
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
                err = '%s got unexpected keyword arguments: %s'
                raise TypeError(err % (f.__name__, list(unexpected_kwargs)))

            for k, v in default_kwargs.items():
                kwargs.setdefault(k, v)

            return f(*args, **kwargs)

        return wrapper

    return decorate


if __name__ == '__main__':
    import doctest

    doctest.testmod()
