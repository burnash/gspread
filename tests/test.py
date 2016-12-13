# -*- coding: utf-8 -*-
import os
import re
import random
import unittest
import itertools
<<<<<<< 46798d67c38d2cf8e1c751b684897cdc98598205
<<<<<<< 95d918ab8c3e881f4363e5f5a50e98f79c768ddf
<<<<<<< 7e91ce60c91237a29536f0b2f609ab27a82d3d68
<<<<<<< 0f67973a7427fb0d14703e22f8f1308f0dfd6af5
=======
<<<<<<< HEAD
>>>>>>> # This is a combination of 2 commits.
=======
<<<<<<< HEAD
=======
<<<<<<< HEAD
>>>>>>> Update README.md
>>>>>>> Update README.md
import uuid
try:
    import ConfigParser
except ImportError:
    import configparser as ConfigParser

from oauth2client.service_account import ServiceAccountCredentials
<<<<<<< 46798d67c38d2cf8e1c751b684897cdc98598205
=======
<<<<<<< 95d918ab8c3e881f4363e5f5a50e98f79c768ddf
=======
>>>>>>> # This is a combination of 2 commits.
import json
<<<<<<< HEAD
<<<<<<< HEAD
import uuid
=======
>>>>>>> bce8213... switched tests to oauth
=======
import uuid
>>>>>>> 10dd72e... use uuid for test values generation

from oauth2client.client import SignedJwtAssertionCredentials
<<<<<<< 7e91ce60c91237a29536f0b2f609ab27a82d3d68
>>>>>>> Squashing all the commits to simpy things for merge
=======
<<<<<<< HEAD
>>>>>>> Update README.md
=======
=======
import json

from oauth2client.client import SignedJwtAssertionCredentials
>>>>>>> # This is a combination of 2 commits.
<<<<<<< 46798d67c38d2cf8e1c751b684897cdc98598205
>>>>>>> # This is a combination of 2 commits.
=======
>>>>>>> Update README.md
>>>>>>> Update README.md

import gspread

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

I18N_STR = u'Iñtërnâtiônàlizætiøn'#.encode('utf8')


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

<<<<<<< HEAD
=======

CONFIG_FILENAME = os.path.join(os.path.dirname(__file__), 'tests.config')
CREDS_FILENAME = os.path.join(os.path.dirname(__file__), 'creds.json')
SCOPE = ['https://spreadsheets.google.com/feeds']


def read_config(filename):
    config = ConfigParser.ConfigParser()
    config.readfp(open(filename))
    return config


def read_credentials(filename):
    creds_data = json.load(open(filename))
    return SignedJwtAssertionCredentials(creds_data['client_email'],
                                         creds_data['private_key'],
                                         SCOPE)

>>>>>>> Update README.md

CONFIG_FILENAME = os.path.join(os.path.dirname(__file__), 'tests.config')
CREDS_FILENAME = os.path.join(os.path.dirname(__file__), 'creds.json')
SCOPE = ['https://spreadsheets.google.com/feeds']


def read_config(filename):
    config = ConfigParser.ConfigParser()
    config.readfp(open(filename))
    return config


def read_credentials(filename):
    creds_data = json.load(open(filename))
    return SignedJwtAssertionCredentials(creds_data['client_email'],
                                         creds_data['private_key'],
                                         SCOPE)


<<<<<<< 95d918ab8c3e881f4363e5f5a50e98f79c768ddf
def gen_value(prefix=None):
    if prefix:
        return u'%s %s' % (prefix, gen_value())
    else:
        return unicode(uuid.uuid4())


CONFIG_FILENAME = os.path.join(os.path.dirname(__file__), 'tests.config')
CREDS_FILENAME = os.path.join(os.path.dirname(__file__), 'creds.json')
SCOPE = ['https://spreadsheets.google.com/feeds']


def read_config(filename):
    config = ConfigParser.ConfigParser()
    config.readfp(open(filename))
    return config


def read_credentials(filename):
    creds_data = json.load(open(filename))
    return SignedJwtAssertionCredentials(creds_data['client_email'],
                                         creds_data['private_key'],
                                         SCOPE)


