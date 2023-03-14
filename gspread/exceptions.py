"""
gspread.exceptions
~~~~~~~~~~~~~~~~~~

Exceptions used in gspread.

"""


class UnSupportedExportFormat(Exception):
    """Raised when export format is not supported."""


class GSpreadException(Exception):
    """A base class for gspread's exceptions."""


class SpreadsheetNotFound(GSpreadException):
    """Trying to open non-existent or inaccessible spreadsheet."""


class WorksheetNotFound(GSpreadException):
    """Trying to open non-existent or inaccessible worksheet."""


class CellNotFound(GSpreadException):
    """Cell lookup exception."""


class NoValidUrlKeyFound(GSpreadException):
    """No valid key found in URL."""


class IncorrectCellLabel(GSpreadException):
    """The cell label is incorrect."""


class InvalidInputValue(GSpreadException):
    """The provided values is incorrect."""


class APIError(GSpreadException):
    def __init__(self, response):
        super().__init__(self._extract_text(response))
        self.response = response

    def _extract_text(self, response):
        return self._text_from_detail(response) or response.text

    def _text_from_detail(self, response):
        try:
            errors = response.json()
            return errors["error"]
        except (AttributeError, KeyError, ValueError):
            return None
