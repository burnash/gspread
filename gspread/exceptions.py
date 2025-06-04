"""
gspread.exceptions
~~~~~~~~~~~~~~~~~~

Exceptions used in gspread.

"""

from typing import Any, Mapping

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
        try:
            error = response.json()["error"]
        except Exception as e:
            # in case we failed to parse the error from the API
            # build an empty error object to notify the caller
            # and keep the exception raise flow running

            error = {
                "code": -1,
                "message": response.text,
                "status": "invalid JSON: '{}'".format(e),
            }

        super().__init__(error)
        self.response: Response = response
        self.error: Mapping[str, Any] = error
        self.code: int = self.error["code"]

    def __str__(self) -> str:
        return "{}: [{}]: {}".format(
            self.__class__.__name__, self.code, self.error["message"]
        )

    def __repr__(self) -> str:
        return self.__str__()

    def __reduce__(self) -> tuple:
        return self.__class__, (self.response,)


class SpreadsheetNotFound(GSpreadException):
    """Trying to open non-existent or inaccessible spreadsheet."""