<<<<<<< HEAD
<<<<<<< HEAD
=======
>>>>>>> 10dd72e... use uuid for test values generation
def gen_value(prefix=None):
    if prefix:
        return u'%s %s' % (prefix, gen_value())
    else:
        return unicode(uuid.uuid4())


=======
>>>>>>> # This is a combination of 2 commits.
class GspreadTest(unittest.TestCase):
<<<<<<< HEAD
<<<<<<< 46798d67c38d2cf8e1c751b684897cdc98598205


<<<<<<< 358c39a5513a0d4983c3302e15bb78acca66481b
<<<<<<< 7e91ce60c91237a29536f0b2f609ab27a82d3d68
<<<<<<< 0f67973a7427fb0d14703e22f8f1308f0dfd6af5
=======

>>>>>>> Squashing all the commits to simpy things for merge
=======
=======
>>>>>>> Update README.md

>>>>>>> # This is a combination of 2 commits.
=======
=======
class GspreadTest(unittest.TestCase):

>>>>>>> bce8213... switched tests to oauth
>>>>>>> small date fix in changelog from commit 0a06735a4d
    @classmethod
    def setUpClass(cls):
<<<<<<< 46798d67c38d2cf8e1c751b684897cdc98598205
=======
<<<<<<< HEAD
=======
>>>>>>> Update README.md
=======
    def setUp(self):
        creds_filename = "tests.config"
>>>>>>> e676183... added test for Worksheet "updated" property
<<<<<<< 46798d67c38d2cf8e1c751b684897cdc98598205
=======
>>>>>>> Update README.md
>>>>>>> Update README.md
        try:
            cls.config = read_config(CONFIG_FILENAME)
            credentials = read_credentials(CREDS_FILENAME)
            cls.gc = gspread.authorize(credentials)
        except IOError as e:
            msg = "Can't find %s for reading test configuration. "
            raise Exception(msg % e.filename)

    def setUp(self):
        self.assertTrue(isinstance(self.gc, gspread.Client))


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

    def test_create(self):
        title = gen_value('TestSpreadsheet')
        new_spreadsheet = self.gc.create(title)
        self.assertTrue(isinstance(new_spreadsheet, gspread.Spreadsheet))


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
        self.assertEqual(self.spreadsheet.worksheets(),
            [sheet for sheet in self.spreadsheet])


class WorksheetTest(GspreadTest):

    """Test for gspread.Worksheet."""

    @classmethod
    def setUpClass(cls):
        super(WorksheetTest, cls).setUpClass()
        title = cls.config.get('Spreadsheet', 'title')
        cls.spreadsheet = cls.gc.open(title)

    def setUp(self):
        super(WorksheetTest, self).setUp()
        #NOTE(msuozzo): Here, a new worksheet is created for each test.
        # This was determined to be faster than reusing a single sheet and
        # having to clear its contents after each test.
        # Basically: Time(add_wks + del_wks) < Time(range + update_cells)
        self.sheet = self.spreadsheet.add_worksheet('wksht_test', 20, 20)

    def tearDown(self):
        self.spreadsheet.del_worksheet(self.sheet)

    def test_get_int_addr(self):
        self.assertEqual(self.sheet.get_int_addr('ABC3'), (3, 731))

    def test_get_addr_int(self):
        self.assertEqual(self.sheet.get_addr_int(3, 731), 'ABC3')
        self.assertEqual(self.sheet.get_addr_int(1, 104), 'CZ1')
<<<<<<< 46798d67c38d2cf8e1c751b684897cdc98598205
<<<<<<< 95d918ab8c3e881f4363e5f5a50e98f79c768ddf
<<<<<<< 358c39a5513a0d4983c3302e15bb78acca66481b
<<<<<<< 7e91ce60c91237a29536f0b2f609ab27a82d3d68
<<<<<<< 0f67973a7427fb0d14703e22f8f1308f0dfd6af5
=======
<<<<<<< HEAD
>>>>>>> # This is a combination of 2 commits.
=======
<<<<<<< HEAD

    def test_get_updated(self):
        RFC_3339 = (r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?'
                    r'(Z|[+-]\d{2}:\d{2})')
        has_match = re.match(RFC_3339, self.sheet.updated) is not None
        self.assertTrue(has_match)
