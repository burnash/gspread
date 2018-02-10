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

class ImportException(GSpreadException):
    """An error during import."""

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


class APIError(GSpreadException):
    def __init__(self, response):

        super(APIError, self).__init__(self._extract_text(response))
        self.response = response

    def _extract_text(self, response):
        return self._text_from_detail(response) or response.text

    def _text_from_detail(self, response):
        try:
            errors = response.json()
            return errors['detail']
        except (AttributeError, KeyError, ValueError):
            return None
