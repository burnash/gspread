# -*- coding: utf-8 -*-

import os
import re
import random
import unittest
import itertools
import uuid

try:
    import ConfigParser
except ImportError:
    import configparser as ConfigParser

from oauth2client.service_account import ServiceAccountCredentials

import gspread
from gspread import utils

try:
    unicode
except NameError:
    basestring = unicode = str


CONFIG_FILENAME = os.path.join(os.path.dirname(__file__), 'tests.config')
CREDS_FILENAME = os.path.join(os.path.dirname(__file__), 'creds.json')
SCOPE = [
    'https://spreadsheets.google.com/feeds',
    'https://www.googleapis.com/auth/drive.file'
]

I18N_STR = u'Iñtërnâtiônàlizætiøn'  # .encode('utf8')


def read_config(filename):
    config = ConfigParser.ConfigParser()
    config.readfp(open(filename))
    return config


def read_credentials(filename):
    return ServiceAccountCredentials.from_json_keyfile_name(filename, SCOPE)


def gen_value(prefix=None):
    if prefix:
        return u'%s %s' % (prefix, gen_value())
    else:
        return unicode(uuid.uuid4())


def prefixed_counter(prefix, start=1):
    c = itertools.count(start)
    for value in c:
        yield u'%s %s' % (prefix, value)


def get_method_name(self_id):
    return self_id.split('.')[-1]


class UtilsTest(unittest.TestCase):

    def test_extract_id_from_url(self):
        url_id_list = [
            # New-style url
            ('https://docs.google.com/spreadsheets/d/'
             '1qpyC0X3A0MwQoFDE8p-Bll4hps/edit#gid=0',
             '1qpyC0X3A0MwQoFDE8p-Bll4hps'),

            ('https://docs.google.com/spreadsheets/d/'
             '1qpyC0X3A0MwQoFDE8p-Bll4hps/edit',
             '1qpyC0X3A0MwQoFDE8p-Bll4hps'),

            ('https://docs.google.com/spreadsheets/d/'
             '1qpyC0X3A0MwQoFDE8p-Bll4hps',
             '1qpyC0X3A0MwQoFDE8p-Bll4hps'),

            # Old-style url
            ('https://docs.google.com/spreadsheet/'
             'ccc?key=1qpyC0X3A0MwQoFDE8p-Bll4hps&usp=drive_web#gid=0',
             '1qpyC0X3A0MwQoFDE8p-Bll4hps')
        ]

        for url, id in url_id_list:
            self.assertEqual(id, utils.extract_id_from_url(url))

    def test_no_extract_id_from_url(self):
        self.assertRaises(
            gspread.NoValidUrlKeyFound,
            utils.extract_id_from_url,
            'http://example.org'
        )

    def test_a1_to_rowcol(self):
        self.assertEqual(utils.a1_to_rowcol('ABC3'), (3, 731))

    def test_rowcol_to_a1(self):
        self.assertEqual(utils.rowcol_to_a1(3, 731), 'ABC3')
        self.assertEqual(utils.rowcol_to_a1(1, 104), 'CZ1')

    def test_addr_converters(self):
        for row in range(1, 257):
            for col in range(1, 512):
                addr = utils.rowcol_to_a1(row, col)
                (r, c) = utils.a1_to_rowcol(addr)
                self.assertEqual((row, col), (r, c))

    def test_get_gid(self):
        gid = 'od6'
        self.assertEqual(utils.wid_to_gid(gid), '0')
        gid = 'osyqnsz'
        self.assertEqual(utils.wid_to_gid(gid), '1751403737')
        gid = 'ogsrar0'
        self.assertEqual(utils.wid_to_gid(gid), '1015761654')


class GspreadTest(unittest.TestCase):
    def _sequence_generator(self):
        return prefixed_counter(get_method_name(self.id()))

    @classmethod
    def setUpClass(cls):
        try:
            cls.config = read_config(CONFIG_FILENAME)
            credentials = read_credentials(CREDS_FILENAME)
            cls.gc = gspread.authorize(credentials)
        except IOError as e:
            msg = "Can't find %s for reading test configuration. "
            raise Exception(msg % e.filename)


