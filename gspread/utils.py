# -*- coding: utf-8 -*-

"""
gspread.utils
~~~~~~~~~~~~~

This module contains utility functions.

"""

from xml.etree import ElementTree


def finditem(func, seq):
    """Finds and returns first item in iterable for which func(item) is True.

    """
    return next((item for item in seq if func(item)))


# http://stackoverflow.com/questions/749796/pretty-printing-xml-in-python
# http://effbot.org/zone/element-lib.htm#prettyprint
def _indent(elem, level=0):
    i = "\n" + level*"  "
    if len(elem):
        if not elem.text or not elem.text.strip():
            elem.text = i + "  "
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
        for elem in elem:
            _indent(elem, level+1)
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

def numericise(value, empty2zero=False):
    """Returns a value that depends on the input string:
        - Float if input can be converted to Float
        - Integer if iinputt can be converted to integer
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
    >>> numericise("")
    ''
    >>>
    """

    try:
        value = int(value)
    except ValueError:
        try: 
            value = float(value)
        except ValueError:
            if value == "" and empty2zero == True: 
                value = 0
                
    return value

def numericise_all(input, empty2zero=False):
    """Returns a list of numericised values from strings"""
    return [numericise(s, empty2zero) for s in input]

if __name__ == '__main__':
    import doctest
    doctest.testmod()