=======
<<<<<<< HEAD
<<<<<<< HEAD
=======
=======
>>>>>>> 02c23fc... # This is a combination of 2 commits.
>>>>>>> Update README.md

    def test_get_updated(self):
<<<<<<< HEAD
        RFC_3339 = '(\d\d\d\d)(-)?(\d\d)(-)?(\d\d)(T)?(\d\d)(:)?(\d\d)(:)?(\d\d)(\.\d+)?(Z|([+-])(\d\d)(:)?(\d\d))'
        print self.sheet.updated
=======
        RFC_3339 = (r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?'
                    r'(Z|[+-]\d{2}:\d{2})')
<<<<<<< HEAD
>>>>>>> 5cc0902... Fixed failing tests, refactored WorksheetTests
        self.assertRegexpMatches(self.sheet.updated, RFC_3339)
>>>>>>> e676183... added test for Worksheet "updated" property
=======
        has_match = re.match(RFC_3339, self.sheet.updated) is not None
        self.assertTrue(has_match)
<<<<<<< 46798d67c38d2cf8e1c751b684897cdc98598205
=======
<<<<<<< 95d918ab8c3e881f4363e5f5a50e98f79c768ddf
=======
>>>>>>> # This is a combination of 2 commits.
=======
<<<<<<< HEAD
<<<<<<< HEAD
>>>>>>> small date fix in changelog from commit 0a06735a4d
    
    def test_get_updated(self):
        RFC_3339 = ('\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?'
	                    '(Z|[+-]\d{2}:\d{2})')
	self.assertRegexpMatches(self.sheet.updated, RFC_3339)
<<<<<<< 358c39a5513a0d4983c3302e15bb78acca66481b
<<<<<<< 7e91ce60c91237a29536f0b2f609ab27a82d3d68
>>>>>>> Squashing all the commits to simpy things for merge
=======
>>>>>>> # This is a combination of 2 commits.
=======
=======
>>>>>>> bce8213... switched tests to oauth
=======

    def test_get_updated(self):
        RFC_3339 = '(\d\d\d\d)(-)?(\d\d)(-)?(\d\d)(T)?(\d\d)(:)?(\d\d)(:)?(\d\d)(\.\d+)?(Z|([+-])(\d\d)(:)?(\d\d))'
        print self.sheet.updated
        self.assertRegexpMatches(self.sheet.updated, RFC_3339)
>>>>>>> e676183... added test for Worksheet "updated" property
>>>>>>> small date fix in changelog from commit 0a06735a4d
=======
>>>>>>> # This is a combination of 2 commits.
>>>>>>> # This is a combination of 2 commits.
=======
<<<<<<< HEAD
>>>>>>> 0459e76... Fix all the tests!
=======
=======
>>>>>>> # This is a combination of 2 commits.
>>>>>>> 02c23fc... # This is a combination of 2 commits.
>>>>>>> Update README.md
>>>>>>> Update README.md

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
        cell_range1 = self.sheet.range('A1:A5')
        cell_range2 = self.sheet.range(1, 1, 5, 1)
        for c1, c2 in zip(cell_range1, cell_range2):
            self.assertTrue(isinstance(c1, gspread.Cell))
            self.assertTrue(isinstance(c2, gspread.Cell))
            self.assertTrue(c1.col == c2.col)
            self.assertTrue(c1.row == c2.row)
            self.assertTrue(c1.value == c2.value)

    def test_update_acell(self):
        value = gen_value()
        self.sheet.update_acell('A2', value)
        self.assertEqual(self.sheet.acell('A2').value, value)

    def test_update_cell(self):
        value = gen_value()
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
        value = gen_value()
        value = "%s\n%s" % (value, value)
        self.sheet.update_cell(1, 2, value)
        self.assertEqual(self.sheet.cell(1, 2).value, value)

    def test_update_cell_unicode(self):
        self.sheet.update_cell(1, 1, I18N_STR)

        cell = self.sheet.cell(1, 1)
        self.assertEqual(cell.value, I18N_STR)

    def test_update_cells(self):
        list_len = 10
        value_list = [gen_value(i) for i in range(list_len)]

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
<<<<<<< 0f67973a7427fb0d14703e22f8f1308f0dfd6af5
=======
        sheet = self.sheet
