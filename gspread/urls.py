# -*- coding: utf-8 -*-

"""
gspread.urls
~~~~~~~~~~~~

Google API urls.

"""

SPREADSHEETS_API_V4_BASE_URL = 'https://sheets.googleapis.com/v4/spreadsheets'
SPREADSHEET_URL = SPREADSHEETS_API_V4_BASE_URL + '/%s'
SPREADSHEET_BATCH_UPDATE_URL = SPREADSHEETS_API_V4_BASE_URL + '/%s:batchUpdate'
SPREADSHEET_VALUES_URL = SPREADSHEETS_API_V4_BASE_URL + '/%s/values/%s'
SPREADSHEET_VALUES_APPEND_URL = SPREADSHEET_VALUES_URL + ':append'
SPREADSHEET_VALUES_CLEAR_URL = SPREADSHEET_VALUES_URL + ':clear'

DRIVE_FILES_API_V2_URL = 'https://www.googleapis.com/drive/v2/files'
DRIVE_FILES_UPLOAD_API_V2_URL = ('https://www.googleapis.com'
                                 '/upload/drive/v2/files')
