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
            config_filename = os.path.join(
                os.path.dirname(__file__), creds_filename)
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

    def test_properties(self):
        self.assertEqual(self.config.get('Spreadsheet', 'id'),
                         self.spreadsheet.id)
        self.assertEqual(self.config.get('Spreadsheet', 'title'),
                         self.spreadsheet.title)

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

    def test_get_addr_int(self):
        self.assertEqual(self.sheet.get_addr_int(3, 731), 'ABC3')
        self.assertEqual(self.sheet.get_addr_int(1, 104),'CZ1')

    def test_addr_converters(self):
        for row in range(1, 257):
            for col in range(1, 512):
                addr = self.sheet.get_addr_int(row, col)
                (r, c) = self.sheet.get_int_addr(addr)
                self.assertEqual((row, col), (r, c))

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

        self.sheet.update_cell(1, 2, 42)
        self.assertEqual(self.sheet.cell(1, 2).value, '42')

        self.sheet.update_cell(1, 2, 42.01)
        self.assertEqual(self.sheet.cell(1, 2).value, '42.01')

        self.sheet.update_cell(1, 2, u'Артур')
        self.assertEqual(self.sheet.cell(1, 2).value, u'Артур')

    def test_update_cell_multiline(self):
        value = hashlib.md5(str(time.time())).hexdigest()
        value = "%s\n%s" % (value, value)
        self.sheet.update_cell(1, 2, value)
        self.assertEqual(self.sheet.cell(1, 2).value, value)

    def test_update_cells(self):
        list_len = 10
        value_list = [hashlib.md5(str(time.time() + i)).hexdigest()
                      for i in range(list_len)]
        # Test multiline
        value_list[0] = "%s\n%s" % (value_list[0], value_list[0])

        range_label = 'A1:A%s' % list_len
        cell_list = self.sheet.range(range_label)

        for c, v in zip(cell_list, value_list):
            c.value = v

        self.sheet.update_cells(cell_list)

        cell_list = self.sheet.range(range_label)

        for c, v in zip(cell_list, value_list):
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
            char = chr(random.randrange(ord('a'), ord('z')))
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
        rows = [["A1", "B1", "", "D1"],
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
        self.assertEqual(read_data, rows)

        # clean up newly added worksheet
        # will have to be done by hand; there is no delete worksheet method

    def test_get_all_records(self):
        # make a new, clean worksheet
        # same as for test_all_values, find a way to refactor it
        self.spreadsheet.add_worksheet('get_all_values_test', 10, 5)
        sheet = self.spreadsheet.worksheet('get_all_values_test')

        # put in new values, made from three lists
        rows = [["A1", "B1", "", "D1"],
                [1, "b2", 1.45, ""],
                ["", "", "", ""],
                ["A4", 0.4, "", 4]]
        cell_list = sheet.range('A1:D1')
        cell_list.extend(sheet.range('A2:D2'))
        cell_list.extend(sheet.range('A3:D3'))
        cell_list.extend(sheet.range('A4:D4'))
        for cell, value in zip(cell_list, itertools.chain(*rows)):
            cell.value = value
        sheet.update_cells(cell_list)

        # first, read empty strings to empty strings
        read_records = sheet.get_all_records()
        d0 = dict(zip(rows[0], rows[1]))
        d1 = dict(zip(rows[0], rows[2]))
        d2 = dict(zip(rows[0], rows[3]))
        self.assertEqual(read_records[0], d0)
        self.assertEqual(read_records[1], d1)
        self.assertEqual(read_records[2], d2)

        # then, read empty strings to zeros
        read_records = sheet.get_all_records(empty2zero=True)
        d1 = dict(zip(rows[0], (0, 0, 0, 0)))
        self.assertEqual(read_records[1], d1)

    def test_get_all_records_different_header(self):
        # make a new, clean worksheet
        # same as for test_all_values, find a way to refactor it
        self.spreadsheet.add_worksheet('get_all_records', 10, 5)
        sheet = self.spreadsheet.worksheet('get_all_records')

        # put in new values, made from three lists
        rows = [["", "", "", ""],
                ["", "", "", ""],
                ["A1", "B1", "", "D1"],
                [1, "b2", 1.45, ""],
                ["", "", "", ""],
                ["A4", 0.4, "", 4]]
        cell_list = sheet.range('A1:D1')
        cell_list.extend(sheet.range('A2:D2'))
        cell_list.extend(sheet.range('A3:D3'))
        cell_list.extend(sheet.range('A4:D4'))
        cell_list.extend(sheet.range('A5:D5'))
        cell_list.extend(sheet.range('A6:D6'))
        for cell, value in zip(cell_list, itertools.chain(*rows)):
            cell.value = value
        sheet.update_cells(cell_list)

        # first, read empty strings to empty strings
        read_records = sheet.get_all_records(head=3)
        d0 = dict(zip(rows[2], rows[3]))
        d1 = dict(zip(rows[2], rows[4]))
        d2 = dict(zip(rows[2], rows[5]))
        self.assertEqual(read_records[0], d0)
        self.assertEqual(read_records[1], d1)
        self.assertEqual(read_records[2], d2)

        # then, read empty strings to zeros
        read_records = sheet.get_all_records(empty2zero=True, head=3)
        d1 = dict(zip(rows[2], (0, 0, 0, 0)))
        self.assertEqual(read_records[1], d1)

        self.gc.del_worksheet(sheet)

    def test_append_row(self):
        num_rows = self.sheet.row_count
        num_cols = self.sheet.col_count
        values = ['o_0'] * (num_cols + 4)
        self.sheet.append_row(values)
        self.assertEqual(self.sheet.row_count, num_rows + 1)
        self.assertEqual(self.sheet.col_count, num_cols + 4)
        read_values = self.sheet.row_values(self.sheet.row_count)
        self.assertEqual(values, read_values)

        # undo the appending and resizing
        self.sheet.resize(num_rows, num_cols)

    def test_insert_row(self):
        num_rows = self.sheet.row_count
        num_cols = self.sheet.col_count
        values = ['o_0'] * (num_cols + 4)
        self.sheet.insert_row(values, 1)
        self.assertEqual(self.sheet.row_count, num_rows + 1)
        self.assertEqual(self.sheet.col_count, num_cols + 4)
        read_values = self.sheet.row_values(1)
        self.assertEqual(values, read_values)

        # undo the appending and resizing
        # self.sheet.resize(num_rows, num_cols)

    def test_export(self):
        list_len = 10
        time_md5 = hashlib.md5(str(time.time())).hexdigest()
        wks_name = 'export_test_%s' % time_md5

        self.spreadsheet.add_worksheet(wks_name, list_len, 5)
        sheet = self.spreadsheet.worksheet(wks_name)

        value_list = [hashlib.md5(str(time.time() + i)).hexdigest()
                      for i in range(list_len)]

        range_label = 'A1:A%s' % list_len
        cell_list = sheet.range(range_label)

        for c, v in zip(cell_list, value_list):
            c.value = v

        sheet.update_cells(cell_list)

        exported_data = sheet.export(format='csv').read()

        csv_value = '\n'.join(value_list)

        self.assertEqual(exported_data, csv_value)

class WorksheetDeleteTest(GspreadTest):

    def setUp(self):
        super(WorksheetDeleteTest, self).setUp()
        title = self.config.get('Spreadsheet', 'title')
        self.spreadsheet = self.gc.open(title)
        ws1_name = self.config.get('WorksheetDelete', 'ws1_name')
        ws2_name = self.config.get('WorksheetDelete', 'ws2_name')
        self.ws1 = self.spreadsheet.add_worksheet(ws1_name, 1, 1)
        self.ws2 = self.spreadsheet.add_worksheet(ws2_name, 1, 1)

    def test_delete_multiple_worksheets(self):
        self.spreadsheet.del_worksheet(self.ws1)
        self.spreadsheet.del_worksheet(self.ws2)


class CellTest(GspreadTest):
    """Test for gspread.Cell."""

    def setUp(self):
        super(CellTest, self).setUp()
        title = self.config.get('Spreadsheet', 'title')
        sheet = self.gc.open(title).sheet1
        self.sheet = sheet

    def test_properties(self):
        update_value = hashlib.md5(str(time.time())).hexdigest()
        self.sheet.update_acell('A1', update_value)
        cell = self.sheet.acell('A1')
        self.assertEqual(cell.value, update_value)
        self.assertEqual(cell.row, 1)
        self.assertEqual(cell.col, 1)

    def test_numeric_value(self):
        numeric_value = 1.0 / 1024
        # Use a formula here to avoid issues with differing decimal marks:
        self.sheet.update_acell('A1', '= 1 / 1024')
        cell = self.sheet.acell('A1')
        self.assertEqual(cell.numeric_value, numeric_value)
        self.assertIsInstance(cell.numeric_value, float)
        self.sheet.update_acell('A1', 'Non-numeric value')
        cell = self.sheet.acell('A1')
        self.assertIs(cell.numeric_value, None)
