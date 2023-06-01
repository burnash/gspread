import itertools
import random
import re

import pytest

import gspread
import gspread.utils as utils
from gspread.exceptions import APIError, GSpreadException

from .conftest import I18N_STR, GspreadTest


class WorksheetTest(GspreadTest):

    """Test for gspread.Worksheet."""

    @pytest.fixture(scope="function", autouse=True)
    def init(self, client, request):
        name = self.get_temporary_spreadsheet_title(request.node.name)
        WorksheetTest.spreadsheet = client.create(name)
        WorksheetTest.sheet = WorksheetTest.spreadsheet.sheet1

        yield

        client.del_spreadsheet(WorksheetTest.spreadsheet.id)

    @pytest.fixture(autouse=True)
    @pytest.mark.vcr()
    def reset_sheet(self):
        WorksheetTest.sheet.clear()

    @pytest.mark.vcr()
    def test_acell(self):
        cell = self.sheet.acell("A1")
        self.assertTrue(isinstance(cell, gspread.cell.Cell))

    @pytest.mark.vcr()
    def test_cell(self):
        cell = self.sheet.cell(1, 1)
        self.assertTrue(isinstance(cell, gspread.cell.Cell))

    @pytest.mark.vcr()
    def test_range(self):
        cell_range1 = self.sheet.range("A1:A5")
        cell_range2 = self.sheet.range(1, 1, 5, 1)

        self.assertEqual(len(cell_range1), 5)

        for c1, c2 in zip(cell_range1, cell_range2):
            self.assertTrue(isinstance(c1, gspread.cell.Cell))
            self.assertTrue(isinstance(c2, gspread.cell.Cell))
            self.assertTrue(c1.col == c2.col)
            self.assertTrue(c1.row == c2.row)
            self.assertTrue(c1.value == c2.value)

    @pytest.mark.vcr()
    def test_range_unbounded(self):
        cell_range1 = self.sheet.range("A1:C")
        cell_range2 = self.sheet.range(1, 1, self.sheet.row_count, 3)
        tuples1 = [(c.row, c.col, c.value) for c in cell_range1]
        tuples2 = [(c.row, c.col, c.value) for c in cell_range2]
        self.assertSequenceEqual(tuples1, tuples2)

    @pytest.mark.vcr()
    def test_range_reversed(self):
        cell_range1 = self.sheet.range("A1:D4")
        cell_range2 = self.sheet.range("D4:A1")
        tuples1 = [(c.row, c.col, c.value) for c in cell_range1]
        tuples2 = [(c.row, c.col, c.value) for c in cell_range2]
        self.assertSequenceEqual(tuples1, tuples2)

    @pytest.mark.vcr()
    def test_range_get_all_values(self):
        self.sheet.resize(4, 4)
        rows = [
            ["", "Hi", "Mom", ""],
            ["My", "Name", "is", "bon"],
            ["", "", "", ""],
            ["1", "2", "3", "4"],
        ]

        self.sheet.update("A1:D4", rows)

        cell_range1 = self.sheet.range()
        cell_range2 = self.sheet.range("A1:D4")

        tuples1 = [(c.row, c.col, c.value) for c in cell_range1]
        tuples2 = [(c.row, c.col, c.value) for c in cell_range2]

        self.assertSequenceEqual(tuples1, tuples2)

    @pytest.mark.vcr()
    def test_update_acell(self):
        sg = self._sequence_generator()
        value = next(sg)

        self.sheet.update_acell("A2", value)
        self.assertEqual(self.sheet.acell("A2").value, value)

    @pytest.mark.vcr()
    def test_update_cell(self):
        sg = self._sequence_generator()
        value = next(sg)

        self.sheet.update_cell(1, 2, value)
        self.assertEqual(self.sheet.cell(1, 2).value, value)

        self.sheet.update_cell(1, 2, 42)
        self.assertEqual(self.sheet.cell(1, 2).value, "42")

        self.sheet.update_cell(1, 2, "0042")
        self.assertEqual(self.sheet.cell(1, 2).value, "42")

        self.sheet.update_cell(1, 2, 42.01)
        self.assertEqual(self.sheet.cell(1, 2).value, "42.01")

        self.sheet.update_cell(1, 2, "Артур")
        self.assertEqual(self.sheet.cell(1, 2).value, "Артур")

    @pytest.mark.vcr()
    def test_update_cell_multiline(self):
        sg = self._sequence_generator()
        value = next(sg)

        value = "{}\n{}".format(value, value)
        self.sheet.update_cell(1, 2, value)
        self.assertEqual(self.sheet.cell(1, 2).value, value)

    @pytest.mark.vcr()
    def test_update_cell_unicode(self):
        self.sheet.update_cell(1, 1, I18N_STR)

        cell = self.sheet.cell(1, 1)
        self.assertEqual(cell.value, I18N_STR)

    @pytest.mark.vcr()
    def test_update_cells(self):
        sg = self._sequence_generator()

        list_len = 10
        value_list = [next(sg) for i in range(list_len)]

        # Test multiline
        value_list[0] = "{}\n{}".format(value_list[0], value_list[0])

        range_label = "A1:A%s" % list_len
        cell_list = self.sheet.range(range_label)

        for c, v in zip(cell_list, value_list):
            c.value = v

        self.sheet.update_cells(cell_list)

        cell_list = self.sheet.range(range_label)

        for c, v in zip(cell_list, value_list):
            self.assertEqual(c.value, v)

    @pytest.mark.vcr()
    def test_update_cells_unicode(self):
        cell = self.sheet.cell(1, 1)
        cell.value = I18N_STR
        self.sheet.update_cells([cell])

        cell = self.sheet.cell(1, 1)
        self.assertEqual(cell.value, I18N_STR)

    @pytest.mark.vcr()
    def test_update_tab_color(self):
        # Assert that the method returns None.
        # Set the color.
        # Get the color.
        # Assert it contains each color, red, green, blue
        red_color = {
            "red": 1,
            "green": 0,
            "blue": 0,
        }
        self.assertEqual(self.sheet.tab_color, None)
        self.sheet.update_tab_color(red_color)
        self.assertEqual(self.sheet.tab_color, red_color)

    @pytest.mark.vcr()
    def test_update_cells_noncontiguous(self):
        sg = self._sequence_generator()

        num_rows = 6
        num_cols = 4

        rows = [[next(sg) for j in range(num_cols)] for i in range(num_rows)]

        cell_list = self.sheet.range("A1:D6")
        for cell, value in zip(cell_list, itertools.chain(*rows)):
            cell.value = value
        self.sheet.update_cells(cell_list)

        # Re-fetch cells
        cell_list = self.sheet.range("A1:D6")
        test_values = [c.value for c in cell_list]

        top_left = cell_list[0]
        bottom_right = cell_list[-1]

        top_left.value = top_left_value = next(sg) + " top_left"
        bottom_right.value = bottom_right_value = next(sg) + " bottom_right"

        self.sheet.update_cells([top_left, bottom_right])

        cell_list = self.sheet.range("A1:D6")
        read_values = [c.value for c in cell_list]
        test_values[0] = top_left_value
        test_values[-1] = bottom_right_value
        self.assertEqual(test_values, read_values)

    @pytest.mark.vcr()
    def test_update_cell_objects(self):
        test_values = ["cell row 1, col 2", "cell row 2 col 1"]

        cell_list = [
            gspread.cell.Cell(1, 2, test_values[0]),
            gspread.cell.Cell(2, 1, test_values[1]),
        ]
        self.sheet.update_cells(cell_list)

        # Re-fetch cells
        cell_list = (self.sheet.cell(1, 2), self.sheet.cell(2, 1))
        read_values = [c.value for c in cell_list]

        self.assertEqual(test_values, read_values)

    @pytest.mark.vcr()
    def test_resize(self):
        add_num = 10
        new_rows = self.sheet.row_count + add_num

        def get_grid_props():
            sheets = self.spreadsheet.fetch_sheet_metadata()["sheets"]
            return utils.finditem(
                lambda x: x["properties"]["sheetId"] == self.sheet.id, sheets
            )["properties"]["gridProperties"]

        self.sheet.add_rows(add_num)

        grid_props = get_grid_props()

        self.assertEqual(grid_props["rowCount"], new_rows)

        new_cols = self.sheet.col_count + add_num

        self.sheet.add_cols(add_num)

        grid_props = get_grid_props()

        self.assertEqual(grid_props["columnCount"], new_cols)

        new_rows -= add_num
        new_cols -= add_num
        self.sheet.resize(new_rows, new_cols)

        grid_props = get_grid_props()

        self.assertEqual(grid_props["rowCount"], new_rows)
        self.assertEqual(grid_props["columnCount"], new_cols)

    @pytest.mark.vcr()
    def test_sort(self):
        rows = [
            ["Apple", "2012", "4"],
            ["Banana", "2013", "3"],
            ["Canada", "2007", "1"],
            ["Dinosaur", "2013", "6"],
            ["Elephant", "2019", "2"],
            ["Fox", "2077", "5"],
        ]

        self.sheet.resize(6, 3)
        cell_list = self.sheet.range("A1:C6")
        for c, v in zip(cell_list, itertools.chain(*rows)):
            c.value = v
        self.sheet.update_cells(cell_list)

        specs = [
            (3, "asc"),
        ]
        self.sheet.sort(*specs, range="A1:C6")
        rows = sorted(rows, key=lambda x: int(x[2]), reverse=False)
        self.assertEqual(self.sheet.get_all_values(), rows)

        specs = [
            (1, "des"),
        ]
        self.sheet.sort(*specs, range="A1:C6")
        rows = sorted(rows, key=lambda x: x[0], reverse=True)
        self.assertEqual(self.sheet.get_all_values(), rows)

        specs = [
            (2, "asc"),
            (3, "asc"),
        ]
        self.sheet.sort(*specs, range="A1:C6")
        rows = sorted(rows, key=lambda x: (x[1], int(x[2])), reverse=False)
        self.assertEqual(self.sheet.get_all_values(), rows)

        specs = [
            (3, "asc"),
        ]
        self.sheet.sort(*specs)
        rows = sorted(rows, key=lambda x: int(x[2]), reverse=False)
        self.assertEqual(self.sheet.get_all_values(), rows)

        specs = [
            (3, "des"),
        ]
        self.sheet._properties["gridProperties"]["frozenRowCount"] = 1
        self.sheet.sort(*specs)
        rows = [rows[0]] + sorted(rows[1:], key=lambda x: int(x[2]), reverse=True)
        self.assertEqual(self.sheet.get_all_values(), rows)

    @pytest.mark.vcr()
    def test_freeze(self):
        freeze_cols = 1
        freeze_rows = 2

        def get_grid_props():
            sheets = self.spreadsheet.fetch_sheet_metadata()["sheets"]
            return utils.finditem(
                lambda x: x["properties"]["sheetId"] == self.sheet.id, sheets
            )["properties"]["gridProperties"]

        self.sheet.freeze(freeze_rows)

        grid_props = get_grid_props()

        self.assertEqual(grid_props["frozenRowCount"], freeze_rows)

        self.sheet.freeze(cols=freeze_cols)

        grid_props = get_grid_props()

        self.assertEqual(grid_props["frozenColumnCount"], freeze_cols)

        self.sheet.freeze(0, 0)

        grid_props = get_grid_props()

        self.assertTrue("frozenRowCount" not in grid_props)
        self.assertTrue("frozenColumnCount" not in grid_props)

    @pytest.mark.vcr()
    def test_basic_filters(self):
        def get_sheet():
            sheets = self.spreadsheet.fetch_sheet_metadata()["sheets"]
            return utils.finditem(
                lambda x: x["properties"]["sheetId"] == self.sheet.id, sheets
            )

        def get_basic_filter_range():
            return get_sheet()["basicFilter"]["range"]

        self.sheet.resize(20, 20)

        self.sheet.set_basic_filter()
        filter_range = get_basic_filter_range()

        self.assertEqual(filter_range["startRowIndex"], 0)
        self.assertEqual(filter_range["startColumnIndex"], 0)
        self.assertEqual(filter_range["endRowIndex"], 20)
        self.assertEqual(filter_range["endColumnIndex"], 20)

        self.sheet.set_basic_filter("B1:C2")
        filter_range = get_basic_filter_range()

        self.assertEqual(filter_range["startRowIndex"], 0)
        self.assertEqual(filter_range["startColumnIndex"], 1)
        self.assertEqual(filter_range["endRowIndex"], 2)
        self.assertEqual(filter_range["endColumnIndex"], 3)

        self.sheet.set_basic_filter(1, 2, 2, 3)
        filter_range = get_basic_filter_range()

        self.assertEqual(filter_range["startRowIndex"], 0)
        self.assertEqual(filter_range["startColumnIndex"], 1)
        self.assertEqual(filter_range["endRowIndex"], 2)
        self.assertEqual(filter_range["endColumnIndex"], 3)

        self.sheet.clear_basic_filter()
        self.assertTrue("basicFilter" not in get_sheet())

    @pytest.mark.vcr()
    def test_find(self):
        sg = self._sequence_generator()
        value = next(sg)

        self.sheet.update_cell(2, 10, value)
        self.sheet.update_cell(2, 11, value)

        cell = self.sheet.find(value)
        self.assertEqual(cell.value, value)

        value2 = next(sg)
        value = "{}o_O{}".format(value, value2)
        self.sheet.update_cell(2, 11, value)

        o_O_re = re.compile("[a-z]_[A-Z]%s" % value2)

        cell = self.sheet.find(o_O_re)
        self.assertEqual(cell.value, value)

        not_found = self.sheet.find("does not exists")
        self.assertIs(
            not_found, None, "find should return 'None' when value is not found"
        )

        lower_value = "camelcase"
        upper_value = "CamelCase"
        self.sheet.update_cell(2, 10, lower_value)
        self.sheet.update_cell(2, 11, upper_value)

        cell = self.sheet.find(upper_value, case_sensitive=False)
        self.assertEqual(cell.value, lower_value)

    @pytest.mark.vcr()
    def test_findall(self):
        list_len = 10
        range_label = "A1:A%s" % list_len
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
            char = chr(random.randrange(ord("a"), ord("z")))
            c.value = "{}{}_{}{}".format(c.value, char, char.upper(), value)

        self.sheet.update_cells(cell_list)

        o_O_re = re.compile("[a-z]_[A-Z]%s" % value)

        result_list = self.sheet.findall(o_O_re)

        self.assertEqual(list_len, len(result_list))

    @pytest.mark.vcr()
    def test_get_all_values(self):
        self.sheet.resize(4, 4)
        # put in new values
        rows = [
            ["A1", "B1", "", "D1"],
            ["", "b2", "", ""],
            ["", "", "", ""],
            ["A4", "B4", "", "D4"],
        ]
        cell_list = self.sheet.range("A1:D1")

        cell_list.extend(self.sheet.range("A2:D2"))
        cell_list.extend(self.sheet.range("A3:D3"))
        cell_list.extend(self.sheet.range("A4:D4"))
        for cell, value in zip(cell_list, itertools.chain(*rows)):
            cell.value = value
        self.sheet.update_cells(cell_list)

        # read values with get_all_values, get a list of lists
        read_data = self.sheet.get_all_values()
        # values should match with original lists
        self.assertEqual(read_data, rows)

    @pytest.mark.vcr()
    def test_get_all_values_title_is_a1_notation(self):
        self.sheet.resize(4, 4)
        # renames sheet to contain single and double quotes
        self.sheet.update_title("D3")
        # put in new values
        rows = [
            ["A1", "B1", "", "D1"],
            ["", "b2", "", ""],
            ["", "", "", ""],
            ["A4", "B4", "", "d4"],
        ]
        cell_list = self.sheet.range("A1:D1")

        cell_list.extend(self.sheet.range("A2:D2"))
        cell_list.extend(self.sheet.range("A3:D3"))
        cell_list.extend(self.sheet.range("A4:D4"))
        for cell, value in zip(cell_list, itertools.chain(*rows)):
            cell.value = value
        self.sheet.update_cells(cell_list)

        # read values with get_all_values, get a list of lists
        read_data = self.sheet.get_all_values()
        # values should match with original lists
        self.assertEqual(read_data, rows)

    @pytest.mark.vcr()
    def test_get_all_records(self):
        self.sheet.resize(4, 4)
        # put in new values
        rows = [
            ["A1", "B1", "", "D1"],
            [1, "b2", 1.45, ""],
            ["", "", "", ""],
            ["A4", 0.4, "", 4],
        ]
        cell_list = self.sheet.range("A1:D4")
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
        read_records = self.sheet.get_all_records(default_blank="foo")
        d1 = dict(zip(rows[0], ("foo", "foo", "foo", "foo")))
        self.assertEqual(read_records[1], d1)

    @pytest.mark.vcr()
    def test_get_all_records_different_header(self):
        self.sheet.resize(6, 4)
        # put in new values
        rows = [
            ["", "", "", ""],
            ["", "", "", ""],
            ["A1", "B1", "", "D1"],
            [1, "b2", 1.45, ""],
            ["", "", "", ""],
            ["A4", 0.4, "", 4],
        ]
        cell_list = self.sheet.range("A1:D6")
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
        read_records = self.sheet.get_all_records(default_blank="foo", head=3)
        d1 = dict(zip(rows[2], ("foo", "foo", "foo", "foo")))
        self.assertEqual(read_records[1], d1)

    @pytest.mark.vcr()
    def test_get_all_records_value_render_options(self):
        self.sheet.resize(2, 4)
        # put in new values
        rows = [
            ["=4/2", "2020-01-01", "string", 53],
            ["=3/2", 0.12, "1999-01-02", ""],
        ]
        cell_list = self.sheet.range("A1:D2")
        for cell, value in zip(cell_list, itertools.chain(*rows)):
            cell.value = value
        self.sheet.update_cells(
            cell_list, value_input_option=utils.ValueInputOption.user_entered
        )

        # default, formatted read
        read_records = self.sheet.get_all_records()
        expected_keys = ["2", "2020-01-01", "string", "53"]
        expected_values = [3 / 2, 0.12, "1999-01-02", ""]
        d0 = dict(zip(expected_keys, expected_values))
        self.assertEqual(read_records[0], d0)

        # unformatted read
        read_records = self.sheet.get_all_records(
            value_render_option=utils.ValueRenderOption.unformatted
        )
        expected_keys = [2, 43831, "string", 53]
        expected_values = [3 / 2, 0.12, 36162, ""]
        d0 = dict(zip(expected_keys, expected_values))
        self.assertEqual(read_records[0], d0)

        # formula read
        read_records = self.sheet.get_all_records(
            value_render_option=utils.ValueRenderOption.formula
        )
        expected_keys = ["=4/2", 43831, "string", 53]
        expected_values = ["=3/2", 0.12, 36162, ""]
        d0 = dict(zip(expected_keys, expected_values))
        self.assertEqual(read_records[0], d0)

    @pytest.mark.vcr()
    def test_get_all_records_duplicate_keys(self):
        self.sheet.resize(4, 4)
        # put in new values
        rows = [
            ["A1", "A1", "", "D1"],
            [1, "b2", 1.45, ""],
            ["", "", "", ""],
            ["A4", 0.4, "", 4],
        ]
        cell_list = self.sheet.range("A1:D4")
        for cell, value in zip(cell_list, itertools.chain(*rows)):
            cell.value = value
        self.sheet.update_cells(cell_list)

        with pytest.raises(GSpreadException):
            self.sheet.get_all_records()

    @pytest.mark.vcr(allow_playback_repeats=True)
    def test_get_all_records_expected_headers(self):
        self.sheet.resize(4, 4)

        # put in new values
        rows = [
            ["A1", "B2", "C3", "D4"],
            [1, "b2", 1.45, ""],
            ["", "", "", ""],
            ["A4", 0.4, "", 4],
        ]
        cell_list = self.sheet.range("A1:D4")
        for cell, value in zip(cell_list, itertools.chain(*rows)):
            cell.value = value
        self.sheet.update_cells(cell_list)

        # check non uniques expected headers
        expected_headers = ["A1", "A1"]
        with pytest.raises(GSpreadException):
            self.sheet.get_all_records(expected_headers=expected_headers)

        # check extra headers
        expected_headers = ["A1", "E5"]
        with pytest.raises(GSpreadException):
            self.sheet.get_all_records(expected_headers=expected_headers)

        # check nominal case.
        expected_headers = ["A1", "C3"]
        read_records = self.sheet.get_all_records(
            expected_headers=expected_headers,
        )

        expected_values_1 = dict(zip(rows[0], rows[1]))
        expected_values_2 = dict(zip(rows[0], rows[2]))
        expected_values_3 = dict(zip(rows[0], rows[3]))
        self.assertDictEqual(expected_values_1, read_records[0])
        self.assertDictEqual(expected_values_2, read_records[1])
        self.assertDictEqual(expected_values_3, read_records[2])

    @pytest.mark.vcr()
    def test_get_all_records_numericise_unformatted(self):
        self.sheet.resize(2, 4)
        # put in new values, made from three lists
        rows = [
            ["A", "", "C", "3_1_0"],
            ["=3/2", 0.12, "", "3_2_1"],
        ]
        cell_list = self.sheet.range("A1:D2")
        for cell, value in zip(cell_list, itertools.chain(*rows)):
            cell.value = value
        self.sheet.update_cells(
            cell_list, value_input_option=utils.ValueInputOption.user_entered
        )

        read_records = self.sheet.get_all_records(
            default_blank="empty",
            allow_underscores_in_numeric_literals=True,
            value_render_option=utils.ValueRenderOption.unformatted,
        )
        expected_values = [3 / 2, 0.12, "empty", 321]
        d0 = dict(zip(rows[0], expected_values))
        self.assertEqual(read_records[0], d0)

    @pytest.mark.vcr()
    def test_append_row(self):
        sg = self._sequence_generator()
        value_list = [next(sg) for i in range(10)]
        self.sheet.append_row(value_list)
        read_values = self.sheet.row_values(1)
        self.assertEqual(value_list, read_values)

    @pytest.mark.vcr()
    def test_append_row_with_empty_value(self):
        sg = self._sequence_generator()
        value_list = [next(sg) for i in range(3)]
        value_list[1] = ""  # Skip one cell to create two "tables" as in #537
        self.sheet.append_row(value_list)
        # Append it again
        self.sheet.append_row(value_list)
        # This should produce a shift in rows as in #537
        shifted_value_list = ["", ""] + value_list
        read_values = self.sheet.row_values(2)
        self.assertEqual(shifted_value_list, read_values)

    @pytest.mark.vcr()
    def test_append_row_with_empty_value_and_table_range(self):
        sg = self._sequence_generator()
        value_list = [next(sg) for i in range(3)]
        value_list[1] = ""  # Skip one cell to create two "tables" as in #537
        self.sheet.append_row(value_list)
        # Append it again
        self.sheet.append_row(value_list, table_range="A1")
        # This should produce no shift in rows
        # contrary to test_append_row_with_empty_value
        read_values = self.sheet.row_values(2)
        self.assertEqual(value_list, read_values)

    @pytest.mark.vcr()
    def test_insert_row(self):
        sg = self._sequence_generator()

        num_rows = 6
        num_cols = 4

        rows = [[next(sg) for j in range(num_cols)] for i in range(num_rows)]

        cell_list = self.sheet.range("A1:D6")
        for cell, value in zip(cell_list, itertools.chain(*rows)):
            cell.value = value
        self.sheet.update_cells(cell_list)

        new_row_values = [next(sg) for i in range(num_cols + 4)]
        self.sheet.insert_row(new_row_values, 2)
        read_values = self.sheet.row_values(2)
        self.assertEqual(new_row_values, read_values)

        formula = "=1+1"
        self.sheet.update_acell("B2", formula)
        values = [next(sg) for i in range(num_cols + 4)]
        self.sheet.insert_row(values, 1)
        b3 = self.sheet.acell("B3", value_render_option=utils.ValueRenderOption.formula)
        self.assertEqual(b3.value, formula)

        new_row_values = [next(sg) for i in range(num_cols + 4)]
        with pytest.raises(GSpreadException):
            self.sheet.insert_row(new_row_values, 1, inherit_from_before=True)

    @pytest.mark.vcr()
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

    @pytest.mark.vcr()
    def test_clear(self):
        rows = [
            ["", "", "", ""],
            ["", "", "", ""],
            ["A1", "B1", "", "D1"],
            [1, "b2", 1.45, ""],
            ["", "", "", ""],
            ["A4", 0.4, "", 4],
        ]

        cell_list = self.sheet.range("A1:D6")
        for cell, value in zip(cell_list, itertools.chain(*rows)):
            cell.value = value
        self.sheet.update_cells(cell_list)

        self.sheet.clear()
        self.assertEqual(self.sheet.get_all_values(), [])

    @pytest.mark.vcr()
    def test_update_and_get(self):
        values = [
            ["A1", "B1", "", "D1"],
            ["", "b2", "", ""],
            ["", "", "", ""],
            ["A4", "B4", "", "D4"],
        ]

        self.sheet.update("A1", values)

        read_data = self.sheet.get("A1:D4")

        self.assertEqual(
            read_data, [["A1", "B1", "", "D1"], ["", "b2"], [], ["A4", "B4", "", "D4"]]
        )

    @pytest.mark.vcr()
    def test_batch_get(self):
        values = [
            ["A1", "B1", "", "D1"],
            ["", "b2", "", ""],
            ["", "", "", ""],
            ["A4", "B4", "", "D4"],
        ]

        self.sheet.update("A1", values)

        value_ranges = self.sheet.batch_get(["A1:B1", "B4:D4"])

        self.assertEqual(value_ranges, [[["A1", "B1"]], [["B4", "", "D4"]]])
        self.assertEqual(value_ranges[0].range, "Sheet1!A1:B1")
        self.assertEqual(value_ranges[1].range, "Sheet1!B4:D4")
        self.assertEqual(value_ranges[0].first(), "A1")

    @pytest.mark.vcr()
    def test_batch_update(self):
        self.sheet.batch_update(
            [
                {
                    "range": "A1:D1",
                    "values": [["A1", "B1", "", "D1"]],
                },
                {
                    "range": "A4:D4",
                    "values": [["A4", "B4", "", "D4"]],
                },
            ]
        )

        data = self.sheet.get("A1:D4")

        self.assertEqual(data, [["A1", "B1", "", "D1"], [], [], ["A4", "B4", "", "D4"]])

    @pytest.mark.vcr()
    def test_format(self):
        cell_format = {
            "backgroundColor": {"green": 1, "blue": 1},
            "horizontalAlignment": "CENTER",
            "textFormat": {
                "foregroundColor": {
                    "red": 1,
                    "green": 1,
                },
                "fontSize": 12,
                "bold": True,
            },
        }
        self.maxDiff = None
        self.sheet.format("A2:B2", cell_format)

        data = self.spreadsheet._spreadsheets_get(
            {
                "includeGridData": False,
                "ranges": ["Sheet1!A2"],
                "fields": "sheets.data.rowData.values.userEnteredFormat",
            }
        )

        uef = data["sheets"][0]["data"][0]["rowData"][0]["values"][0][
            "userEnteredFormat"
        ]

        del uef["backgroundColorStyle"]
        del uef["textFormat"]["foregroundColorStyle"]

        self.assertEqual(uef, cell_format)

    @pytest.mark.vcr()
    def test_reorder_worksheets(self):
        w = self.spreadsheet.worksheets()
        w.reverse()
        self.spreadsheet.reorder_worksheets(w)
        self.assertEqual(
            [i.id for i in w], [i.id for i in self.spreadsheet.worksheets()]
        )

    @pytest.mark.vcr()
    def test_worksheet_update_index(self):
        w = self.spreadsheet.worksheets()
        last_sheet = w[-1]
        last_sheet.update_index(0)
        w = self.spreadsheet.worksheets()
        self.assertEqual(w[0].id, last_sheet.id)

    @pytest.mark.vcr()
    def test_worksheet_notes(self):
        w = self.spreadsheet.worksheets()[0]

        # will trigger a Exception in case of any issue
        self.assertEqual(w.get_note("A1"), "")
        test_note_string = "slim shaddy"
        w.insert_note("A1", test_note_string)
        self.assertEqual(w.get_note("A1"), test_note_string)
        update_note = "the real " + test_note_string
        w.update_note("A1", update_note)
        self.assertEqual(w.get_note("A1"), update_note)
        w.clear_note("A1")
        self.assertEqual(w.get_note("A1"), "")

        notes = {"A1": "read my note", "B2": "Or don't"}

        w.insert_notes(notes)
        self.assertEqual(w.get_note("A1"), notes["A1"])
        self.assertEqual(w.get_note("B2"), notes["B2"])

        notes["A1"] = "remember to clean bedroom"
        notes["B2"] = "do homeworks"
        w.update_notes(notes)
        self.assertEqual(w.get_note("A1"), notes["A1"])
        self.assertEqual(w.get_note("B2"), notes["B2"])

        w.clear_notes(["A1", "B2"])

        with self.assertRaises(TypeError) as _:
            w.insert_note("A1", 42)
            w.insert_note("A1", ["asddf", "asdfqwebn"])
            w.insert_note("A1", w)

    @pytest.mark.vcr()
    def test_batch_clear(self):
        w = self.spreadsheet.sheet1

        # make sure cells are empty
        self.assertListEqual(w.get_values("A1:B1"), [])
        self.assertListEqual(w.get_values("C2:E2"), [])

        # fill the cells
        w.update("A1:B1", [["12345", "ThisIsText"]])
        w.update("C2:E2", [["5678", "Second", "Text"]])

        # confirm the cells are not empty
        self.assertNotEqual(w.get_values("A1:B1"), [])
        self.assertNotEqual(w.get_values("C2:E2"), [])

        # empty both cell range at once
        w.batch_clear(["A1:B1", "C2:E2"])

        # confirm cells are empty
        # make sure cells are empty
        self.assertListEqual(w.get_values("A1:B1"), [])
        self.assertListEqual(w.get_values("C2:E2"), [])

    @pytest.mark.vcr()
    def test_group_columns(self):
        w = self.sheet
        w.add_dimension_group_columns(0, 2)

        col_groups = self.sheet.list_dimension_group_columns()

        range = col_groups[0]["range"]
        self.assertEqual(range["dimension"], utils.Dimension.cols)
        self.assertEqual(range["startIndex"], 0)
        self.assertEqual(range["endIndex"], 2)

        self.sheet.delete_dimension_group_columns(0, 2)

        col_groups = self.sheet.list_dimension_group_columns()
        self.assertEqual(col_groups, [])

    @pytest.mark.vcr()
    def test_group_rows(self):
        w = self.sheet
        w.add_dimension_group_rows(0, 2)

        row_groups = self.sheet.list_dimension_group_rows()

        range = row_groups[0]["range"]
        self.assertEqual(range["dimension"], utils.Dimension.rows)
        self.assertEqual(range["startIndex"], 0)
        self.assertEqual(range["endIndex"], 2)

        self.sheet.delete_dimension_group_rows(0, 2)

        row_groups = self.sheet.list_dimension_group_rows()
        self.assertEqual(row_groups, [])

    @pytest.mark.vcr()
    def test_hide_columns_rows(self):
        w = self.sheet

        # This is hard to verify
        # simply make the HTTP request to make sure it does not fail
        w.hide_columns(0, 2)
        w.unhide_columns(0, 2)

        w.hide_rows(0, 2)
        w.unhide_rows(0, 2)

    @pytest.mark.vcr()
    def test_hide_show_worksheet(self):
        """We can't retrieve this property from the API
        see issue: https://issuetracker.google.com/issues/229298342

        We can only send the request and make sure it works.
        This is a trivial method, using recorded cassettes it will never fail.
        But next time we refresh the cassette it will make the real request."""

        # you cannot hide all worksheet in a document
        with pytest.raises(APIError):
            self.sheet.hide()

        new_sheet = self.spreadsheet.add_worksheet("you cannot see me", 2, 2)

        # as describe in https://issuetracker.google.com/issues/229298342
        # the response does not include some default values.
        # if missing => value is False
        res = self.spreadsheet.fetch_sheet_metadata()
        before_hide = res["sheets"][1]["properties"].get("hidden", False)
        self.assertFalse(before_hide)

        new_sheet.hide()

        res = self.spreadsheet.fetch_sheet_metadata()
        after_hide = res["sheets"][1]["properties"].get("hidden", False)
        self.assertTrue(after_hide)

        new_sheet.show()
        res = self.spreadsheet.fetch_sheet_metadata()
        before_hide = res["sheets"][1]["properties"].get("hidden", False)
        self.assertFalse(before_hide)

    @pytest.mark.vcr()
    def test_hide_gridlines(self):
        """Hide gridlines. Check API to see if they are hidden."""

        def are_gridlines_hidden():
            res = self.spreadsheet.fetch_sheet_metadata()
            sheets = res["sheets"]
            sheet = utils.finditem(
                lambda x: x["properties"]["sheetId"] == self.sheet.id,
                sheets,
            )
            return (
                sheet["properties"]
                .get("gridProperties", {})
                .get("hideGridlines", False)
            )

        hidden_before = are_gridlines_hidden()
        hidden_before_property = self.sheet.is_gridlines_hidden

        self.sheet.hide_gridlines()

        hidden_after = are_gridlines_hidden()
        hidden_after_property = self.sheet.is_gridlines_hidden

        self.assertFalse(hidden_before)
        self.assertFalse(hidden_before_property)
        self.assertTrue(hidden_after)
        self.assertTrue(hidden_after_property)

    @pytest.mark.vcr()
    def test_show_gridlines(self):
        """Show gridlines. Check API to see if they are shown."""

        def are_gridlines_hidden():
            res = self.spreadsheet.fetch_sheet_metadata()
            sheets = res["sheets"]
            sheet = utils.finditem(
                lambda x: x["properties"]["sheetId"] == self.sheet.id,
                sheets,
            )
            return (
                sheet["properties"]
                .get("gridProperties", {})
                .get("hideGridlines", False)
            )

        hidden_before = are_gridlines_hidden()
        hidden_before_property = self.sheet.is_gridlines_hidden

        self.sheet.hide_gridlines()
        self.sheet.show_gridlines()

        hidden_after = are_gridlines_hidden()
        hidden_after_property = self.sheet.is_gridlines_hidden

        self.assertFalse(hidden_before)
        self.assertFalse(hidden_before_property)
        self.assertFalse(hidden_after)
        self.assertFalse(hidden_after_property)

    @pytest.mark.vcr()
    def test_auto_resize_columns(self):
        w = self.sheet

        # we can only check the result of `auto_resize_columns`
        # using only code and the API.
        # To test `auto_resize_row` we must use a web browser and
        # force the size of a row then auto resize it using gspread.

        # insert enough text to make it larger than the column
        w.update_acell("A1", "A" * 1024)

        # request only what we are looking for
        params = {"fields": "sheets.data.columnMetadata"}
        res = self.spreadsheet.fetch_sheet_metadata(params=params)
        size_before = res["sheets"][0]["data"][0]["columnMetadata"][0]["pixelSize"]

        # auto resize the first column
        w.columns_auto_resize(0, 1)

        res = self.spreadsheet.fetch_sheet_metadata(params=params)
        size_after = res["sheets"][0]["data"][0]["columnMetadata"][0]["pixelSize"]

        self.assertGreater(size_after, size_before)

    @pytest.mark.vcr()
    def test_copy_cut_range(self):
        w = self.sheet

        # init the sheet values
        values = [["A1"], ["A2"]]
        w.update("A1:A2", values)

        # copy the values
        w.copy_range("A1:A2", "B1:B2")

        # check the copied values
        cells = w.range("B1:B2")
        self.assertListEqual(
            list(itertools.chain(*values)), [cell.value for cell in cells]
        )

        # cut the original values in A1:A2
        w.cut_range("A1:A2", "C1")

        # check the values have moved
        cells = w.range("A1:A2")
        self.assertListEqual([cell.value for cell in cells], ["", ""])

        cells = w.range("C1:C2")
        self.assertListEqual(
            list(itertools.chain(*values)),
            [cell.value for cell in cells],
        )
