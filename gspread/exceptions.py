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
<<<<<<< 7e91ce60c91237a29536f0b2f609ab27a82d3d68
<<<<<<< a69cd84f789e21aa91b9c488abd3dc4ac39c8361
    def __init__(self, code, msg):
        super(HTTPError, self).__init__(msg)
        self.code = code
=======
>>>>>>> # This is a combination of 2 commits.
=======
    def __init__(self, code, msg):
        super(HTTPError, self).__init__(msg)
        self.code = code
>>>>>>> # This is a combination of 2 commits.
