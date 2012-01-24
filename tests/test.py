# -*- coding: utf-8 -*-

import os
import time
import hashlib
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
    """Test for gspread.client."""
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
    """Test for gspread.Spreadsheet."""
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


class WorksheetTest(GspreadTest):
    """Test for gspread.Worksheet."""
    def setUp(self):
        super(WorksheetTest, self).setUp()
        title = self.config.get('Spreadsheet', 'title')
        self.sheet = self.gc.open(title).sheet1

    def test_properties(self):
        self.assertEqual(self.sheet.id,
                         self.config.get('Worksheet', 'id'))
        self.assertEqual(self.sheet.title,
                         self.config.get('Worksheet', 'title'))
        self.assertEqual(self.sheet.row_count,
                         self.config.getint('Worksheet', 'row_count'))
        self.assertEqual(self.sheet.col_count,
                         self.config.getint('Worksheet', 'col_count'))

    def test_get_int_addr(self):
        self.assertEqual(self.sheet.get_int_addr('ABC3'), (3, 731))

    def test_acell(self):
        cell = self.sheet.acell('A1')
        self.assertTrue(isinstance(cell, gspread.Cell))

    def test_cell(self):
        cell = self.sheet.cell(1, 1)
        self.assertTrue(isinstance(cell, gspread.Cell))

    def test_range(self):
        cell_range = self.sheet.range('A1:A5')
        for c in cell_range:
            self.assertTrue(isinstance(c, gspread.Cell))

    def test_update_acell(self):
        value = hashlib.md5(str(time.time())).hexdigest()
        self.sheet.update_acell('A2', value)
        self.assertEqual(self.sheet.acell('A2').value, value)

    def test_update_cell(self):
        value = hashlib.md5(str(time.time())).hexdigest()
        self.sheet.update_cell(1, 2, value)
        self.assertEqual(self.sheet.cell(1, 2).value, value)

        self.sheet.update_cell(1, 2, 42)
        self.assertEqual(self.sheet.cell(1, 2).value, '42')

        self.sheet.update_cell(1, 2, 42L)
        self.assertEqual(self.sheet.cell(1, 2).value, '42')

        self.sheet.update_cell(1, 2, 42.01)
        self.assertEqual(self.sheet.cell(1, 2).value, '42.01')

        self.sheet.update_cell(1, 2, u'Артур')
        self.assertEqual(self.sheet.cell(1, 2).value, u'Артур')

    def test_update_cells(self):
        list_len = 10
        value_list = [hashlib.md5(str(time.time() + i)).hexdigest()
                        for i in range(list_len)]
        range_label = 'A1:A%s' % list_len
        cell_list = self.sheet.range(range_label)

        for c, v in zip(cell_list, value_list):
            c.value = v

        self.sheet.update_cells(cell_list)

        cell_list = self.sheet.range(range_label)

        for c, v in zip(cell_list, value_list):
            c.value = v
            self.assertEqual(c.value, v)

    def test_resize(self):
        init_rows = self.sheet.row_count
        init_cols = self.sheet.col_count

        self.sheet.resize(init_rows + 10, init_cols + 10)

        self.assertEqual(self.sheet.row_count, init_rows + 10)
        self.assertEqual(self.sheet.col_count, init_cols + 10)


class CellTest(GspreadTest):
    """Test for gspread.Cell."""
    def setUp(self):
        super(CellTest, self).setUp()
        title = self.config.get('Spreadsheet', 'title')
        sheet = self.gc.open(title).sheet1
        self.update_value = hashlib.md5(str(time.time())).hexdigest()
        sheet.update_acell('A1', self.update_value)
        self.cell = sheet.acell('A1')

    def test_properties(self):
        cell = self.cell
        self.assertEqual(cell.value, self.update_value)
        self.assertEqual(cell.row, 1)
        self.assertEqual(cell.col, 1)
