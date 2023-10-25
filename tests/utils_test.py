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

    def test_combine_merge_values(self):
        sheet_data = [
            [1, None, None, None],
            [None, None, "title", None],
            [None, None, 2, None],
            ["num", "val", None, 0],
        ]
        sheet_metadata = {
            "properties": {"sheetId": 0},
            "merges": [
                {
                    "startRowIndex": 0,
                    "endRowIndex": 2,
                    "startColumnIndex": 0,
                    "endColumnIndex": 2,
                },
                {
                    "startRowIndex": 1,
                    "endRowIndex": 2,
                    "startColumnIndex": 2,
                    "endColumnIndex": 4,
                },
                {
                    "startRowIndex": 2,
                    "endRowIndex": 4,
                    "startColumnIndex": 2,
                    "endColumnIndex": 3,
                },
            ],
        }
        expected_combine = [
            [1, 1, None, None],
            [1, 1, "title", "title"],
            [None, None, 2, None],
            ["num", "val", 2, 0],
        ]

        actual_combine = utils.combined_merge_values(sheet_metadata, sheet_data, 0, 0)

        self.assertEqual(actual_combine, expected_combine)

    def test_combine_merge_values_outside_range(self):
        """Make sure that merges outside the range of the sheet are ignored or partially ignored
        see issue #1298
        """
        sheet_data = [
            [1, None, None, None],
            [None, None, "title", None],
            [None, None, 2, None],
            ["num", "val", None, 0],
        ]
        sheet_metadata = {
            "properties": {"sheetId": 0},
            "merges": [
                {
                    "startRowIndex": 7,
                    "endRowIndex": 9,
                    "startColumnIndex": 7,
                    "endColumnIndex": 9,
                },
                {
                    "startRowIndex": 3,
                    "endRowIndex": 5,
                    "startColumnIndex": 1,
                    "endColumnIndex": 2,
                },
            ],
        }
        expected_combine = [
            [1, None, None, None],
            [None, None, "title", None],
            [None, None, 2, None],
            ["num", "val", None, 0],
        ]

        actual_combine = utils.combined_merge_values(sheet_metadata, sheet_data, 0, 0)

        self.assertEqual(actual_combine, expected_combine)

    def test_combine_merge_values_from_centre_of_sheet(self):
        """Make sure that merges start from the right index when the sheet is not at the top left
        see issue #1330
        """
        sheet_data = [
            [1, None, None, None],
            [None, None, "title", None],
            [None, None, 2, None],
            ["num", "val", None, 0],
        ]
        sheet_metadata = {
            "properties": {"sheetId": 0},
            "merges": [
                {
                    "startRowIndex": 0,
                    "endRowIndex": 2,
                    "startColumnIndex": 0,
                    "endColumnIndex": 2,
                },
                {
                    "startRowIndex": 1,
                    "endRowIndex": 2,
                    "startColumnIndex": 2,
                    "endColumnIndex": 4,
                },
                {
                    "startRowIndex": 2,
                    "endRowIndex": 4,
                    "startColumnIndex": 2,
                    "endColumnIndex": 3,
                },
            ],
        }
        sheet_data_cropped = [sheet_data[1:] for sheet_data in sheet_data][1:]
        # [None, "title", None],
        # [None, 2, None],
        # ["val", None, 0]
        expected_combined_cropped = [
            [None, "title", "title"],
            [None, 2, None],
            ["val", 2, 0],
        ]

        actual_combine = utils.combined_merge_values(
            sheet_metadata, sheet_data_cropped, start_row_index=1, start_col_index=1
        )

        self.assertEqual(actual_combine, expected_combined_cropped)

    def test_convert_colors_to_hex_value(self):
        color = {"red": 1, "green": 0.5, "blue": 0}
        expected_hex = "#FF8000"

        # successful convert from colors
        hex = utils.convert_colors_to_hex_value(**color)
        self.assertEqual(hex, expected_hex)

        # successful convert from partial input
        hex = utils.convert_colors_to_hex_value(green=1)
        self.assertEqual(hex, "#00FF00")

        # throw ValueError on color values out of range (0-1)
        with self.assertRaises(ValueError):
            utils.convert_colors_to_hex_value(1.23, 0, -50)

    def test_convert_hex_to_color(self):
        hexcolor = "#FF7F00"
        expected_color = {"red": 1, "green": 0.49803922, "blue": 0}

        # successful convert from hex to color
        rgbcolor = utils.convert_hex_to_colors_dict(hexcolor)
        for key, rgbvalue in rgbcolor.items():
            self.assertAlmostEqual(rgbvalue, expected_color[key])

        # successful ignore alpha
        rgbcolor = utils.convert_hex_to_colors_dict(f"{hexcolor}42")
        for key, rgbvalue in rgbcolor.items():
            self.assertAlmostEqual(rgbvalue, expected_color[key])

        # raise ValueError on invalid hex length
        with self.assertRaises(ValueError):
            utils.convert_hex_to_colors_dict("123456abcdef")

        # raise ValueError on invalid hex characters
        with self.assertRaises(ValueError):
            utils.convert_hex_to_colors_dict("axbcde")

    def test_fill_gaps(self):
        """test fill_gaps function"""
        matrix = [
            [1, 2, 3, 4],
            [5, 6, 7, 8],
        ]
        expected = [
            [1, 2, 3, 4, "", ""],
            [5, 6, 7, 8, "", ""],
            ["", "", "", "", "", ""],
        ]
        actual = utils.fill_gaps(matrix, 3, 6)

        self.assertEqual(actual, expected)

    def test_fill_gaps_with_value(self):
        """test fill_gaps function"""
        matrix = [
            [1, 2, 3, 4],
            [5, 6, 7, 8],
        ]
        expected = [
            [1, 2, 3, 4, "a", "a"],
            [5, 6, 7, 8, "a", "a"],
            ["a", "a", "a", "a", "a", "a"],
        ]
        actual = utils.fill_gaps(matrix, 3, 6, "a")

        self.assertEqual(actual, expected)

        expected = [
            [1, 2, 3, 4, 3, 3],
            [5, 6, 7, 8, 3, 3],
            [3, 3, 3, 3, 3, 3],
        ]
        actual = utils.fill_gaps(matrix, 3, 6, 3)

        self.assertEqual(actual, expected)

    def test_accepted_kwargs(self):
        """test accepted_kwargs function.
        Test the temporary special value: REQUIRED_KWARGS
        """

        expected_arg0 = 0
        expected_arg1 = 1

        @utils.accepted_kwargs(arg1=1)
        def sample_arg1(arg0, **kwargs):
            self.assertEqual(arg0, expected_arg0)
            self.assertEqual(kwargs["arg1"], expected_arg1)

        sample_arg1(0)

        expected_arg2 = 2

        @utils.accepted_kwargs(arg1=utils.REQUIRED_KWARGS, arg2=2)
        def sample_arg2(arg0, arg1=None, **kwargs):
            self.assertEqual(arg0, expected_arg0)
            self.assertEqual(arg1, expected_arg1)
            self.assertEqual(kwargs["arg2"], expected_arg2)

        sample_arg2(0, arg1=1, arg2=2)

    def test_is_full_a1_notation(self):
        """test is_full_a1_notation function"""
        self.assertTrue(utils.is_full_a1_notation("A1:B2"))
        self.assertTrue(utils.is_full_a1_notation("Sheet1!A1:B2"))
        self.assertTrue(utils.is_full_a1_notation("AZ1:BBY2"))
        self.assertTrue(utils.is_full_a1_notation("AZ142:BBY122"))

        self.assertFalse(utils.is_full_a1_notation("Sheet1"))
        self.assertFalse(utils.is_full_a1_notation("A:B"))
        self.assertFalse(utils.is_full_a1_notation("1:2"))
        self.assertFalse(utils.is_full_a1_notation("1:"))
        self.assertFalse(utils.is_full_a1_notation("A1"))
        self.assertFalse(utils.is_full_a1_notation("A"))
        self.assertFalse(utils.is_full_a1_notation("1"))
        self.assertFalse(utils.is_full_a1_notation(""))

    def test_get_a1_from_absolute_range(self):
        """test get_a1_from_absolute_range function"""
        self.assertEqual(utils.get_a1_from_absolute_range("'Sheet1'!A1:B2"), "A1:B2")
        self.assertEqual(utils.get_a1_from_absolute_range("'Sheet1'!A1:B"), "A1:B")
        self.assertEqual(utils.get_a1_from_absolute_range("Sheet1!A1:B2"), "A1:B2")
        self.assertEqual(utils.get_a1_from_absolute_range("A1:B2"), "A1:B2")
        self.assertEqual(utils.get_a1_from_absolute_range("A1:B"), "A1:B")
        self.assertEqual(utils.get_a1_from_absolute_range("2"), "2")
