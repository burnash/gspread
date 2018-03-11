# -*- coding: utf-8 -*-

"""
gspread.v4.exceptions
~~~~~~~~~~~~~~~~~~

Exceptions used in gspread.

"""


class GSpreadException(Exception):
    """A base class for gspread's exceptions."""


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
