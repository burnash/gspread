# -*- coding: utf-8 -*-

"""
gspread
~~~~~~~

Google Spreadsheets client library.

"""

__version__ = '0.6.2'
__author__ = 'Anton Burnashev'


try:
    from urllib import urlencode
except ImportError:
    from urllib.parse import urlencode


from .client import Client, authorize, public
from .models import Spreadsheet, Worksheet, Cell
from .exceptions import (GSpreadException, AuthenticationError,
                         SpreadsheetNotFound, NoValidUrlKeyFound,
                         IncorrectCellLabel, WorksheetNotFound,
                         UpdateCellError, RequestError, CellNotFound)
