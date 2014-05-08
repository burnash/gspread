# -*- coding: utf-8 -*-

"""
gspread
~~~~~~~

Google Spreadsheets client library.

"""

<<<<<<< 95d918ab8c3e881f4363e5f5a50e98f79c768ddf
<<<<<<< a69cd84f789e21aa91b9c488abd3dc4ac39c8361
__version__ = '0.5.0'
=======
__version__ = '0.2.5'
>>>>>>> # This is a combination of 2 commits.
=======
<<<<<<< HEAD
__version__ = '0.3.0'
>>>>>>> # This is a combination of 2 commits.
__author__ = 'Anton Burnashev'


try:
    from urllib import urlencode
except ImportError:
    from urllib.parse import urlencode


<<<<<<< 95d918ab8c3e881f4363e5f5a50e98f79c768ddf
<<<<<<< a69cd84f789e21aa91b9c488abd3dc4ac39c8361
from .client import Client, authorize
=======
=======
=======
__version__ = '0.2.5'
__author__ = 'Anton Burnashev'

>>>>>>> # This is a combination of 2 commits.
>>>>>>> # This is a combination of 2 commits.
from .client import Client, login, authorize
>>>>>>> # This is a combination of 2 commits.
from .models import Spreadsheet, Worksheet, Cell
from .exceptions import (GSpreadException, AuthenticationError,
                         SpreadsheetNotFound, NoValidUrlKeyFound,
                         IncorrectCellLabel, WorksheetNotFound,
                         UpdateCellError, RequestError, CellNotFound)