<<<<<<< 7e91ce60c91237a29536f0b2f609ab27a82d3d68
>>>>>>> Squashing all the commits to simpy things for merge
=======
>>>>>>> # This is a combination of 2 commits.
        value = gen_value()

        self.sheet.update_cell(2, 10, value)
        self.sheet.update_cell(2, 11, value)

        cell = self.sheet.find(value)
        self.assertEqual(cell.value, value)

        value2 = gen_value()
        value = "%so_O%s" % (value, value2)
        self.sheet.update_cell(2, 11, value)

        o_O_re = re.compile('[a-z]_[A-Z]%s' % value2)

        cell = self.sheet.find(o_O_re)
        self.assertEqual(cell.value, value)

    def test_findall(self):
        list_len = 10
        range_label = 'A1:A%s' % list_len
<<<<<<< 0f67973a7427fb0d14703e22f8f1308f0dfd6af5
        cell_list = self.sheet.range(range_label)
=======
        cell_list = sheet.range(range_label)
<<<<<<< 7e91ce60c91237a29536f0b2f609ab27a82d3d68
>>>>>>> Squashing all the commits to simpy things for merge
=======
>>>>>>> # This is a combination of 2 commits.
        value = gen_value()

        for c in cell_list:
            c.value = value
        self.sheet.update_cells(cell_list)

        result_list = self.sheet.findall(value)

        self.assertEqual(list_len, len(result_list))

        for c in result_list:
            self.assertEqual(c.value, value)

        cell_list = self.sheet.range(range_label)

        value = gen_value()
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

<<<<<<< a69cd84f789e21aa91b9c488abd3dc4ac39c8361
        # then, read empty strings to None
        read_records = self.sheet.get_all_records(default_blank=None)
        d1 = dict(zip(rows[0], (None, None, None, None)))
        self.assertEqual(read_records[1], d1)

        # then, read empty strings to something else
        read_records = self.sheet.get_all_records(default_blank='foo')
        d1 = dict(zip(rows[0], ('foo', 'foo', 'foo', 'foo')))
        self.assertEqual(read_records[1], d1)

    def test_get_all_records_different_header(self):
<<<<<<< HEAD
<<<<<<< 46798d67c38d2cf8e1c751b684897cdc98598205
        self.sheet.resize(6, 4)
=======
<<<<<<< 95d918ab8c3e881f4363e5f5a50e98f79c768ddf
    def test_get_all_records_different_header(self):
=======
>>>>>>> # This is a combination of 2 commits.
=======
        self.sheet.resize(6, 4)
=======
<<<<<<< HEAD
        self.sheet.resize(6, 4)
=======
>>>>>>> Update README.md
        # make a new, clean worksheet
        # same as for test_all_values, find a way to refactor it
        self.spreadsheet.add_worksheet('get_all_records', 10, 5)
        sheet = self.spreadsheet.worksheet('get_all_records')

>>>>>>> # This is a combination of 2 commits.
<<<<<<< 46798d67c38d2cf8e1c751b684897cdc98598205
=======
>>>>>>> Update README.md
>>>>>>> Update README.md
        # put in new values, made from three lists
        rows = [["", "", "", ""],
                ["", "", "", ""],
                ["A1", "B1", "", "D1"],
                [1, "b2", 1.45, ""],
                ["", "", "", ""],
                ["A4", 0.4, "", 4]]
<<<<<<< 46798d67c38d2cf8e1c751b684897cdc98598205
<<<<<<< 95d918ab8c3e881f4363e5f5a50e98f79c768ddf
<<<<<<< a69cd84f789e21aa91b9c488abd3dc4ac39c8361
=======
<<<<<<< HEAD
>>>>>>> # This is a combination of 2 commits.
=======
<<<<<<< HEAD
        cell_list = self.sheet.range('A1:D6')
=======
<<<<<<< HEAD
>>>>>>> Update README.md
        cell_list = self.sheet.range('A1:D6')
        for cell, value in zip(cell_list, itertools.chain(*rows)):
            cell.value = value
        self.sheet.update_cells(cell_list)

        # first, read empty strings to empty strings
        read_records = self.sheet.get_all_records(head=3)
