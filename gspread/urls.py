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
SPREADSHEET_VALUES_BATCH_URL = SPREADSHEETS_API_V4_BASE_URL + '/%s/values:batchGet'
SPREADSHEET_VALUES_BATCH_UPDATE_URL = SPREADSHEETS_API_V4_BASE_URL + '/%s/values:batchUpdate'
SPREADSHEET_VALUES_BATCH_CLEAR_URL = SPREADSHEETS_API_V4_BASE_URL + '/%s/values:batchClear'
SPREADSHEET_VALUES_APPEND_URL = SPREADSHEET_VALUES_URL + ':append'
SPREADSHEET_VALUES_CLEAR_URL = SPREADSHEET_VALUES_URL + ':clear'
SPREADSHEET_SHEETS_COPY_TO_URL = SPREADSHEET_URL + '/sheets/%s:copyTo'

DRIVE_FILES_API_V2_URL = 'https://www.googleapis.com/drive/v2/files'
DRIVE_FILES_API_V3_URL = "https://www.googleapis.com/drive/v3/files"
DRIVE_FILES_UPLOAD_API_V2_URL = ('https://www.googleapis.com'
                                 '/upload/drive/v2/files')

SPREADSHEET_DRIVE_URL = "https://docs.google.com/spreadsheets/d/%s"
WORKSHEET_DRIVE_URL = SPREADSHEET_URL + "#gid=%s"
