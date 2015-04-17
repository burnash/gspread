# -*- coding: utf-8 -*-

"""
gspread.exceptions
~~~~~~~~~~~~~~~~~~

Exceptions used in gspread.

"""

class GSpreadException(Exception):
    """A base class for gspread's exceptions."""

class AuthenticationError(GSpreadException):
    """An error during authentication process."""

class SpreadsheetNotFound(GSpreadException):
    """Trying to open non-existent or inaccessible spreadsheet."""

class WorksheetNotFound(GSpreadException):
    """Trying to open non-existent or inaccessible worksheet."""

class CellNotFound(GSpreadException):
    """Cell lookup exception."""

class NoValidUrlKeyFound(GSpreadException):
    """No valid key found in URL."""

class UnsupportedFeedTypeError(GSpreadException):
    pass

class UrlParameterMissing(GSpreadException):
    pass

class IncorrectCellLabel(GSpreadException):
    """The cell label is incorrect."""

class UpdateCellError(GSpreadException):
    """Error while setting cell's value."""

class RequestError(GSpreadException):
    """Error while sending API request."""

class HTTPError(RequestError):
    """DEPRECATED. Error while sending API request."""
