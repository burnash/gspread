# flake8: noqa

"""
gspread
~~~~~~~

Google Spreadsheets client library.

"""


__version__ = "5.4.0"
__author__ = "Anton Burnashev"


from .auth import oauth, oauth_from_dict, service_account, service_account_from_dict
from .cell import Cell
from .client import BackoffClient, Client, ClientFactory
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


def authorize(credentials, client_factory=Client):
    """Login to Google API using OAuth2 credentials.
    This is a shortcut function which
    instantiates using `client_factory`.
    By default :class:`gspread.Client` is used (but could also use
    :class:`gspread.BackoffClient` to avoid rate limiting).

    :returns: `client_class` instance.
    """

    client = client_factory(auth=credentials)
    return client
