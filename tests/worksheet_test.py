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
        WorksheetTest.sheet: gspread.worksheet.Worksheet = (
            WorksheetTest.spreadsheet.sheet1
        )

        yield

        client.del_spreadsheet(WorksheetTest.spreadsheet.id)

    @pytest.fixture(autouse=True)
    @pytest.mark.vcr()
    def reset_sheet(self):
        WorksheetTest.sheet.clear()

    @pytest.mark.vcr()
    def test_acell(self):
        cell = self.sheet.acell("A1")
        self.assertIsInstance(cell, gspread.cell.Cell)

    @pytest.mark.vcr()
    def test_cell(self):
        cell = self.sheet.cell(1, 1)
        self.assertIsInstance(cell, gspread.cell.Cell)

    @pytest.mark.vcr()
    def test_range(self):
        cell_range1 = self.sheet.range("A1:A5")
        cell_range2 = self.sheet.range(1, 1, 5, 1)

        self.assertEqual(len(cell_range1), 5)

        for c1, c2 in zip(cell_range1, cell_range2):
            self.assertIsInstance(c1, gspread.cell.Cell)
            self.assertIsInstance(c2, gspread.cell.Cell)
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
    def test_get_values_and_combine_merged_cells(self):
        self.sheet.resize(4, 4)
        sheet_data = [
            ["1", "", "", ""],
            ["", "", "title", ""],
            ["", "", "2", ""],
            ["num", "val", "", "0"],
        ]

        self.sheet.update("A1:D4", sheet_data)

        self.sheet.merge_cells("A1:B2")
        self.sheet.merge_cells("C2:D2")
        self.sheet.merge_cells("C3:C4")

        expected_merge = [
            ["1", "1", "", ""],
            ["1", "1", "title", "title"],
            ["", "", "2", ""],
            ["num", "val", "2", "0"],
        ]

        values = self.sheet.get_values()
        values_with_merged = self.sheet.get_values(combine_merged_cells=True)

        self.assertEqual(values, sheet_data)
        self.assertEqual(values_with_merged, expected_merge)

        # test with cell address
        values_with_merged = self.sheet.get_values("A1:D4", combine_merged_cells=True)
        self.assertEqual(values_with_merged, expected_merge)

    @pytest.mark.vcr()
    def test_get_values_merge_cells_outside_of_range(self):
        self.sheet.resize(4, 4)
        sheet_data = [
            ["1", "2", "4", ""],
            ["down", "", "", ""],
            ["", "", "2", ""],
            ["num", "val", "", "0"],
        ]

        self.sheet.update("A1:D4", sheet_data)

        self.sheet.merge_cells("A2:A3")
        self.sheet.merge_cells("C1:D2")

        REQUEST_RANGE = "A1:B2"
        expected_values = [
            ["1", "2"],
            ["down", ""],
        ]

        values_with_merged = self.sheet.get_values(
            REQUEST_RANGE, combine_merged_cells=True
        )
        self.assertEqual(values_with_merged, expected_values)

    @pytest.mark.vcr()
    def test_get_values_merge_cells_from_centre_of_sheet(self):
        self.sheet.resize(4, 3)
        sheet_data = [
            ["1", "2", "4"],
            ["down", "up", ""],
            ["", "", "2"],
            ["num", "val", ""],
        ]
        self.sheet.update("A1:C4", sheet_data)
        self.sheet.merge_cells("A2:A3")
        self.sheet.merge_cells("C1:C2")

        REQUEST_RANGE = "B1:C3"
        expected_values = [
            ["2", "4"],
            ["up", "4"],
            ["", "2"],
        ]

        values_with_merged = self.sheet.get_values(
            REQUEST_RANGE, combine_merged_cells=True
        )
        self.assertEqual(values_with_merged, expected_values)

    @pytest.mark.vcr()
    def test_get_values_merge_cells_with_named_range(self):
        self.sheet.resize(4, 3)
        sheet_data = [
            ["1", "2", "4"],
            ["down", "up", ""],
            ["", "", "2"],
            ["num", "val", ""],
        ]
        self.sheet.update("A1:C4", sheet_data)
        self.sheet.merge_cells("A2:A3")
        self.sheet.merge_cells("C1:C2")

        request_range = "NamedRange"
        self.sheet.define_named_range("B1:C3", request_range)
        expected_values = [
            ["2", "4"],
            ["up", "4"],
            ["", "2"],
        ]

        values_with_merged = self.sheet.get_values(
            request_range, combine_merged_cells=True
        )
        self.assertEqual(values_with_merged, expected_values)

    @pytest.mark.vcr()
    def test_get_values_and_maintain_size(self):
        """test get_values with maintain_size=True"""
        self.sheet.resize(5, 5)
        sheet_data = [
            ["1", "2", "", "", ""],
            ["3", "4", "", "", ""],
            ["5", "6", "", "", ""],
            ["", "", "", "", ""],
            ["", "", "", "", ""],
        ]
        request_range = "A1:D4"
        expected_values = [
            ["1", "2", "", ""],
            ["3", "4", "", ""],
            ["5", "6", "", ""],
            ["", "", "", ""],
        ]

        self.sheet.update("A1:E5", sheet_data)

        values = self.sheet.get_values(request_range, maintain_size=True)

        self.assertEqual(values, expected_values)

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
    def test_update_title(self):
        res = self.spreadsheet.fetch_sheet_metadata()
        title_before = res["sheets"][0]["properties"]["title"]
        title_before_prop = self.sheet.title

        new_title = "I'm a new title"
        self.sheet.update_title(new_title)

        res = self.spreadsheet.fetch_sheet_metadata()
        title_after = res["sheets"][0]["properties"]["title"]
        title_after_prop = self.sheet.title

        self.assertEqual(title_after, new_title)
        self.assertEqual(title_after_prop, new_title)
        self.assertNotEqual(title_before, new_title)
        self.assertNotEqual(title_before_prop, new_title)

    @pytest.mark.vcr()
    def test_update_tab_color(self):
        # Set the color.
        # Get the color.
        # Assert the color is the set and changed by google.
        pink_color = {
            "red": 1,
            "green": 0,
            "blue": 0.5,
        }
        # if a color is 0, it is not returned by google
        # also, floats are coalesced to the closest 8-bit value
        #   so 0.5 becomes 0.49803922 (127/255)
        pink_color_from_google = {
            "red": 1,
            "blue": 0.49803922,  # 127/255
        }

        params = {"fields": "sheets.properties.tabColorStyle"}
        res = self.spreadsheet.fetch_sheet_metadata(params=params)
        color_before = (
            res["sheets"][0]["properties"]
            .get("tabColorStyle", {})
            .get("rgbColor", None)
        )
        color_param_before = self.sheet.tab_color
        color_hex_before = self.sheet.get_tab_color()

        self.sheet.update_tab_color(pink_color)

        res = self.spreadsheet.fetch_sheet_metadata(params=params)
        color_after = (
            res["sheets"][0]["properties"]
            .get("tabColorStyle", {})
            .get("rgbColor", None)
        )
        color_param_after = self.sheet.tab_color
        color_hex_after = self.sheet.get_tab_color()

        # params are set to whatever the user sets them to
        # google returns the closest 8-bit value
        # so these are different
        self.assertEqual(color_before, None)
        self.assertEqual(color_param_before, None)
        self.assertEqual(color_hex_before, None)
        self.assertEqual(color_after, pink_color_from_google)
        self.assertEqual(color_param_after, pink_color)
        self.assertEqual(color_hex_after, "#FF0080")

    @pytest.mark.vcr()
    def test_clear_tab_color(self):
        # Set the color.
        # Clear the color.
        # Assert that the color is None.
        pink_color = {
            "red": 1,
            "green": 0,
            "blue": 0.5,
        }

        params = {"fields": "sheets.properties.tabColorStyle"}
        res = self.spreadsheet.fetch_sheet_metadata(params=params)
        color_before = (
            res["sheets"][0]["properties"]
            .get("tabColorStyle", {})
            .get("rgbColor", None)
        )
        color_param_before = self.sheet.tab_color

        self.sheet.update_tab_color(pink_color)
        self.sheet.clear_tab_color()

        res = self.spreadsheet.fetch_sheet_metadata(params=params)
        color_after = (
            res["sheets"][0]["properties"]
            .get("tabColorStyle", {})
            .get("rgbColor", None)
        )
        color_param_after = self.sheet.tab_color

        self.assertEqual(color_before, None)
        self.assertEqual(color_param_before, None)
        self.assertEqual(color_after, None)
        self.assertEqual(color_param_after, None)

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
        self.assertEqual(self.sheet.row_count, new_rows)

        new_cols = self.sheet.col_count + add_num
        self.sheet.add_cols(add_num)

        grid_props = get_grid_props()
        self.assertEqual(grid_props["columnCount"], new_cols)
        self.assertEqual(self.sheet.col_count, new_cols)

        new_rows -= add_num
        new_cols -= add_num
        self.sheet.resize(new_rows, new_cols)

        grid_props = get_grid_props()
        self.assertEqual(grid_props["rowCount"], new_rows)
        self.assertEqual(grid_props["columnCount"], new_cols)
        self.assertEqual(self.sheet.row_count, new_rows)
        self.assertEqual(self.sheet.col_count, new_cols)

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
        self.assertEqual(self.sheet.frozen_row_count, freeze_rows)

        self.sheet.freeze(cols=freeze_cols)

        grid_props = get_grid_props()
        self.assertEqual(grid_props["frozenColumnCount"], freeze_cols)
        self.assertEqual(self.sheet.frozen_col_count, freeze_cols)

        self.sheet.freeze(0, 0)

        grid_props = get_grid_props()
        self.assertTrue("frozenRowCount" not in grid_props)
        self.assertTrue("frozenColumnCount" not in grid_props)
        self.assertEqual(self.sheet.frozen_row_count, 0)
        self.assertEqual(self.sheet.frozen_col_count, 0)

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
    def test_get_all_values_date_time_render_options(self):
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

        # with value_render as unformatted
        # date_time_render as serial_number
        read_records = self.sheet.get_values(
            value_render_option=utils.ValueRenderOption.unformatted,
            date_time_render_option=utils.DateTimeOption.serial_number,
        )
        expected_values = [
            [2, 43831, "string", 53],
            [3 / 2, 0.12, 36162, ""],
        ]
        self.assertEqual(read_records, expected_values)

        # with value_render as unformatted
        # date_time_render as formatted_string
        read_records = self.sheet.get_values(
            value_render_option=utils.ValueRenderOption.unformatted,
            date_time_render_option=utils.DateTimeOption.formatted_string,
        )
        expected_values = [
            [2, "2020-01-01", "string", 53],
            [3 / 2, 0.12, "1999-01-02", ""],
        ]
        self.assertEqual(read_records, expected_values)

        # with value_render as formatted (overrides date_time_render)
        # date_time_render as serial_number
        read_records = self.sheet.get_values(
            value_render_option=utils.ValueRenderOption.formatted,
            date_time_render_option=utils.DateTimeOption.serial_number,
        )
        expected_values = [
            ["2", "2020-01-01", "string", "53"],
            ["1.5", "0.12", "1999-01-02", ""],
        ]
        self.assertEqual(read_records, expected_values)

        # with value_render as formatted (overrides date_time_render)
        # date_time_render as formatted_string
        read_records = self.sheet.get_values(
            value_render_option=utils.ValueRenderOption.formatted,
            date_time_render_option=utils.DateTimeOption.formatted_string,
        )
        expected_values = [
            ["2", "2020-01-01", "string", "53"],
            ["1.5", "0.12", "1999-01-02", ""],
        ]
        self.assertEqual(read_records, expected_values)

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
        self.sheet.update("A1:D4", rows)

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
        self.sheet.update("A1:D6", rows)

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
            ["A1", "faff", "C3", "faff"],
            [1, "b2", 1.45, ""],
            ["", "", "", ""],
            ["A4", 0.4, "", 4],
        ]
        self.sheet.update("A1:D4", rows)

        # check no expected headers
        with pytest.raises(GSpreadException):
            self.sheet.get_all_records()

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
    def test_get_all_records_with_blank_final_headers(self):
        # regression test for #590, #629, #1354
        self.sheet.resize(4, 4)

        # put in new values
        rows = [
            ["A1", "faff", "", ""],
            [1, "b2", 1.45, ""],
            ["", "", "", ""],
            ["A4", 0.4, "", 4],
        ]
        self.sheet.update("A1:D4", rows)

        with pytest.raises(GSpreadException):
            self.sheet.get_all_records()

        expected_headers = []
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
    def test_get_all_records_with_keys_blank(self):
        # regression test for #1355
        self.sheet.resize(4, 4)

        rows = [
            ["", "", "", ""],
            ["c", "d", "e", "f"],
            ["g", "h", "i", "j"],
            ["k", "l", "m", ""],
        ]
        cell_list = self.sheet.range("A1:D4")
        for cell, value in zip(cell_list, itertools.chain(*rows)):
            cell.value = value
        self.sheet.update_cells(cell_list)

        # duplicate headers
        with pytest.raises(GSpreadException):
            self.sheet.get_all_records()

        # ignore duplicate headers
        read_records = self.sheet.get_all_records(expected_headers=[])

        expected_values_1 = dict(zip(rows[0], rows[1]))
        expected_values_2 = dict(zip(rows[0], rows[2]))
        expected_values_3 = dict(zip(rows[0], rows[3]))
        self.assertDictEqual(expected_values_1, read_records[0])
        self.assertDictEqual(expected_values_2, read_records[1])
        self.assertDictEqual(expected_values_3, read_records[2])

    @pytest.mark.vcr()
    def test_get_records_with_all_values_blank(self):
        # regression test for #1355
        self.sheet.resize(4, 4)

        rows = [
            ["a", "b", "c", "d"],
            ["", "", "", ""],
            ["", "", "", ""],
            ["", "", "", ""],
        ]
        self.sheet.update("A1:D4", rows)

        expected_values_1 = dict(zip(rows[0], rows[1]))
        expected_values_2 = dict(zip(rows[0], rows[2]))
        expected_values_3 = dict(zip(rows[0], rows[3]))

        # I ask for get_records(first_index=2, last_index=4)
        # I want [{...}, {...}, {...}]

        read_records_first_last = self.sheet.get_records(first_index=2, last_index=4)
        self.assertEqual(len(read_records_first_last), 3)
        self.assertDictEqual(expected_values_1, read_records_first_last[0])
        self.assertDictEqual(expected_values_2, read_records_first_last[1])
        self.assertDictEqual(expected_values_3, read_records_first_last[2])

        # I ask for get_records()
        # I want []
        read_records_nofirst_nolast = self.sheet.get_records()
        self.assertEqual(len(read_records_nofirst_nolast), 0)

        # I ask for get_records(first_index=1)
        # I want []
        read_records_first_nolast = self.sheet.get_records(first_index=2)
        self.assertEqual(len(read_records_first_nolast), 0)

        # I ask for get_records(last_index=4)
        # I want [{...}, {...}, {...}]
        read_records_nofirst_last = self.sheet.get_records(last_index=4)
        self.assertEqual(len(read_records_nofirst_last), 3)
        self.assertDictEqual(expected_values_1, read_records_nofirst_last[0])
        self.assertDictEqual(expected_values_2, read_records_nofirst_last[1])
        self.assertDictEqual(expected_values_3, read_records_nofirst_last[2])

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
    def test_get_records(self):
        self.sheet.resize(5, 3)
        rows = [
            ["A1", "B1", "C1"],
            [1, 2, 3],
            [4, 5, 6],
            [7, 8, 9],
            [10, 11, 12],
        ]
        self.sheet.update("A1:C5", rows)

        # test1 - set last_index only
        read_records = self.sheet.get_records(last_index=3)
        d0 = dict(zip(rows[0], rows[1]))
        d1 = dict(zip(rows[0], rows[2]))
        records_list = [d0, d1]
        self.assertEqual(read_records, records_list)

        # test2 - set first_index only
        read_records = self.sheet.get_records(first_index=3)
        d0 = dict(zip(rows[0], rows[2]))
        d1 = dict(zip(rows[0], rows[3]))
        d2 = dict(zip(rows[0], rows[4]))
        records_list = [d0, d1, d2]
        self.assertEqual(read_records, records_list)

        # test3 - set both last_index and first_index unequal to each other
        read_records = self.sheet.get_records(first_index=3, last_index=4)
        d0 = dict(zip(rows[0], rows[2]))
        d1 = dict(zip(rows[0], rows[3]))
        records_list = [d0, d1]
        self.assertEqual(read_records, records_list)

        # test4 - set last_index and first_index equal to each other
        read_records = self.sheet.get_records(first_index=3, last_index=3)
        d0 = dict(zip(rows[0], rows[2]))
        records_list = [d0]
        self.assertEqual(read_records, records_list)

        # test5 - set head only
        read_records = self.sheet.get_records(
            head=2, value_render_option="UNFORMATTED_VALUE"
        )
        d0 = dict(zip(rows[1], rows[2]))
        d1 = dict(zip(rows[1], rows[3]))
        d2 = dict(zip(rows[1], rows[4]))
        records_list = [d0, d1, d2]
        self.assertEqual(read_records, records_list)

    @pytest.mark.vcr()
    def test_get_records_pad_one_key(self):
        self.sheet.resize(2, 4)
        rows = [
            ["A1", "B1", "C1"],
            [1, 2, 3, 4],
        ]
        self.sheet.update("A1:D2", rows)

        read_records = self.sheet.get_records(head=1, first_index=2, last_index=2)
        rows[0].append("")
        d0 = dict(zip(rows[0], rows[1]))
        records_list = [d0]
        self.assertEqual(read_records, records_list)

    @pytest.mark.vcr()
    def test_get_records_pad_values(self):
        self.sheet.resize(2, 4)
        rows = [
            ["A1", "B1", "C1"],
            [1, 2],
        ]
        self.sheet.update("A1:C2", rows)

        read_records = self.sheet.get_records(head=1, first_index=2, last_index=2)
        rows[1].append("")
        d0 = dict(zip(rows[0], rows[1]))
        records_list = [d0]
        self.assertEqual(read_records, records_list)

    @pytest.mark.vcr()
    def test_get_records_pad_more_than_one_key(self):
        self.sheet.resize(2, 4)
        rows = [
            ["A1", "B1"],
            [1, 2, 3, 4],
        ]
        self.sheet.update("A1:D2", rows)

        with pytest.raises(GSpreadException):
            self.sheet.get_records(head=1, first_index=2, last_index=2)

    @pytest.mark.vcr()
    def test_get_records_wrong_rows_input(self):
        self.sheet.resize(5, 3)

        # set first_index to a value greater than last_index
        with pytest.raises(ValueError):
            self.sheet.get_records(head=1, first_index=4, last_index=3)

        # set first_index to a value less than head
        with pytest.raises(ValueError):
            self.sheet.get_records(head=3, first_index=2, last_index=4)

    @pytest.mark.vcr()
    def test_append_row(self):
        row_num_before = self.sheet.row_count
        sg = self._sequence_generator()
        value_list = [next(sg) for i in range(10)]

        self.sheet.append_row(value_list)
        read_values = self.sheet.row_values(1)
        row_num_after = self.sheet.row_count

        self.assertEqual(value_list, read_values)
        self.assertEqual(row_num_before + 1, row_num_after)

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
        row_count_before = self.sheet.row_count

        self.sheet.insert_row(new_row_values, 2)
        read_values = self.sheet.row_values(2)
        row_count_after = self.sheet.row_count

        self.assertEqual(new_row_values, read_values)
        self.assertEqual(row_count_before + 1, row_count_after)

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
    def test_insert_cols(self):
        sequence_generator = self._sequence_generator()
        num_rows = 6
        num_cols = 4
        rows = [
            [next(sequence_generator) for j in range(num_cols)] for i in range(num_rows)
        ]
        cell_list = self.sheet.range("A1:D6")
        for cell, value in zip(cell_list, itertools.chain(*rows)):
            cell.value = value
        self.sheet.update_cells(cell_list)

        new_col_values = [
            [next(sequence_generator) for i in range(num_cols)] for i in range(2)
        ]
        col_count_before = self.sheet.col_count

        self.sheet.insert_cols(new_col_values, 2)

        read_values_1 = self.sheet.col_values(2)
        read_values_2 = self.sheet.col_values(3)
        read_values = [read_values_1, read_values_2]
        col_count_after = self.sheet.col_count

        self.assertEqual(col_count_before + 2, col_count_after)
        self.assertEqual(new_col_values, read_values)

    @pytest.mark.vcr()
    def test_delete_row(self):
        sequence_generator = self._sequence_generator()

        for i in range(5):
            value_list = [next(sequence_generator) for i in range(10)]
            self.sheet.append_row(value_list)

        prev_row = self.sheet.row_values(1)
        next_row = self.sheet.row_values(3)
        row_count_before = self.sheet.row_count

        self.sheet.delete_rows(2)

        row_count_after = self.sheet.row_count
        self.assertEqual(row_count_before - 1, row_count_after)
        self.assertEqual(self.sheet.row_values(1), prev_row)
        self.assertEqual(self.sheet.row_values(2), next_row)

    @pytest.mark.vcr()
    def test_delete_cols(self):
        sequence_generator = self._sequence_generator()
        num_rows = 6
        num_cols = 4
        rows = [
            [next(sequence_generator) for j in range(num_cols)] for i in range(num_rows)
        ]
        cell_list = self.sheet.range("A1:D6")
        for cell, value in zip(cell_list, itertools.chain(*rows)):
            cell.value = value
        self.sheet.update_cells(cell_list)

        col_count_before = self.sheet.col_count
        first_col_before = self.sheet.col_values(1)
        fourth_col_before = self.sheet.col_values(4)

        self.sheet.delete_columns(2, 3)

        col_count_after = self.sheet.col_count
        first_col_after = self.sheet.col_values(1)
        second_col_after = self.sheet.col_values(2)

        self.assertEqual(col_count_before - 2, col_count_after)
        self.assertEqual(first_col_before, first_col_after)
        self.assertEqual(fourth_col_before, second_col_after)

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
        # need to have multiple worksheets to reorder them
        self.spreadsheet.add_worksheet("test_sheet", 100, 100)
        self.spreadsheet.add_worksheet("test_sheet 2", 100, 100)

        worksheets = self.spreadsheet.worksheets()
        last_sheet = worksheets[-1]
        self.assertEqual(last_sheet.index, len(worksheets) - 1)

        last_sheet.update_index(0)

        worksheets = self.spreadsheet.worksheets()
        self.assertEqual(worksheets[0].id, last_sheet.id)
        self.assertEqual(last_sheet.index, 0)

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
        hidden_before = res["sheets"][1]["properties"].get("hidden", False)
        hidden_before_prop = new_sheet.isSheetHidden

        self.assertFalse(hidden_before)
        self.assertFalse(hidden_before_prop)

        new_sheet.hide()

        res = self.spreadsheet.fetch_sheet_metadata()
        hidden_after = res["sheets"][1]["properties"].get("hidden", False)
        hidden_after_prop = new_sheet.isSheetHidden
        self.assertTrue(hidden_after)
        self.assertTrue(hidden_after_prop)

        new_sheet.show()

        res = self.spreadsheet.fetch_sheet_metadata()
        hidden_before = res["sheets"][1]["properties"].get("hidden", False)
        hidden_before_prop = new_sheet.isSheetHidden
        self.assertFalse(hidden_before)
        self.assertFalse(hidden_before_prop)

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
