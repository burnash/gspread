# -*- coding: utf-8 -*-

"""
gspread.utils
~~~~~~~~~~~~~

This module contains utility functions.

"""

try:
    from lxml.etree import ElementTree
except ImportError:
    from xml.etree import ElementTree

from .exceptions import IncorrectCellLabel

MAGIC_NUMBER = 64


def finditem(func, seq):
    """Finds and returns first item in iterable for which func(item) is True.

    """
    return next((item for item in seq if func(item)))


# http://stackoverflow.com/questions/749796/pretty-printing-xml-in-python
# http://effbot.org/zone/element-lib.htm#prettyprint
def _indent(elem, level=0):
    i = "\n" + level * "  "
    if len(elem):
        if not elem.text or not elem.text.strip():
            elem.text = i + "  "
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
        for elem in elem:
            _indent(elem, level + 1)
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
    else:
        if level and (not elem.tail or not elem.tail.strip()):
            elem.tail = i


def _ds(elem):
    """ElementTree debug function.

    Indents and renders xml tree to a string.

    """
    _indent(elem)
    return ElementTree.tostring(elem)


def numericise(value, empty2zero=False, default_blank=""):
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


def numericise_all(input, empty2zero=False, default_blank=""):
    """Returns a list of numericised values from strings"""
    return [numericise(s, empty2zero, default_blank) for s in input]


def rowcol_to_a1(row, col):
    """Translates a row and column cell address to A1 notation.

    The result is a string containing the cell's coordinates in A1 notation.

    :param row: The row of the cell to be converted.
                Rows start at index 1.

    :param col: The column of the cell to be converted.
                Columns start at index 1.

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


if __name__ == '__main__':
    import doctest
    doctest.testmod()