=======
        cell_list = sheet.range('A1:D1')
        cell_list.extend(sheet.range('A2:D2'))
        cell_list.extend(sheet.range('A3:D3'))
        cell_list.extend(sheet.range('A4:D4'))
        cell_list.extend(sheet.range('A5:D5'))
        cell_list.extend(sheet.range('A6:D6'))
<<<<<<< 46798d67c38d2cf8e1c751b684897cdc98598205
        for cell, value in zip(cell_list, itertools.chain(*rows)):
            cell.value = value
        sheet.update_cells(cell_list)

        # first, read empty strings to empty strings
        read_records = sheet.get_all_records(head=3)
>>>>>>> # This is a combination of 2 commits.
=======
>>>>>>> Update README.md
        for cell, value in zip(cell_list, itertools.chain(*rows)):
            cell.value = value
        self.sheet.update_cells(cell_list)

        # first, read empty strings to empty strings
<<<<<<< HEAD
        read_records = self.sheet.get_all_records(head=3)
=======
        read_records = sheet.get_all_records(head=3)
>>>>>>> # This is a combination of 2 commits.
>>>>>>> Update README.md
>>>>>>> Update README.md
        d0 = dict(zip(rows[2], rows[3]))
        d1 = dict(zip(rows[2], rows[4]))
        d2 = dict(zip(rows[2], rows[5]))
        self.assertEqual(read_records[0], d0)
        self.assertEqual(read_records[1], d1)
        self.assertEqual(read_records[2], d2)

        # then, read empty strings to zeros
<<<<<<< 46798d67c38d2cf8e1c751b684897cdc98598205
<<<<<<< 95d918ab8c3e881f4363e5f5a50e98f79c768ddf
<<<<<<< a69cd84f789e21aa91b9c488abd3dc4ac39c8361
=======
<<<<<<< HEAD
>>>>>>> # This is a combination of 2 commits.
=======
<<<<<<< HEAD
>>>>>>> Update README.md
        read_records = self.sheet.get_all_records(empty2zero=True, head=3)
        d1 = dict(zip(rows[2], (0, 0, 0, 0)))
        self.assertEqual(read_records[1], d1)

<<<<<<< 46798d67c38d2cf8e1c751b684897cdc98598205
<<<<<<< 95d918ab8c3e881f4363e5f5a50e98f79c768ddf
        # then, read empty strings to None
        read_records = self.sheet.get_all_records(default_blank=None, head=3)
        d1 = dict(zip(rows[2], (None, None, None, None)))
        self.assertEqual(read_records[1], d1)

        # then, read empty strings to something else
        read_records = self.sheet.get_all_records(default_blank='foo', head=3)
        d1 = dict(zip(rows[2], ('foo', 'foo', 'foo', 'foo')))
        self.assertEqual(read_records[1], d1)
=======
>>>>>>> # This is a combination of 2 commits.
=======
=======
<<<<<<< HEAD
        read_records = self.sheet.get_all_records(empty2zero=True, head=3)
        d1 = dict(zip(rows[2], (0, 0, 0, 0)))
        self.assertEqual(read_records[1], d1)

>>>>>>> Update README.md
=======
        read_records = sheet.get_all_records(empty2zero=True, head=3)
        d1 = dict(zip(rows[2], (0, 0, 0, 0)))
        self.assertEqual(read_records[1], d1)

        self.gc.del_worksheet(sheet)
<<<<<<< 46798d67c38d2cf8e1c751b684897cdc98598205
<<<<<<< 95d918ab8c3e881f4363e5f5a50e98f79c768ddf
>>>>>>> # This is a combination of 2 commits.

=======

>>>>>>> # This is a combination of 2 commits.
>>>>>>> # This is a combination of 2 commits.
=======

