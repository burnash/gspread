import re

import pytest

import gspread

from .conftest import GspreadTest


class SpreadsheetTest(GspreadTest):

    """Test for gspread.Spreadsheet."""

    @pytest.fixture(scope="function", autouse=True)
    def init(self, client, request):
        name = self.get_temporary_spreadsheet_title(request.node.name)
        SpreadsheetTest.spreadsheet = client.create(name)

        yield

        client.del_spreadsheet(SpreadsheetTest.spreadsheet.id)

    @pytest.mark.vcr()
    def test_properties(self):
        self.assertTrue(re.match(r"^[a-zA-Z0-9-_]+$", self.spreadsheet.id))
        self.assertTrue(len(self.spreadsheet.title) > 0)

    @pytest.mark.vcr()
    def test_sheet1(self):
        sheet1 = self.spreadsheet.sheet1
        self.assertTrue(isinstance(sheet1, gspread.Worksheet))

    @pytest.mark.vcr()
    def test_get_worksheet(self):
        sheet1 = self.spreadsheet.get_worksheet(0)
        self.assertTrue(isinstance(sheet1, gspread.Worksheet))

    @pytest.mark.vcr()
    def test_get_worksheet_by_id(self):
        sheet1 = self.spreadsheet.get_worksheet_by_id(0)
        self.assertTrue(isinstance(sheet1, gspread.Worksheet))

    @pytest.mark.vcr()
    def test_worksheet(self):
        sheet_title = "Sheet1"
        sheet = self.spreadsheet.worksheet(sheet_title)
        self.assertTrue(isinstance(sheet, gspread.Worksheet))

    @pytest.mark.vcr()
    def test_worksheet_iteration(self):
        self.assertEqual(
            [x.id for x in self.spreadsheet.worksheets()],
            [sheet.id for sheet in self.spreadsheet],
        )

    @pytest.mark.vcr()
    def test_values_get(self):
        sg = self._sequence_generator()

        worksheet1_name = "{} {}".format("🌵", next(sg))

        worksheet = self.spreadsheet.add_worksheet(worksheet1_name, 10, 10)

        range_label = "{}!{}".format(worksheet1_name, "A1")

        values = [["🍇", "🍉", "🍋"], ["🍐", "🍎", "🍓"]]

        self.spreadsheet.values_update(
            range_label, params={"valueInputOption": "RAW"}, body={"values": values}
        )

        read_data = self.spreadsheet.values_get(worksheet1_name)

        self.assertEqual(values, read_data["values"])
        self.spreadsheet.del_worksheet(worksheet)

    @pytest.mark.vcr()
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

    @pytest.mark.vcr()
    def test_values_batch_get(self):
        sg = self._sequence_generator()

        worksheet1_name = "{} {}".format("🌵", next(sg))

        worksheet = self.spreadsheet.add_worksheet(worksheet1_name, 10, 10)

        range_label = "{}!{}".format(worksheet1_name, "A1")

        values = [["🍇", "🍉", "🍋"], ["🍐", "🍎", "🍓"]]

        self.spreadsheet.values_update(
            range_label, params={"valueInputOption": "RAW"}, body={"values": values}
        )
        ranges = [
            "{}!{}:{}".format(worksheet1_name, col, col) for col in ["A", "B", "C"]
        ]

        read_data = self.spreadsheet.values_batch_get(ranges)

        for colix, rng in enumerate(read_data["valueRanges"]):
            for rowix, ele in enumerate(rng["values"]):
                self.assertEqual(values[rowix][colix], ele[0])
        self.spreadsheet.del_worksheet(worksheet)

    @pytest.mark.vcr()
    def test_timezone_and_locale(self):
        prev_timezone = self.spreadsheet.timezone
        prev_locale = self.spreadsheet.locale
        new_timezone = "Europe/Paris"
        new_locale = "fr_FR"

        self.spreadsheet.update_timezone(new_timezone)
        self.spreadsheet.update_locale(new_locale)

        # must fect metadata
        properties = self.spreadsheet.fetch_sheet_metadata()["properties"]

        self.assertNotEqual(prev_timezone, properties["timeZone"])
        self.assertNotEqual(prev_locale, properties["locale"])

        self.assertEqual(new_timezone, properties["timeZone"])
        self.assertEqual(new_locale, properties["locale"])

    @pytest.mark.vcr()
    def test_update_title(self):
        prev_title = self.spreadsheet.title
        new_title = "🎊 Updated Title #123 🎉"

        self.spreadsheet.update_title(new_title)

        # Check whether title is updated immediately
        self.assertNotEqual(prev_title, self.spreadsheet.title)
        self.assertEqual(new_title, self.spreadsheet.title)

        # Check whether changes persist upon re-fetching
        properties = self.spreadsheet.fetch_sheet_metadata()["properties"]

        self.assertNotEqual(prev_title, properties["title"])
        self.assertEqual(new_title, properties["title"])

    @pytest.mark.vcr()
    def test_get_updated_time(self):
        current_metadata = self.spreadsheet._properties
        self.assertNotIn("modifiedTime", self.spreadsheet._properties)

        res = self.spreadsheet.lastUpdateTime

        self.assertIsNotNone(res)

        new_metadata = self.spreadsheet._properties
        self.assertIn("modifiedTime", self.spreadsheet._properties)

        self.assertDictContainsSubset(current_metadata, new_metadata)
