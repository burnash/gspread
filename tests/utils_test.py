import unittest

import gspread
import gspread.utils as utils


class UtilsTest(unittest.TestCase):
    def test_extract_id_from_url(self):
        url_id_list = [
            # New-style url
            (
                "https://docs.google.com/spreadsheets/d/"
                "1qpyC0X3A0MwQoFDE8p-Bll4hps/edit#gid=0",
                "1qpyC0X3A0MwQoFDE8p-Bll4hps",
            ),
            (
                "https://docs.google.com/spreadsheets/d/"
                "1qpyC0X3A0MwQoFDE8p-Bll4hps/edit",
                "1qpyC0X3A0MwQoFDE8p-Bll4hps",
            ),
            (
                "https://docs.google.com/spreadsheets/d/" "1qpyC0X3A0MwQoFDE8p-Bll4hps",
                "1qpyC0X3A0MwQoFDE8p-Bll4hps",
            ),
            # Old-style url
            (
                "https://docs.google.com/spreadsheet/"
                "ccc?key=1qpyC0X3A0MwQoFDE8p-Bll4hps&usp=drive_web#gid=0",
                "1qpyC0X3A0MwQoFDE8p-Bll4hps",
            ),
        ]

        for url, id in url_id_list:
            self.assertEqual(id, utils.extract_id_from_url(url))

    def test_no_extract_id_from_url(self):
        self.assertRaises(
            gspread.NoValidUrlKeyFound, utils.extract_id_from_url, "http://example.org"
        )

    def test_a1_to_rowcol(self):
        self.assertEqual(utils.a1_to_rowcol("ABC3"), (3, 731))

    def test_rowcol_to_a1(self):
        self.assertEqual(utils.rowcol_to_a1(3, 731), "ABC3")
        self.assertEqual(utils.rowcol_to_a1(1, 104), "CZ1")

    def test_addr_converters(self):
        for row in range(1, 257):
            for col in range(1, 512):
                addr = utils.rowcol_to_a1(row, col)
                (r, c) = utils.a1_to_rowcol(addr)
                self.assertEqual((row, col), (r, c))

    def test_get_gid(self):
        gid = "od6"
        self.assertEqual(utils.wid_to_gid(gid), "0")
        gid = "osyqnsz"
        self.assertEqual(utils.wid_to_gid(gid), "1751403737")
        gid = "ogsrar0"
        self.assertEqual(utils.wid_to_gid(gid), "1015761654")

    def test_numericise(self):
        self.assertEqual(utils.numericise("faa"), "faa")
        self.assertEqual(utils.numericise("3"), 3)
        self.assertEqual(utils.numericise("3_2"), "3_2")
        self.assertEqual(
            utils.numericise("3_2", allow_underscores_in_numeric_literals=False), "3_2"
        )
        self.assertEqual(
            utils.numericise("3_2", allow_underscores_in_numeric_literals=True), 32
        )
        self.assertEqual(utils.numericise("3.1"), 3.1)
        self.assertEqual(utils.numericise("", empty2zero=True), 0)
        self.assertEqual(utils.numericise("", empty2zero=False), "")
        self.assertEqual(utils.numericise("", default_blank=None), None)
        self.assertEqual(utils.numericise("", default_blank="foo"), "foo")
        self.assertEqual(utils.numericise(""), "")
        self.assertEqual(utils.numericise(None), None)

        # test numericise_all
        inputs = ["1", "2", "3"]
        expected = [1, 2, 3]
        self.assertEqual(utils.numericise_all(inputs), expected)

        # skip non digit values
        inputs + ["a"]
        expected + ["a"]
        self.assertEqual(utils.numericise_all(inputs), expected)

        # skip ignored columns
        inputs + ["5", "5"]
        expected + ["5", 5]
        self.assertEqual(utils.numericise_all(inputs, ignore=[5]), expected)

        # provide explicit `None` as ignored list
        self.assertEqual(utils.numericise_all(inputs, ignore=None), expected)

    def test_a1_to_grid_range_simple(self):
        expected_single_dimension = {
            "startRowIndex": 0,
            "endRowIndex": 10,
            "startColumnIndex": 0,
            "endColumnIndex": 1,
        }
        actual_single_dimension = utils.a1_range_to_grid_range("A1:A10")

        expected_two_dimensional = {
            "startRowIndex": 2,
            "endRowIndex": 4,
            "startColumnIndex": 0,
            "endColumnIndex": 2,
        }
        actual_two_dimensional = utils.a1_range_to_grid_range("A3:B4")

        expected_with_sheet_id = {
            "sheetId": 0,
            "startRowIndex": 0,
            "endRowIndex": 10,
            "startColumnIndex": 0,
            "endColumnIndex": 1,
        }
        actual_with_sheet_id = utils.a1_range_to_grid_range("A1:A10", sheet_id=0)

        self.assertEqual(actual_single_dimension, expected_single_dimension)
        self.assertEqual(actual_two_dimensional, expected_two_dimensional)
        self.assertEqual(actual_with_sheet_id, expected_with_sheet_id)

    def test_a1_to_grid_range_unbounded(self):
        expected_unbounded = {
            "startRowIndex": 4,
            "startColumnIndex": 0,
            "endColumnIndex": 2,
        }
        actual_unbounded = utils.a1_range_to_grid_range("A5:B")

        expected_full_columns = {"startColumnIndex": 0, "endColumnIndex": 2}
        actual_full_columns = utils.a1_range_to_grid_range("A:B")

        expected_with_sheet_id = {
            "sheetId": 0,
            "startRowIndex": 4,
            "startColumnIndex": 0,
            "endColumnIndex": 2,
        }
        actual_with_sheet_id = utils.a1_range_to_grid_range("A5:B", sheet_id=0)

        self.assertEqual(actual_unbounded, expected_unbounded)
        self.assertEqual(actual_full_columns, expected_full_columns)
        self.assertEqual(actual_with_sheet_id, expected_with_sheet_id)

    def test_a1_to_grid_range_improper_range(self):
        expected_single_cell = {
            "startRowIndex": 0,
            "endRowIndex": 1,
            "startColumnIndex": 0,
            "endColumnIndex": 1,
        }
        actual_single_cell = utils.a1_range_to_grid_range("A1")

        expected_single_column = {"startColumnIndex": 0, "endColumnIndex": 1}
        actual_single_column = utils.a1_range_to_grid_range("A")

        expected_single_row = {"startRowIndex": 0, "endRowIndex": 1}
        actual_single_row = utils.a1_range_to_grid_range("1")

        expected_with_sheet = {
            "sheetId": 0,
            "startRowIndex": 0,
            "endRowIndex": 1,
            "startColumnIndex": 0,
            "endColumnIndex": 1,
        }
        actual_with_sheet = utils.a1_range_to_grid_range("A1", sheet_id=0)

        self.assertEqual(actual_single_cell, expected_single_cell)
        self.assertEqual(actual_single_column, expected_single_column)
        self.assertEqual(actual_single_row, expected_single_row)
        self.assertEqual(actual_with_sheet, expected_with_sheet)

    def test_a1_to_grid_range_other_directions(self):
        from_top_left = utils.a1_range_to_grid_range("C2:D4")
        from_bottom_right = utils.a1_range_to_grid_range("D4:C2")
        from_top_right = utils.a1_range_to_grid_range("D2:C4")
        from_bottom_left = utils.a1_range_to_grid_range("C4:D2")

        self.assertEqual(from_top_left, from_bottom_right)
        self.assertEqual(from_top_left, from_bottom_left)
        self.assertEqual(from_top_left, from_top_right)

    def test_column_letter_to_index(self):
        # All the input values to test one after an other
        # [0] input value
        # [1] expected return value
        # [2] expected exception to raise
        inputs = [
            ("", None, gspread.exceptions.InvalidInputValue),
            ("A", 1, None),
            ("Z", 26, None),
            ("AA", 27, None),
            ("AAA", 703, None),
            ("ABCDEFGHIJKLMNOPQRSTUVWXYZ", 256094574536617744129141650397448476, None),
            ("!@#$%^&*()", None, gspread.exceptions.InvalidInputValue),
        ]

        for label, expected, exception in inputs:
            if exception is not None:
                # assert the exception is raised
                with self.assertRaises(exception):
                    utils.column_letter_to_index(label)
            else:
                # assert the return values is correct
                result = utils.column_letter_to_index(label)
                self.assertEqual(
                    result,
                    expected,
                    "could not convert column letter '{}' to the right value '{}".format(
                        label, expected
                    ),
                )