class ClientTest(GspreadTest):

    """Test for gspread.client."""

    def test_open(self):
        title = self.config.get('Spreadsheet', 'title')
        spreadsheet = self.gc.open(title)
        self.assertTrue(isinstance(spreadsheet, gspread.models.Spreadsheet))

    def test_no_found_exeption(self):
        noexistent_title = "Please don't use this phrase as a name of a sheet."
        self.assertRaises(gspread.SpreadsheetNotFound,
                          self.gc.open,
                          noexistent_title)

    def test_open_by_key(self):
        key = self.config.get('Spreadsheet', 'key')
        spreadsheet = self.gc.open_by_key(key)
        self.assertTrue(isinstance(spreadsheet, gspread.models.Spreadsheet))

    def test_open_by_url(self):
        url = self.config.get('Spreadsheet', 'url')
        spreadsheet = self.gc.open_by_url(url)
        self.assertTrue(isinstance(spreadsheet, gspread.models.Spreadsheet))

    def test_openall(self):
        spreadsheet_list = self.gc.openall()
        for s in spreadsheet_list:
            self.assertTrue(isinstance(s, gspread.models.Spreadsheet))

    def test_create(self):
        title = 'Test Spreadsheet'
        new_spreadsheet = self.gc.create(title)
        self.assertTrue(
            isinstance(new_spreadsheet, gspread.models.Spreadsheet))

    def test_import_csv(self):
        title = 'TestImportSpreadsheet'
        new_spreadsheet = self.gc.create(title)

        sg = self._sequence_generator()

        csv_rows = 4
        csv_cols = 4

        rows = [[
            next(sg)
            for j in range(csv_cols)]
            for i in range(csv_rows)
        ]

        simple_csv_data = '\n'.join([','.join(row) for row in rows])

        self.gc.import_csv(new_spreadsheet.id, simple_csv_data)

        sh = self.gc.open_by_key(new_spreadsheet.id)
        self.assertEqual(sh.sheet1.get_all_values(), rows)

        self.gc.del_spreadsheet(new_spreadsheet.id)


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

    def test_worksheet_iteration(self):
        self.assertEqual(
            [x.id for x in self.spreadsheet.worksheets()],
            [sheet.id for sheet in self.spreadsheet]
        )


