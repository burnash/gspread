# -*- coding: utf-8 -*-

"""
gspread
~~~~~~~

Google Spreadsheets client library.

"""


__version__ = '3.1.0'
__author__ = 'Anton Burnashev'


from .client import Client
from .models import Spreadsheet, Worksheet, Cell

from .exceptions import (
    GSpreadException,
    SpreadsheetNotFound,
    NoValidUrlKeyFound,
    IncorrectCellLabel,
    WorksheetNotFound,
    CellNotFound
)


def authorize(credentials, client_class=Client):
    """Login to Google API using OAuth2 credentials.
    This is a shortcut function which
    instantiates :class:`gspread.client.Client`
    and performs login right away.

    :returns: :class:`gspread.Client` instance.
    """
    client = client_class(auth=credentials)
    client.login()
    return client
