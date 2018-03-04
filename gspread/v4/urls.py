# -*- coding: utf-8 -*-

"""
gspread.v4.urls
~~~~~~~~~~~~

This module is Google API url patterns storage.

"""

SPREADSHEETS_API_V4_BASE_URL = 'https://sheets.googleapis.com/v4/spreadsheets'
SPREADSHEET_URL = SPREADSHEETS_API_V4_BASE_URL + '/%s'
SPREADSHEET_BATCH_UPDATE_URL = SPREADSHEETS_API_V4_BASE_URL + '/%s:batchUpdate'
SPREADSHEET_VALUES_URL = SPREADSHEETS_API_V4_BASE_URL + '/%s/values/%s'
SPREADSHEET_VALUES_APPEND_URL = SPREADSHEET_VALUES_URL + ':append'
SPREADSHEET_VALUES_CLEAR_URL = SPREADSHEET_VALUES_URL + ':clear'
