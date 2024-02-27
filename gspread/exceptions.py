"""
gspread.exceptions
~~~~~~~~~~~~~~~~~~

Exceptions used in gspread.

"""

from typing import Any, Dict, Mapping, Optional, Union

from requests import Response


class UnSupportedExportFormat(Exception):
    """Raised when export format is not supported."""


class GSpreadException(Exception):
    """A base class for gspread's exceptions."""


class WorksheetNotFound(GSpreadException):
    """Trying to open non-existent or inaccessible worksheet."""


class NoValidUrlKeyFound(GSpreadException):
    """No valid key found in URL."""


class IncorrectCellLabel(GSpreadException):
    """The cell label is incorrect."""


class InvalidInputValue(GSpreadException):
    """The provided values is incorrect."""


class APIError(GSpreadException):
    """Errors coming from the API itself,
    such as when we attempt to retrieve things that don't exist."""

    def __init__(self, response: Response):
        super().__init__(self._extract_error(response))
        self.response: Response = response
        self.error: Mapping[str, Any] = response.json()["error"]
        self.code: int = self.error["code"]

    def _extract_error(
        self, response: Response
    ) -> Optional[Dict[str, Union[int, str]]]:
        try:
            errors = response.json()
            return dict(errors["error"])
        except (AttributeError, KeyError, ValueError):
            return None

    def __str__(self) -> str:
        return "{}: [{}]: {}".format(
            self.__class__.__name__, self.code, self.error["message"]
        )

    def __repr__(self) -> str:
        return self.__str__()


class SpreadsheetNotFound(GSpreadException):
    """Trying to open non-existent or inaccessible spreadsheet."""