>>>>>>> # This is a combination of 2 commits.
>>>>>>> Update README.md
>>>>>>> Update README.md
    def test_append_row(self):
        num_rows = self.sheet.row_count
        num_cols = self.sheet.col_count
        values = [I18N_STR] * (num_cols + 4)
        self.sheet.append_row(values)
        self.assertEqual(self.sheet.row_count, num_rows + 1)
        self.assertEqual(self.sheet.col_count, num_cols + 4)
        read_values = self.sheet.row_values(self.sheet.row_count)
        self.assertEqual(values, read_values)

    def test_insert_row(self):
        num_rows = self.sheet.row_count
        num_cols = self.sheet.col_count
        values = [gen_value(i) for i in range(num_cols + 4)]
        self.sheet.insert_row(values, 1)
        self.assertEqual(self.sheet.row_count, num_rows + 1)
        self.assertEqual(self.sheet.col_count, num_cols + 4)
        read_values = self.sheet.row_values(1)
        self.assertEqual(values, read_values)

<<<<<<< 0f67973a7427fb0d14703e22f8f1308f0dfd6af5
        formula = '=1+1'
        self.sheet.update_acell('B2', formula)
        values = [gen_value(i) for i in range(num_cols + 4)]
        self.sheet.insert_row(values, 1)
        b3 = self.sheet.acell('B3')
        self.assertEqual(b3.input_value, formula)

    def test_delete_row(self):
        num_rows = self.sheet.row_count

        prev = self.sheet.row_values(1)
        next = self.sheet.row_values(3)
        self.sheet.delete_row(2)
        self.assertEqual(self.sheet.row_count, num_rows - 1)
        self.assertEqual(self.sheet.row_values(1), prev)
        self.assertEqual(self.sheet.row_values(2), next)

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

    def test_export(self):
        list_len = 10

=======
        # undo the appending and resizing
        # self.sheet.resize(num_rows, num_cols)
    
    def test_insert_column(self):
    	num_rows = self.sheet.row_count
    	num_cols = self.sheet.col_count
    	values = ['o_0'] * (num_rows + 4)
    	self.sheet.insert_column(values, 1)
    	self.assertEqual(self.sheet.row_count, num_rows + 4)
    	self.assertEqual(self.sheet.col_count, num_cols + 1)
    	read_values = self.sheet.row_values(1)
    	self.assertEqual(values, read_values)

    def test_export(self):
        list_len = 10
        time_md5 = gen_value()
        wks_name = 'export_test_%s' % time_md5

        self.spreadsheet.add_worksheet(wks_name, list_len, 5)
        sheet = self.spreadsheet.worksheet(wks_name)

>>>>>>> Squashing all the commits to simpy things for merge
        value_list = [gen_value(i) for i in range(list_len)]

        range_label = 'A1:A%s' % list_len
        cell_list = self.sheet.range(range_label)

        for c, v in zip(cell_list, value_list):
            c.value = v

        self.sheet.update_cells(cell_list)
<<<<<<< HEAD

        exported_data = self.sheet.export(format='csv')
        exported_values = [unicode(line.decode())
                           for line in exported_data.splitlines()]

        self.assertEqual(exported_values, value_list)
=======

        exported_data = self.sheet.export(format='csv')
        exported_values = [unicode(line.decode())
                           for line in exported_data.splitlines()]

<<<<<<< 0f67973a7427fb0d14703e22f8f1308f0dfd6af5
=======
        exported_values = exported_data.split()

>>>>>>> Squashing all the commits to simpy things for merge
        self.assertEqual(exported_values, value_list)


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

    def test_insert_row(self):
        num_rows = self.sheet.row_count
        num_cols = self.sheet.col_count
        values = [gen_value(i) for i in range(num_cols + 4)]
<<<<<<< HEAD
<<<<<<< HEAD
=======
        print values
