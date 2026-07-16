import datetime
import json
from unittest import TestCase
from unittest.mock import Mock, patch

from gspread.exceptions import APIError
from gspread.http_client import BackOffHTTPClient, HTTPClient
from gspread.worksheet import Worksheet


class HTTPClientSerializerTest(TestCase):
    def _make_client(self):
        session = Mock()
        session.request.return_value.ok = True  # so request() returns, doesn't raise
        return HTTPClient(auth=None, session=session), session

    def test_default_uses_json_kwarg(self):
        """Without default_serializer, the body goes out via json= (unchanged behavior)."""
        client, session = self._make_client()
        body = {"values": [[1, 2, 3]]}

        client.request("post", "http://example.com", json=body)

        _, kwargs = session.request.call_args
        self.assertEqual(kwargs["json"], body)
        self.assertIsNone(kwargs["data"])

    def test_default_serializer_uses_data_and_header(self):
        """With default_serializer, the body is encoded into data= with a JSON header."""
        client, session = self._make_client()
        body = {"values": [[1, 2, 3]]}

        client.request("post", "http://example.com", json=body, default_serializer=str)

        _, kwargs = session.request.call_args
        self.assertIsNone(kwargs["json"])
        self.assertEqual(kwargs["data"], json.dumps(body, default=str))
        self.assertEqual(kwargs["headers"]["Content-Type"], "application/json")

    def test_default_serializer_handles_non_native_types(self):
        """The actual use case from the issue: encode a date the stdlib can't."""
        client, session = self._make_client()
        body = {"values": [[datetime.date(2026, 6, 19)]]}

        client.request(
            "post",
            "http://example.com",
            json=body,
            default_serializer=lambda o: o.isoformat(),
        )

        _, kwargs = session.request.call_args
        self.assertIn("2026-06-19", kwargs["data"])


class WorksheetForwardsSerializerTest(TestCase):
    """default_serializer must reach the client from each write method."""

    MARKER = staticmethod(lambda o: str(o))

    def _make_worksheet(self):
        client = HTTPClient(auth=None, session=Mock())
        client.values_update = Mock()
        client.values_append = Mock()
        client.values_batch_update = Mock()
        properties = {
            "title": "Sheet1",
            "gridProperties": {"rowCount": 5, "columnCount": 5},
        }
        worksheet = Worksheet(
            spreadsheet=None,
            properties=properties,
            spreadsheet_id="abc123",
            client=client,
        )
        return worksheet, client

    def test_update_forwards_serializer(self):
        worksheet, client = self._make_worksheet()
        worksheet.update([[1, 2, 3]], "A1", default_serializer=self.MARKER)
        self.assertIs(
            client.values_update.call_args.kwargs["default_serializer"], self.MARKER
        )

    def test_batch_update_forwards_serializer(self):
        worksheet, client = self._make_worksheet()
        worksheet.batch_update(
            [{"range": "A1", "values": [[1]]}], default_serializer=self.MARKER
        )
        self.assertIs(
            client.values_batch_update.call_args.kwargs["default_serializer"],
            self.MARKER,
        )

    def test_append_rows_forwards_serializer(self):
        worksheet, client = self._make_worksheet()
        worksheet.append_rows([[1, 2, 3]], default_serializer=self.MARKER)
        # values_append receives default_serializer as the last positional arg
        self.assertIs(client.values_append.call_args.args[4], self.MARKER)

    def test_append_row_forwards_serializer(self):
        worksheet, client = self._make_worksheet()
        worksheet.append_row([1, 2, 3], default_serializer=self.MARKER)
        self.assertIs(client.values_append.call_args.args[4], self.MARKER)


class BackOffHTTPClientTest(TestCase):
    @staticmethod
    def _error_response(code, domain="global"):
        response = Mock()
        response.ok = False
        response.text = "request failed"
        response.json.return_value = {
            "error": {
                "code": code,
                "message": "request failed",
                "errors": [{"domain": domain}],
            }
        }
        return response

    def test_terminal_error_does_not_increase_next_retry_delay(self):
        session = Mock()
        success = Mock(ok=True)
        session.request.side_effect = [
            self._error_response(403),
            self._error_response(500),
            success,
        ]
        client = BackOffHTTPClient(auth=None, session=session)

        with self.assertRaises(APIError):
            client.request("get", "http://example.com/forbidden")

        with patch("gspread.http_client.time.sleep") as sleep:
            self.assertIs(
                client.request("get", "http://example.com/retryable"), success
            )

        sleep.assert_called_once_with(2)
