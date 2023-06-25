"""
gspread.exceptions
~~~~~~~~~~~~~~~~~~

Exceptions used in gspread.

"""

from typing import Dict, Optional, Union

from requests import Response


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
    def __init__(self, response: Response):
        super().__init__(self._extract_text(response))
        self.response: Response = response

    def _extract_text(
        self, response: Response
    ) -> Union[Dict[str, Union[int, str]], str]:
        return self._text_from_detail(response) or response.text

    def _text_from_detail(
        self, response: Response
    ) -> Optional[Dict[str, Union[int, str]]]:
        try:
            errors = response.json()
            return dict(errors["error"])
        except (AttributeError, KeyError, ValueError):
            return None
