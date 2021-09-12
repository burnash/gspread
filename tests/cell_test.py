import pytest

import gspread
import gspread.utils as utils

from .conftest import GspreadTest


class CellTest(GspreadTest):
    """Test for gspread.Cell."""

    @pytest.fixture(scope="class", autouse=True)
    def init(self, client, vcr):
        # fixtures are not recorded by default, must do manually
        with vcr.use_cassette(self.get_temporary_spreadsheet_title()):
            # must use class attributes, each test function runs in a different instance
            CellTest.spreadsheet = client.create(self.get_temporary_spreadsheet_title())
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
    def test_numeric_value(self):
        numeric_value = 1.0 / 1024
        # Use a formula here to avoid issues with differing decimal marks:
        self.sheet.update_acell("A1", "= 1 / 1024")
        cell = self.sheet.acell("A1")
        self.assertEqual(cell.numeric_value, numeric_value)
        self.assertTrue(isinstance(cell.numeric_value, float))

        # test value for popular format with long numbers
        numeric_value = 2000000.01
        self.sheet.update_acell("A1", "2,000,000.01")
        cell = self.sheet.acell("A1")
        self.assertEqual(cell.numeric_value, numeric_value)
        self.assertTrue(isinstance(cell.numeric_value, float))

        # test non numeric value
        self.sheet.update_acell("A1", "Non-numeric value")
        cell = self.sheet.acell("A1")
        self.assertEqual(cell.numeric_value, None)

    @pytest.mark.vcr()
    def test_a1_value(self):
        cell = self.sheet.cell(4, 4)
        self.assertEqual(cell.address, "D4")
        self.sheet.update_acell("B1", "Dummy")
        cell = self.sheet.find("Dummy")
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
        self.sheet.update("A1:B2", [[42, 43], [43, 44]])

        # test merge rows
        self.sheet.merge_cells(1, 1, 2, 2, merge_type="MERGE_ROWS")
        meta = self.sheet.spreadsheet.fetch_sheet_metadata()
        merges = utils.finditem(
            lambda x: x["properties"]["sheetId"] == self.sheet.id, meta["sheets"]
        )["merges"]
        self.assertEqual(len(merges), 2)

        # test merge all
        self.sheet.merge_cells(1, 1, 2, 2)

        meta = self.sheet.spreadsheet.fetch_sheet_metadata()
        merges = utils.finditem(
            lambda x: x["properties"]["sheetId"] == self.sheet.id, meta["sheets"]
        )["merges"]

        self.assertEqual(len(merges), 1)
