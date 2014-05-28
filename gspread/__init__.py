# -*- coding: utf-8 -*-

"""
gspread
~~~~~~~

Google Spreadsheets client library.

"""

<<<<<<< a69cd84f789e21aa91b9c488abd3dc4ac39c8361
__version__ = '0.5.0'
=======
__version__ = '0.2.5'
>>>>>>> # This is a combination of 2 commits.
__author__ = 'Anton Burnashev'


try:
    from urllib import urlencode
except ImportError:
    from urllib.parse import urlencode


<<<<<<< a69cd84f789e21aa91b9c488abd3dc4ac39c8361
from .client import Client, authorize
=======
from .client import Client, login, authorize
>>>>>>> # This is a combination of 2 commits.
from .models import Spreadsheet, Worksheet, Cell
from .exceptions import (GSpreadException, AuthenticationError,
                         SpreadsheetNotFound, NoValidUrlKeyFound,
                         IncorrectCellLabel, WorksheetNotFound,
                         UpdateCellError, RequestError, CellNotFound)
