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

class NoValidUrlKeyFound(GSpreadException):
    """No valid key found in URL."""

class UnsupportedFeedTypeError(GSpreadException):
    pass

class UrlParameterMissing(GSpreadException):
    pass

class IncorrectCellLabel(GSpreadException):
    """The cell label is incorrect."""