class WorksheetTest(GspreadTest):

    """Test for gspread.Worksheet."""

    @classmethod
    def setUpClass(cls):
        super(WorksheetTest, cls).setUpClass()
        title = cls.config.get('Spreadsheet', 'title')
        cls.spreadsheet = cls.gc.open(title)

    def setUp(self):
        super(WorksheetTest, self).setUp()
        title = self.config.get('Spreadsheet', 'title')
        self.spreadsheet = self.gc.open(title)

        # NOTE(msuozzo): Here, a new worksheet is created for each test.
        # This was determined to be faster than reusing a single sheet and
        # having to clear its contents after each test.
        # Basically: Time(add_wks + del_wks) < Time(range + update_cells)
        self.sheet = self.spreadsheet.add_worksheet('wksht_test', 20, 20)

    def tearDown(self):
        self.spreadsheet.del_worksheet(self.sheet)
        super(WorksheetTest, self).tearDown()

    def test_acell(self):
        cell = self.sheet.acell('A1')
        self.assertTrue(isinstance(cell, gspread.models.Cell))

    def test_cell(self):
        cell = self.sheet.cell(1, 1)
        self.assertTrue(isinstance(cell, gspread.models.Cell))

    def test_range(self):
        cell_range1 = self.sheet.range('A1:A5')
        cell_range2 = self.sheet.range(1, 1, 5, 1)
        for c1, c2 in zip(cell_range1, cell_range2):
            self.assertTrue(isinstance(c1, gspread.models.Cell))
            self.assertTrue(isinstance(c2, gspread.models.Cell))
            self.assertTrue(c1.col == c2.col)
            self.assertTrue(c1.row == c2.row)
            self.assertTrue(c1.value == c2.value)

    def test_update_acell(self):
        sg = self._sequence_generator()
        value = next(sg)

        self.sheet.update_acell('A2', value)
        self.assertEqual(self.sheet.acell('A2').value, value)

    def test_update_cell(self):
        sg = self._sequence_generator()
        value = next(sg)

        self.sheet.update_cell(1, 2, value)
        self.assertEqual(self.sheet.cell(1, 2).value, value)

        self.sheet.update_cell(1, 2, 42)
        self.assertEqual(self.sheet.cell(1, 2).value, '42')

        self.sheet.update_cell(1, 2, '0042')
        self.assertEqual(self.sheet.cell(1, 2).value, '42')

        self.sheet.update_cell(1, 2, 42.01)
        self.assertEqual(self.sheet.cell(1, 2).value, '42.01')

        self.sheet.update_cell(1, 2, u'Артур')
        self.assertEqual(self.sheet.cell(1, 2).value, u'Артур')

    def test_update_cell_multiline(self):
        sg = self._sequence_generator()
        value = next(sg)

        value = "%s\n%s" % (value, value)
        self.sheet.update_cell(1, 2, value)
        self.assertEqual(self.sheet.cell(1, 2).value, value)

    def test_update_cell_unicode(self):
        self.sheet.update_cell(1, 1, I18N_STR)

        cell = self.sheet.cell(1, 1)
        self.assertEqual(cell.value, I18N_STR)

    def test_update_cells(self):
        sg = self._sequence_generator()

        list_len = 10
        value_list = [next(sg) for i in range(list_len)]

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

    def test_update_cells_unicode(self):
        cell = self.sheet.cell(1, 1)
        cell.value = I18N_STR
        self.sheet.update_cells([cell])

        cell = self.sheet.cell(1, 1)
        self.assertEqual(cell.value, I18N_STR)

    def test_update_cells_noncontiguous(self):
        sg = self._sequence_generator()

        num_rows = 6
        num_cols = 4

        rows = [[
            next(sg)
            for j in range(num_cols)]
            for i in range(num_rows)
        ]

        cell_list = self.sheet.range('A1:D6')
        for cell, value in zip(cell_list, itertools.chain(*rows)):
            cell.value = value
        self.sheet.update_cells(cell_list)

        # Re-fetch cells
        cell_list = self.sheet.range('A1:D6')
        test_values = [c.value for c in cell_list]

        top_left = cell_list[0]
        bottom_right = cell_list[-1]

        top_left.value = top_left_value = next(sg) + ' top_left'
        bottom_right.value = bottom_right_value = next(sg) + ' bottom_right'

        self.sheet.update_cells([top_left, bottom_right])

        cell_list = self.sheet.range('A1:D6')
        read_values = [c.value for c in cell_list]
        test_values[0] = top_left_value
        test_values[-1] = bottom_right_value
        self.assertEqual(test_values, read_values)

    def test_resize(self):
        add_num = 10
        new_rows = self.sheet.row_count + add_num

        def get_grid_props():
            sheets = self.sheet.spreadsheet.fetch_sheet_metadata()['sheets']
            return utils.finditem(
                lambda x: x['properties']['sheetId'] == self.sheet.id, sheets
            )['properties']['gridProperties']

        self.sheet.add_rows(add_num)

        grid_props = get_grid_props()

        self.assertEqual(grid_props['rowCount'], new_rows)

        new_cols = self.sheet.col_count + add_num

        self.sheet.add_cols(add_num)

        grid_props = get_grid_props()

        self.assertEqual(grid_props['columnCount'], new_cols)

        new_rows -= add_num
        new_cols -= add_num
        self.sheet.resize(new_rows, new_cols)

        grid_props = get_grid_props()

        self.assertEqual(grid_props['rowCount'], new_rows)
        self.assertEqual(grid_props['columnCount'], new_cols)

    def test_find(self):
        sg = self._sequence_generator()
        value = next(sg)

        self.sheet.update_cell(2, 10, value)
        self.sheet.update_cell(2, 11, value)

        cell = self.sheet.find(value)
        self.assertEqual(cell.value, value)

        value2 = next(sg)
        value = "%so_O%s" % (value, value2)
        self.sheet.update_cell(2, 11, value)

        o_O_re = re.compile('[a-z]_[A-Z]%s' % value2)

        cell = self.sheet.find(o_O_re)
        self.assertEqual(cell.value, value)

    def test_findall(self):
        list_len = 10
        range_label = 'A1:A%s' % list_len
        cell_list = self.sheet.range(range_label)

        sg = self._sequence_generator()

        value = next(sg)

        for c in cell_list:
            c.value = value
        self.sheet.update_cells(cell_list)

        result_list = self.sheet.findall(value)

        self.assertEqual(list_len, len(result_list))

        for c in result_list:
            self.assertEqual(c.value, value)

        cell_list = self.sheet.range(range_label)

        value = next(sg)
        for c in cell_list:
            char = chr(random.randrange(ord('a'), ord('z')))
            c.value = "%s%s_%s%s" % (c.value, char, char.upper(), value)

        self.sheet.update_cells(cell_list)

        o_O_re = re.compile('[a-z]_[A-Z]%s' % value)

        result_list = self.sheet.findall(o_O_re)

        self.assertEqual(list_len, len(result_list))

    def test_get_all_values(self):
        self.sheet.resize(4, 4)
        # put in new values, made from three lists
        rows = [["A1", "B1", "", "D1"],
                ["", "b2", "", ""],
                ["", "", "", ""],
                ["A4", "B4", "", "D4"]]
        cell_list = self.sheet.range('A1:D1')

        cell_list.extend(self.sheet.range('A2:D2'))
        cell_list.extend(self.sheet.range('A3:D3'))
        cell_list.extend(self.sheet.range('A4:D4'))
        for cell, value in zip(cell_list, itertools.chain(*rows)):
            cell.value = value
        self.sheet.update_cells(cell_list)

        # read values with get_all_values, get a list of lists
        read_data = self.sheet.get_all_values()
        # values should match with original lists
        self.assertEqual(read_data, rows)

    def test_get_all_records(self):
        self.sheet.resize(4, 4)
        # put in new values, made from three lists
        rows = [["A1", "B1", "", "D1"],
                [1, "b2", 1.45, ""],
                ["", "", "", ""],
                ["A4", 0.4, "", 4]]
        cell_list = self.sheet.range('A1:D4')
        for cell, value in zip(cell_list, itertools.chain(*rows)):
            cell.value = value
        self.sheet.update_cells(cell_list)

        # first, read empty strings to empty strings
        read_records = self.sheet.get_all_records()
        d0 = dict(zip(rows[0], rows[1]))
        d1 = dict(zip(rows[0], rows[2]))
        d2 = dict(zip(rows[0], rows[3]))
        self.assertEqual(read_records[0], d0)
        self.assertEqual(read_records[1], d1)
        self.assertEqual(read_records[2], d2)

        # then, read empty strings to zeros
        read_records = self.sheet.get_all_records(empty2zero=True)
        d1 = dict(zip(rows[0], (0, 0, 0, 0)))
        self.assertEqual(read_records[1], d1)

        # then, read empty strings to None
        read_records = self.sheet.get_all_records(default_blank=None)
        d1 = dict(zip(rows[0], (None, None, None, None)))
        self.assertEqual(read_records[1], d1)

        # then, read empty strings to something else
        read_records = self.sheet.get_all_records(default_blank='foo')
        d1 = dict(zip(rows[0], ('foo', 'foo', 'foo', 'foo')))
        self.assertEqual(read_records[1], d1)

    def test_get_all_records_different_header(self):
        self.sheet.resize(6, 4)
        # put in new values, made from three lists
        rows = [["", "", "", ""],
                ["", "", "", ""],
                ["A1", "B1", "", "D1"],
                [1, "b2", 1.45, ""],
                ["", "", "", ""],
                ["A4", 0.4, "", 4]]
        cell_list = self.sheet.range('A1:D6')
        for cell, value in zip(cell_list, itertools.chain(*rows)):
            cell.value = value
        self.sheet.update_cells(cell_list)

        # first, read empty strings to empty strings
        read_records = self.sheet.get_all_records(head=3)
        d0 = dict(zip(rows[2], rows[3]))
        d1 = dict(zip(rows[2], rows[4]))
        d2 = dict(zip(rows[2], rows[5]))
        self.assertEqual(read_records[0], d0)
        self.assertEqual(read_records[1], d1)
        self.assertEqual(read_records[2], d2)

        # then, read empty strings to zeros
        read_records = self.sheet.get_all_records(empty2zero=True, head=3)
        d1 = dict(zip(rows[2], (0, 0, 0, 0)))
        self.assertEqual(read_records[1], d1)

        # then, read empty strings to None
        read_records = self.sheet.get_all_records(default_blank=None, head=3)
        d1 = dict(zip(rows[2], (None, None, None, None)))
        self.assertEqual(read_records[1], d1)

        # then, read empty strings to something else
        read_records = self.sheet.get_all_records(default_blank='foo', head=3)
        d1 = dict(zip(rows[2], ('foo', 'foo', 'foo', 'foo')))
        self.assertEqual(read_records[1], d1)

    def test_append_row(self):
        sg = self._sequence_generator()
        value_list = [next(sg) for i in range(10)]
        self.sheet.append_row(value_list)
        read_values = self.sheet.row_values(1)
        self.assertEqual(value_list, read_values)

    def test_insert_row(self):
        sg = self._sequence_generator()

        num_rows = 6
        num_cols = 4

        rows = [[
            next(sg)
            for j in range(num_cols)]
            for i in range(num_rows)
        ]

        cell_list = self.sheet.range('A1:D6')
        for cell, value in zip(cell_list, itertools.chain(*rows)):
            cell.value = value
        self.sheet.update_cells(cell_list)

        new_row_values = [next(sg) for i in range(num_cols + 4)]
        self.sheet.insert_row(new_row_values, 2)
        read_values = self.sheet.row_values(2)
        self.assertEqual(new_row_values, read_values)

        formula = '=1+1'
        self.sheet.update_acell('B2', formula)
        values = [next(sg) for i in range(num_cols + 4)]
        self.sheet.insert_row(values, 1)
        b3 = self.sheet.acell('B3', value_render_option='FORMULA')
        self.assertEqual(b3.value, formula)

    def test_delete_row(self):
        sg = self._sequence_generator()

        for i in range(5):
            value_list = [next(sg) for i in range(10)]
            self.sheet.append_row(value_list)

        prev_row = self.sheet.row_values(1)
        next_row = self.sheet.row_values(3)
        self.sheet.delete_row(2)
        self.assertEqual(self.sheet.row_values(1), prev_row)
        self.assertEqual(self.sheet.row_values(2), next_row)

    def test_clear(self):
        rows = [["", "", "", ""],
                ["", "", "", ""],
                ["A1", "B1", "", "D1"],
                [1, "b2", 1.45, ""],
                ["", "", "", ""],
                ["A4", 0.4, "", 4]]

        cell_list = self.sheet.range('A1:D6')
        for cell, value in zip(cell_list, itertools.chain(*rows)):
            cell.value = value
        self.sheet.update_cells(cell_list)

        self.sheet.clear()
        self.assertEqual(self.sheet.get_all_values(), [])


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
        self.sheet = self.gc.open(title).sheet1

    def test_properties(self):
        sg = self._sequence_generator()
        update_value = next(sg)
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
        self.assertTrue(isinstance(cell.numeric_value, float))
        self.sheet.update_acell('A1', 'Non-numeric value')
        cell = self.sheet.acell('A1')
        self.assertEqual(cell.numeric_value, None)