>>>>>>> 10dd72e... use uuid for test values generation
=======
>>>>>>> 1dbdb74... remove print
        self.sheet.insert_row(values, 1)
        self.assertEqual(self.sheet.row_count, num_rows + 1)
        self.assertEqual(self.sheet.col_count, num_cols + 4)
        read_values = self.sheet.row_values(1)
        self.assertEqual(values, read_values)

        # undo the appending and resizing
        # self.sheet.resize(num_rows, num_cols)
    
    def test_insert_column(self):
    	num_rows = self.sheet.row_count
    	num_cols = self.sheet.col_count
    	values = ['o_0'] * (num_rows + 4)
    	self.sheet.insert_column(values, 1)
    	self.assertEqual(self.sheet.row_count, num_rows + 4)
    	self.assertEqual(self.sheet.col_count, num_cols + 1)
    	read_values = self.sheet.row_values(1)
    	self.assertEqual(values, read_values)

    def test_export(self):
        list_len = 10
        time_md5 = gen_value()
        wks_name = 'export_test_%s' % time_md5

        self.spreadsheet.add_worksheet(wks_name, list_len, 5)
        sheet = self.spreadsheet.worksheet(wks_name)

        value_list = [gen_value(i) for i in range(list_len)]

        range_label = 'A1:A%s' % list_len
        cell_list = sheet.range(range_label)

        for c, v in zip(cell_list, value_list):
            c.value = v

        sheet.update_cells(cell_list)

        exported_data = sheet.export(format='csv').read()

        exported_values = exported_data.split()
<<<<<<< HEAD

        self.assertEqual(exported_values, value_list)

=======

        self.assertEqual(exported_values, value_list)
>>>>>>> a8f40f4... fixed export test


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

>>>>>>> Update README.md


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
<<<<<<< 46798d67c38d2cf8e1c751b684897cdc98598205
<<<<<<< 95d918ab8c3e881f4363e5f5a50e98f79c768ddf
<<<<<<< a69cd84f789e21aa91b9c488abd3dc4ac39c8361
=======
<<<<<<< HEAD
>>>>>>> # This is a combination of 2 commits.
=======
<<<<<<< HEAD
        self.sheet = self.gc.open(title).sheet1

    def test_properties(self):
        update_value = gen_value()
=======
<<<<<<< HEAD
>>>>>>> Update README.md
        self.sheet = self.gc.open(title).sheet1

    def test_properties(self):
        update_value = gen_value()
=======
        sheet = self.gc.open(title).sheet1
        self.sheet = sheet

    def test_properties(self):
<<<<<<< 46798d67c38d2cf8e1c751b684897cdc98598205
<<<<<<< 95d918ab8c3e881f4363e5f5a50e98f79c768ddf
<<<<<<< 7e91ce60c91237a29536f0b2f609ab27a82d3d68
        update_value = hashlib.md5(str(time.time())).hexdigest()
>>>>>>> # This is a combination of 2 commits.
=======
        update_value = gen_value()
>>>>>>> # This is a combination of 2 commits.
=======
        update_value = hashlib.md5(str(time.time())).hexdigest()
>>>>>>> # This is a combination of 2 commits.
>>>>>>> # This is a combination of 2 commits.
=======
        update_value = hashlib.md5(str(time.time())).hexdigest()
>>>>>>> # This is a combination of 2 commits.
>>>>>>> Update README.md
>>>>>>> Update README.md
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
<<<<<<< 46798d67c38d2cf8e1c751b684897cdc98598205
<<<<<<< 95d918ab8c3e881f4363e5f5a50e98f79c768ddf
<<<<<<< a69cd84f789e21aa91b9c488abd3dc4ac39c8361
=======
<<<<<<< HEAD
>>>>>>> # This is a combination of 2 commits.
=======
<<<<<<< HEAD
        self.assertTrue(isinstance(cell.numeric_value, float))
        self.sheet.update_acell('A1', 'Non-numeric value')
        cell = self.sheet.acell('A1')
        self.assertEqual(cell.numeric_value, None)
=======
<<<<<<< HEAD
>>>>>>> Update README.md
        self.assertTrue(isinstance(cell.numeric_value, float))
        self.sheet.update_acell('A1', 'Non-numeric value')
        cell = self.sheet.acell('A1')
        self.assertEqual(cell.numeric_value, None)
=======
        self.assertIsInstance(cell.numeric_value, float)
        self.sheet.update_acell('A1', 'Non-numeric value')
        cell = self.sheet.acell('A1')
        self.assertIs(cell.numeric_value, None)
>>>>>>> # This is a combination of 2 commits.
<<<<<<< 46798d67c38d2cf8e1c751b684897cdc98598205
=======
>>>>>>> Update README.md
>>>>>>> Update README.md
