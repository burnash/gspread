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
from itertools import chain

from .exceptions import IncorrectCellLabel, NoValidUrlKeyFound


if sys.version_info.major == 2:
    import urllib
elif sys.version_info.major == 3:
    import urllib.parse as urllib


MAGIC_NUMBER = 64
CELL_ADDR_RE = re.compile(r'([A-Za-z]+)([1-9]\d*)')

URL_KEY_V1_RE = re.compile(r'key=([^&#]+)')
URL_KEY_V2_RE = re.compile(r'/spreadsheets/d/([a-zA-Z0-9-_]+)')


def finditem(func, seq):
    """Finds and returns first item in iterable for which func(item) is True.

    """
    return next((item for item in seq if func(item)))


def numericise(value, empty2zero=False, default_blank="", allow_underscores_in_numeric_literals=False):
    """Returns a value that depends on the input string:
        - Float if input can be converted to Float
        - Integer if input can be converted to integer
        - Zero if the input string is empty and empty2zero flag is set
        - The same input string, empty or not, otherwise.

    Executable examples:

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
    if value is not None:
        if "_" in value and not allow_underscores_in_numeric_literals:
            return value
        try:
            value = int(value)
        except ValueError:
            try:
                value = float(value)
            except ValueError:
                if value == "":
                    if empty2zero:
                        value = 0
                    else:
                        value = default_blank

    return value


def numericise_all(input, empty2zero=False, default_blank="", allow_underscores_in_numeric_literals=False):
    """Returns a list of numericised values from strings"""
    return [numericise(s, empty2zero, default_blank, allow_underscores_in_numeric_literals) for s in input]


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

    :param label: A cell label in A1 notation, e.g. 'B1'.
                  Letter case is ignored.
    :type label: str

    :returns: a tuple containing `row` and `column` numbers. Both indexed
              from 1 (one).

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

    max_cols = max(len(row) for row in L) if cols is None else cols
    max_rows = len(L) if rows is None else rows

    pad_rows = max_rows - len(L)

    if pad_rows:
        L = L + ([[]] * pad_rows)

    return [rightpad(row, max_cols) for row in L]


def cell_list_to_rect(cell_list):
    if not cell_list:
        return []

    rows = defaultdict(lambda: {})

    row_offset = cell_list[0].row
    col_offset = cell_list[0].col

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
    return urllib.quote(value.encode(encoding), safe)


if __name__ == '__main__':
    import doctest
    doctest.testmod()
