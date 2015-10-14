# -*- coding: utf-8 -*-

"""
gspread
~~~~~~~

Google Spreadsheets client library.

"""
# trying to work with pip
#from pkg_resources import get_distribution
#__version__ = '0.2.6'#get_distribution('gspread').version

__version__ = '0.2.6'
__author__ = 'Anton Burnashev'


try:
    from urllib import urlencode
except ImportError:
    from urllib.parse import urlencode


from .client import Client, login, authorize
from .models import Spreadsheet, Worksheet, Cell
from .exceptions import (GSpreadException, AuthenticationError,
                         SpreadsheetNotFound, NoValidUrlKeyFound,
                         IncorrectCellLabel, WorksheetNotFound,
                         UpdateCellError, RequestError, CellNotFound)
