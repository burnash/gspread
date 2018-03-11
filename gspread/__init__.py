# -*- coding: utf-8 -*-

"""
gspread
~~~~~~~

Google Spreadsheets client library.

"""

__version__ = '2.0.0'
__author__ = 'Anton Burnashev'


try:
    from urllib import urlencode
except ImportError:
    from urllib.parse import urlencode


from .client import Client
from .models import Spreadsheet, Worksheet, Cell
from .exceptions import (GSpreadException, AuthenticationError,
                         SpreadsheetNotFound, NoValidUrlKeyFound,
                         IncorrectCellLabel, WorksheetNotFound,
                         UpdateCellError, RequestError, CellNotFound)

from . import v4


def authorize(credentials, client_class=v4.Client):
    """Login to Google API using OAuth2 credentials.
    This is a shortcut function which
    instantiates :class:`gspread.v4.client.Client`
    and performs login right away.

    :returns: :class:`gspread.v4.client.Client` instance.
    """
    client = client_class(auth=credentials)
    client.login()
    return client
