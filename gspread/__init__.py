# -*- coding: utf-8 -*-

"""
gspread
~~~~~~~

Google Spreadsheets client library.

"""


__version__ = '3.7.0'
__author__ = 'Anton Burnashev'


from .auth import oauth, service_account, service_account_from_dict
from .client import Client
from .models import Spreadsheet, Worksheet, Cell

from .exceptions import (
    GSpreadException,
    SpreadsheetNotFound,
    NoValidUrlKeyFound,
    IncorrectCellLabel,
    WorksheetNotFound,
    CellNotFound,
)


def authorize(credentials, client_class=Client):
    """Login to Google API using OAuth2 credentials.
    This is a shortcut function which
    instantiates `client_class`.
    By default :class:`gspread.Client` is used.

    :returns: `client_class` instance.
    """

    client = client_class(auth=credentials)
    return client
