from typing import Generator

import pytest
from pytest import FixtureRequest

import gspread
from gspread.client import Client
from gspread.spreadsheet import Spreadsheet
from gspread.worksheet import Worksheet

from .conftest import GspreadTest


class CellTest(GspreadTest):
    """Test for gspread.Cell."""

    spreadsheet: Spreadsheet
    sheet: Worksheet

    @pytest.fixture(scope="function", autouse=True)
    def init(
        self: "CellTest", client: Client, request: FixtureRequest
    ) -> Generator[None, None, None]:
        # User current test name in spreadsheet name
        name = self.get_temporary_spreadsheet_title(request.node.name)
        CellTest.spreadsheet = client.create(name)
        CellTest.sheet = CellTest.spreadsheet.sheet1

        yield

        client.del_spreadsheet(CellTest.spreadsheet.id)

    @pytest.mark.vcr()
    def test_properties(self):
        sg = self._sequence_generator()
        update_value = next(sg)
        self.sheet.update_acell("A1", update_value)
        cell = self.sheet.acell("A1")
        self.assertEqual(cell.value, update_value)
        self.assertEqual(cell.row, 1)
        self.assertEqual(cell.col, 1)

    @pytest.mark.vcr()
    def test_equality(self):
        sg = self._sequence_generator()
        update_value = next(sg)
        self.sheet.update_acell("A1", update_value)
        cell = self.sheet.acell("A1")
        same_cell = self.sheet.cell(1, 1)
        self.assertEqual(cell, same_cell)
        self.sheet.update_acell("A2", update_value)
        another_cell = self.sheet.acell("A2")
        self.assertNotEqual(cell, another_cell)
        self.sheet.update_acell("B1", update_value)
        another_cell = self.sheet.acell("B1")
        self.assertNotEqual(cell, another_cell)

    @pytest.mark.vcr()
    def test_numeric_value(self):
        numeric_value = 1.0 / 1024
        # Use a formula here to avoid issues with differing decimal marks:
        self.sheet.update_acell("A1", "= 1 / 1024")
        cell = self.sheet.acell("A1")
        self.assertEqual(cell.numeric_value, numeric_value)
        self.assertIsInstance(cell.numeric_value, float)

        # test value for popular format with long numbers
        numeric_value = 2000000.01
        self.sheet.update_acell("A1", "2,000,000.01")
        cell = self.sheet.acell("A1")
        self.assertEqual(cell.numeric_value, numeric_value)
        self.assertIsInstance(cell.numeric_value, float)

        # test non numeric value
        self.sheet.update_acell("A1", "Non-numeric value")
        cell = self.sheet.acell("A1")
        self.assertEqual(cell.numeric_value, None)

    @pytest.mark.vcr()
    def test_a1_value(self):
        cell = self.sheet.cell(4, 4)
        self.assertEqual(cell.address, "D4")
        self.sheet.update_acell("B1", "Dummy")
        result = self.sheet.find("Dummy")
        if result is None:
            self.fail("did not find cell with matching text 'Dummy'")
        else:
            cell = result

        self.assertEqual(cell.address, "B1")
        self.assertEqual(cell.value, "Dummy")
        cell = gspread.cell.Cell(1, 2, "Foo Bar")
        self.assertEqual(cell.address, "B1")
        cell = gspread.cell.Cell.from_address("A1", "Foo Bar")
        self.assertEqual(cell.address, "A1")
        self.assertEqual(cell.value, "Foo Bar")
        self.assertEqual((cell.row, cell.col), (1, 1))

    @pytest.mark.vcr()
    def test_merge_cells(self):
        self.sheet.update([[42, 43], [43, 44]], "A1:B2")

        # test merge rows
        self.sheet.merge_cells(1, 1, 2, 2, merge_type="MERGE_ROWS")
        merges = self.sheet._get_sheet_property("merges", [])
        self.assertEqual(len(merges), 2)

        # test merge all
        self.sheet.merge_cells(1, 1, 2, 2)

        merges = self.sheet._get_sheet_property("merges", [])
        self.assertEqual(len(merges), 1)

        self.sheet.unmerge_cells(1, 1, 2, 2)
        merges = self.sheet._get_sheet_property("merges", [])
        self.assertEqual(len(merges), 0)

    @pytest.mark.vcr()
    def test_define_named_range(self):
        # define the named range
        range_name = "TestDefineNamedRange"
        self.sheet.define_named_range("A1:B2", range_name)

        # get the ranges from the metadata
        named_range_dict = self.spreadsheet.fetch_sheet_metadata(
            params={"fields": "namedRanges"}
        )

        # make sure that a range was returned and it has the namedRanges key,
        #  also that the dict contains a single range
        self.assertNotEqual(named_range_dict, {})
        self.assertIn("namedRanges", named_range_dict)
        self.assertTrue(len(named_range_dict["namedRanges"]) == 1)

        named_range = named_range_dict["namedRanges"][0]

        # ensure all of the properties of the named range match what we expect
        self.assertEqual(named_range["name"], range_name)
        self.assertEqual(named_range["range"]["startRowIndex"], 0)
        self.assertEqual(named_range["range"]["endRowIndex"], 2)
        self.assertEqual(named_range["range"]["startColumnIndex"], 0)
        self.assertEqual(named_range["range"]["endColumnIndex"], 2)

        # clean up the named range
        self.sheet.delete_named_range(named_range["namedRangeId"])

        # ensure the range has been deleted
        named_range_dict = self.spreadsheet.fetch_sheet_metadata(
            params={"fields": "namedRanges"}
        )

        self.assertEqual(named_range_dict, {})

        # Add the same range but with index based coordinates
        self.sheet.define_named_range(1, 1, 2, 2, range_name)

        # Check the created named range
        named_range_dict = self.spreadsheet.fetch_sheet_metadata(
            params={"fields": "namedRanges"}
        )

        # make sure that a range was returned and it has the namedRanges key,
        #  also that the dict contains a single range
        self.assertNotEqual(named_range_dict, {})
        self.assertIn("namedRanges", named_range_dict)
        self.assertTrue(len(named_range_dict["namedRanges"]) == 1)

        named_range = named_range_dict["namedRanges"][0]

        # ensure all of the properties of the named range match what we expect
        self.assertEqual(named_range["name"], range_name)
        self.assertEqual(named_range["range"]["startRowIndex"], 0)
        self.assertEqual(named_range["range"]["endRowIndex"], 2)
        self.assertEqual(named_range["range"]["startColumnIndex"], 0)
        self.assertEqual(named_range["range"]["endColumnIndex"], 2)

    @pytest.mark.vcr()
    def test_delete_named_range(self):
        # define a named range
        result = self.sheet.define_named_range("A1:B2", "TestDeleteNamedRange")

        # from the result, get the named range we just created
        named_range_id = result["replies"][0]["addNamedRange"]["namedRange"][
            "namedRangeId"
        ]

        self.sheet.delete_named_range(named_range_id)

        # get the ranges from the metadata
        named_range_dict = self.spreadsheet.fetch_sheet_metadata(
            params={"fields": "namedRanges"}
        )

        # make sure that no ranges were returned
        self.assertEqual(named_range_dict, {})
