# flake8: noqa

"""
gspread
~~~~~~~

Google Spreadsheets client library.

"""


__version__ = "5.0.0"
__author__ = "Anton Burnashev"


from .auth import oauth, service_account, service_account_from_dict
from .cell import Cell
from .client import Client
from .exceptions import (
    CellNotFound,
    GSpreadException,
    IncorrectCellLabel,
    NoValidUrlKeyFound,
    SpreadsheetNotFound,
    WorksheetNotFound,
)
from .spreadsheet import Spreadsheet
from .worksheet import Worksheet


def authorize(credentials, client_class=Client):
    """Login to Google API using OAuth2 credentials.
    This is a shortcut function which
    instantiates `client_class`.
    By default :class:`gspread.Client` is used.

    :returns: `client_class` instance.
    """

    client = client_class(auth=credentials)
    return client
