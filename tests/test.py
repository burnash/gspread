# -*- coding: utf-8 -*-

import os
import re
import time
import random
import hashlib
import unittest
import ConfigParser
import itertools

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
        self.spreadsheet = self.gc.open(title)
        self.sheet = self.spreadsheet.sheet1

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
        add_num = 10

        new_rows = self.sheet.row_count + add_num
        self.sheet.add_rows(add_num)
        self.assertEqual(self.sheet.row_count, new_rows)

        new_cols = self.sheet.col_count + add_num
        self.sheet.add_cols(add_num)
        self.assertEqual(self.sheet.col_count, new_cols)

        new_rows -= add_num
        new_cols -= add_num
        self.sheet.resize(new_rows, new_cols)

        self.assertEqual(self.sheet.row_count, new_rows)
        self.assertEqual(self.sheet.col_count, new_cols)

    def test_find(self):
        sheet = self.sheet
        value = hashlib.md5(str(time.time())).hexdigest()

        sheet.update_cell(2, 10, value)
        sheet.update_cell(2, 11, value)

        cell = sheet.find(value)
        self.assertEqual(cell.value, value)

        value2 = hashlib.md5(str(time.time())).hexdigest()
        value = "%so_O%s" % (value, value2)
        sheet.update_cell(2, 11, value)

        o_O_re = re.compile('[a-z]_[A-Z]%s' % value2)

        cell = sheet.find(o_O_re)
        self.assertEqual(cell.value, value)

    def test_findall(self):
        sheet = self.sheet

        list_len = 10
        range_label = 'A1:A%s' % list_len
        cell_list = sheet.range(range_label)
        value = hashlib.md5(str(time.time())).hexdigest()

        for c in cell_list:
            c.value = value
        sheet.update_cells(cell_list)

        result_list = sheet.findall(value)

        self.assertEqual(list_len, len(result_list))

        for c in result_list:
            self.assertEqual(c.value, value)

        cell_list = sheet.range(range_label)

        value = hashlib.md5(str(time.time())).hexdigest()
        for c in cell_list:
            char = chr(random.randrange(ord('a'),ord('z')))
            c.value = "%s%s_%s%s" % (c.value, char, char.upper(), value)

        sheet.update_cells(cell_list)

        o_O_re = re.compile('[a-z]_[A-Z]%s' % value)

        result_list = sheet.findall(o_O_re)

        self.assertEqual(list_len, len(result_list))

    def test_get_all_values(self):
        # make a new, clean worksheet
        self.spreadsheet.add_worksheet('get_all_values_test', 10, 5)
        sheet = self.spreadsheet.worksheet('get_all_values_test')

        # put in new values, made from three lists
        rows = [["A1","B1", "", "D1"],
                ["", "b2", "", ""],
                ["", "", "", ""],
                ["A4", "B4", "", "D4"]]
        cell_list = sheet.range('A1:D1')
        cell_list.extend(sheet.range('A2:D2'))
        cell_list.extend(sheet.range('A3:D3'))
        cell_list.extend(sheet.range('A4:D4'))
        for cell, value in zip(cell_list, itertools.chain(*rows)):
            cell.value = value
        sheet.update_cells(cell_list)

        # read values with get_all_values, get a list of lists
        read_data = sheet.get_all_values()

        # values should match with original lists
        self.assertEqual(read_data,rows)

        # clean up newly added worksheet
        # will have to be done by hand; there is no delete worksheet method


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
