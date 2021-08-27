# -*- coding: utf-8 -*-

import re

from .test import GspreadTest

import gspread


class SpreadsheetTest(GspreadTest):

    """Test for gspread.Spreadsheet."""

    def setUp(self):
        super(SpreadsheetTest, self).setUp()
        self.spreadsheet = self.gc.open(self.get_temporary_spreadsheet_title())

    def test_properties(self):
        self.assertTrue(re.match(r"^[a-zA-Z0-9-_]+$", self.spreadsheet.id))
        self.assertTrue(len(self.spreadsheet.title) > 0)

    def test_sheet1(self):
        sheet1 = self.spreadsheet.sheet1
        self.assertTrue(isinstance(sheet1, gspread.Worksheet))

    def test_get_worksheet(self):
        sheet1 = self.spreadsheet.get_worksheet(0)
        self.assertTrue(isinstance(sheet1, gspread.Worksheet))

    def test_get_worksheet_by_id(self):
        sheet1 = self.spreadsheet.get_worksheet_by_id(0)
        self.assertTrue(isinstance(sheet1, gspread.Worksheet))

    def test_worksheet(self):
        sheet_title = "Sheet1"
        sheet = self.spreadsheet.worksheet(sheet_title)
        self.assertTrue(isinstance(sheet, gspread.Worksheet))

    def test_worksheet_iteration(self):
        self.assertEqual(
            [x.id for x in self.spreadsheet.worksheets()],
            [sheet.id for sheet in self.spreadsheet],
        )

    def test_values_get(self):
        sg = self._sequence_generator()

        worksheet1_name = u"%s %s" % (u"🌵", next(sg))

        worksheet = self.spreadsheet.add_worksheet(worksheet1_name, 10, 10)

        range_label = "%s!%s" % (worksheet1_name, "A1")

        values = [[u"🍇", u"🍉", u"🍋"], [u"🍐", u"🍎", u"🍓"]]

        self.spreadsheet.values_update(
            range_label, params={"valueInputOption": "RAW"}, body={"values": values}
        )

        read_data = self.spreadsheet.values_get(worksheet1_name)

        self.assertEqual(values, read_data["values"])
        self.spreadsheet.del_worksheet(worksheet)

    def test_add_del_worksheet(self):
        sg = self._sequence_generator()
        worksheet1_name = next(sg)
        worksheet2_name = next(sg)

        worksheet_list = self.spreadsheet.worksheets()
        self.assertEqual(len(worksheet_list), 1)
        existing_sheet_title = worksheet_list[0].title

        # Add
        worksheet1 = self.spreadsheet.add_worksheet(worksheet1_name, 1, 1)
        worksheet2 = self.spreadsheet.add_worksheet(worksheet2_name, 1, 1)

        # Re-read, check again
        worksheet_list = self.spreadsheet.worksheets()
        self.assertEqual(len(worksheet_list), 3)

        # Delete
        self.spreadsheet.del_worksheet(worksheet1)
        self.spreadsheet.del_worksheet(worksheet2)

        worksheet_list = self.spreadsheet.worksheets()
        self.assertEqual(len(worksheet_list), 1)
        self.assertEqual(worksheet_list[0].title, existing_sheet_title)

    def test_values_batch_get(self):
        sg = self._sequence_generator()

        worksheet1_name = u"%s %s" % (u"🌵", next(sg))

        worksheet = self.spreadsheet.add_worksheet(worksheet1_name, 10, 10)

        range_label = "%s!%s" % (worksheet1_name, "A1")

        values = [[u"🍇", u"🍉", u"🍋"], [u"🍐", u"🍎", u"🍓"]]

        self.spreadsheet.values_update(
            range_label, params={"valueInputOption": "RAW"}, body={"values": values}
        )
        ranges = ["%s!%s:%s" % (worksheet1_name, col, col) for col in ["A", "B", "C"]]

        read_data = self.spreadsheet.values_batch_get(ranges)

        for colix, rng in enumerate(read_data["valueRanges"]):
            for rowix, ele in enumerate(rng["values"]):
                self.assertEqual(values[rowix][colix], ele[0])
        self.spreadsheet.del_worksheet(worksheet)
