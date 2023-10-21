import pytest

import gspread

from .conftest import GspreadTest


class ClientTest(GspreadTest):

    """Test for gspread.client."""

    @pytest.fixture(scope="function", autouse=True)
    def init(self, client, request):
        ClientTest.gc = client
        name = self.get_temporary_spreadsheet_title(request.node.name)
        ClientTest.spreadsheet = client.create(name)

        yield

        client.del_spreadsheet(ClientTest.spreadsheet.id)

    @pytest.mark.vcr()
    def test_no_found_exeption(self):
        noexistent_title = "Please don't use this phrase as a name of a sheet."
        self.assertRaises(gspread.SpreadsheetNotFound, self.gc.open, noexistent_title)

    @pytest.mark.vcr()
    def test_list_spreadsheet_files(self):
        res = self.gc.list_spreadsheet_files()
        self.assertIsInstance(res, list)
        for f in res:
            self.assertIsInstance(f, dict)
            self.assertIn("id", f)
            self.assertIn("name", f)
            self.assertIn("createdTime", f)
            self.assertIn("modifiedTime", f)

    @pytest.mark.vcr()
    def test_openall(self):
        spreadsheet_list = self.gc.openall()
        spreadsheet_list2 = self.gc.openall(spreadsheet_list[0].title)

        self.assertTrue(len(spreadsheet_list2) < len(spreadsheet_list))
        for s in spreadsheet_list:
            self.assertIsInstance(s, gspread.Spreadsheet)
        for s in spreadsheet_list2:
            self.assertIsInstance(s, gspread.Spreadsheet)

    @pytest.mark.vcr()
    def test_create(self):
        title = "Test Spreadsheet"
        new_spreadsheet = self.gc.create(title)
        self.assertIsInstance(new_spreadsheet, gspread.Spreadsheet)

    @pytest.mark.vcr()
    def test_copy(self):
        original_spreadsheet = self.spreadsheet
        spreadsheet_copy = self.gc.copy(original_spreadsheet.id)
        self.assertIsInstance(spreadsheet_copy, gspread.Spreadsheet)

        original_metadata = original_spreadsheet.fetch_sheet_metadata()
        copy_metadata = spreadsheet_copy.fetch_sheet_metadata()
        self.assertEqual(original_metadata["sheets"], copy_metadata["sheets"])

    @pytest.mark.vcr()
    def test_import_csv(self):
        spreadsheet = self.spreadsheet

        sg = self._sequence_generator()

        csv_rows = 4
        csv_cols = 4

        rows = [[next(sg) for j in range(csv_cols)] for i in range(csv_rows)]

        simple_csv_data = "\n".join([",".join(row) for row in rows])

        self.gc.import_csv(spreadsheet.id, simple_csv_data)

        sh = self.gc.open_by_key(spreadsheet.id)
        self.assertEqual(sh.sheet1.get_all_values(), rows)

    @pytest.mark.vcr()
    def test_access_non_existing_spreadsheet(self):
        with self.assertRaises(gspread.exceptions.SpreadsheetNotFound):
            self.gc.open_by_key("test")
        with self.assertRaises(gspread.exceptions.SpreadsheetNotFound):
            self.gc.open_by_url("https://docs.google.com/spreadsheets/d/test")

    @pytest.mark.vcr()
    def test_open_all_has_metadata(self):
        """tests all spreadsheets are opened
        and that they all have metadata"""
        spreadsheets = self.gc.openall()
        for spreadsheet in spreadsheets:
            self.assertIsInstance(spreadsheet, gspread.Spreadsheet)
            # has properties that are not from Drive API (i.e., not title, id, creationTime)
            self.assertTrue(spreadsheet.locale)
            self.assertTrue(spreadsheet.timezone)

    @pytest.mark.vcr()
    def test_open_by_key_has_metadata(self):
        """tests open_by_key has metadata"""
        spreadsheet = self.gc.open_by_key(self.spreadsheet.id)
        self.assertIsInstance(spreadsheet, gspread.Spreadsheet)
        # has properties that are not from Drive API (i.e., not title, id, creationTime)
        self.assertTrue(spreadsheet.locale)
        self.assertTrue(spreadsheet.timezone)

    @pytest.mark.vcr()
    def test_open_by_name_has_metadata(self):
        """tests open has metadata"""
        spreadsheet = self.gc.open(self.spreadsheet.title)
        self.assertIsInstance(spreadsheet, gspread.Spreadsheet)
        # has properties that are not from Drive API (i.e., not title, id, creationTime)
        self.assertTrue(spreadsheet.locale)
        self.assertTrue(spreadsheet.timezone)

    @pytest.mark.vcr()
    def test_access_private_spreadsheet(self):
        """tests that opening private spreadsheet returns SpreadsheetPermissionDenied"""
        self.skipTest(
            """
            APIs run up to timeout value.
            With credentials, test passes, but takes ~260 seconds.
            This is an issue with the back-off client.
            See BackOffHTTPClient docstring in
                `gspread/http_client.py`
            > "will retry exponentially even when the error should
            > raise instantly. Due to the Drive API that raises
            > 403 (Forbidden) errors for forbidden access and
            > for api rate limit exceeded."
            """
        )
        private_id = "1jIKzPs8LsiZZdLdeMEP-5ZIHw6RkjiOmj1LrJN706Yc"
        with self.assertRaises(PermissionError):
            self.gc.open_by_key(private_id)
