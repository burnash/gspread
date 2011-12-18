import os
import unittest
import ConfigParser

import gspread

class GspreadTest(unittest.TestCase):

    def setUp(self):
        creds_filename = "tests.config"
        try:
            config_filename = os.path.join(os.path.dirname(__file__), creds_filename)
            config = ConfigParser.ConfigParser()
            config.readfp(open(config_filename))
            email = config.get('Google Account', 'email')
            password = config.get('Google Account', 'password')
            self.config = config
            self.gc = gspread.login(email, password)

            self.assertTrue(isinstance(self.gc, gspread.Client))
        except IOError:
            msg = "Can't find %s for reading google account credentials. " \
                  "You can create it from %s.example in tests/ directory."
            raise Exception(msg % (creds_filename, creds_filename))


class ClientTest(GspreadTest):
    """Test for gspread.client"""
    def test_open(self):
        title = self.config.get('Spreadsheet', 'title')
        spreadsheet = self.gc.open(title)
        self.assertTrue(isinstance(spreadsheet, gspread.Spreadsheet))

    def test_no_found_exeption(self):
        noexistent_title = "Please don't use this phrase as a name of a sheet."
        self.assertRaises(gspread.SpreadsheetNotFound,
                          self.gc.open,
                          noexistent_title)

    def test_open_by_key(self):
        key = self.config.get('Spreadsheet', 'key')
        spreadsheet = self.gc.open_by_key(key)
        self.assertTrue(isinstance(spreadsheet, gspread.Spreadsheet))

    def test_open_by_url(self):
        url = self.config.get('Spreadsheet', 'url')
        spreadsheet = self.gc.open_by_url(url)
        self.assertTrue(isinstance(spreadsheet, gspread.Spreadsheet))

    def test_openall(self):
        spreadsheet_list = self.gc.openall()
        for s in spreadsheet_list:
            self.assertTrue(isinstance(s, gspread.Spreadsheet))


class SpreadsheetTest(GspreadTest):
    """Test for gspread.Spreadsheet"""
    def setUp(self):
        super(SpreadsheetTest, self).setUp()
        title = self.config.get('Spreadsheet', 'title')
        self.spreadsheet = self.gc.open(title)

    def test_sheet1(self):
        sheet1 = self.spreadsheet.sheet1
        self.assertTrue(isinstance(sheet1, gspread.Worksheet))

    def test_get_worksheet(self):
        sheet1 = self.spreadsheet.get_worksheet(0)
        self.assertTrue(isinstance(sheet1, gspread.Worksheet))

    def test_worksheet(self):
        sheet_title = self.config.get('Spreadsheet', 'sheet1_title')
        sheet = self.spreadsheet.worksheet(sheet_title)
        self.assertTrue(isinstance(sheet, gspread.Worksheet))

