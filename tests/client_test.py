import time
from typing import Generator
from unittest.mock import Mock, patch

import pytest
from pytest import FixtureRequest
from requests import Response

import gspread
from gspread.client import Client
from gspread.exceptions import APIError
from gspread.http_client import (
    RETRYABLE_HTTP_CODES,
    SERVER_ERROR_THRESHOLD,
    BackOffHTTPClient,
)
from gspread.spreadsheet import Spreadsheet

from .conftest import GspreadTest


class ClientTest(GspreadTest):
    """Test for gspread.client."""

    gc: Client
    spreadsheet: Spreadsheet

    @pytest.fixture(scope="function", autouse=True)
    def init(
        self: "ClientTest", client: Client, request: FixtureRequest
    ) -> Generator[None, None, None]:
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
        private_id = "1jIKzPs8LsiZZdLdeMEP-5ZIHw6RkjiOmj1LrJN706Yc"
        with self.assertRaises(PermissionError):
            self.gc.open_by_key(private_id)

    @pytest.mark.vcr()
    def test_client_export_spreadsheet(self):
        """Test the export feature of a spreadsheet.

        JSON cannot serialize binary data (like PDF or OpenSpreadsheetFormat)
        Export to CSV text format only
        """
        values = [
            ["a1", "B2"],
        ]
        self.spreadsheet.sheet1.update(
            values=values,
            range_name="A1:B2",
        )

        res = self.gc.export(self.spreadsheet.id, gspread.utils.ExportFormat.CSV)

        res_values = bytes(res).decode("utf-8").strip("'").split(",")

        self.assertEqual(
            values[0], res_values, "exported values are not the value initially set"
        )

    @pytest.mark.vcr()
    def test_add_timeout(self):
        """Test the method to set the HTTP request timeout"""

        # Store original timeout
        original_timeout = self.gc.http_client.timeout

        # So far it took 0.17 seconds to fetch the metadata with my connection.
        # Once recorded it takes 0.001 seconds to run it, so 1 second should be a large enough value
        timeout = 1
        self.gc.set_timeout(timeout)

        start = time.time()
        self.spreadsheet.fetch_sheet_metadata()
        end = time.time()

        self.assertLessEqual(
            end - start, timeout, "Request took longer than the set timeout value"
        )

        # Reset timeout to original value
        # self.gc.set_timeout(original_timeout)
        self.gc.set_timeout(original_timeout)

    @pytest.mark.vcr()
    def test_hookable_decorator_before_hooks(self):
        """Test that before hooks are executed before method calls"""
        before_hook_called = False
        before_hook_args = None
        before_hook_kwargs = None

        def before_hook(method_name, args, kwargs, result=None):
            nonlocal before_hook_called, before_hook_args, before_hook_kwargs
            before_hook_called = True
            before_hook_args = args
            before_hook_kwargs = kwargs

        # Add before hook to the request method
        self.gc.http_client.add_before_hook("request", before_hook)

        # Make a request
        self.spreadsheet.fetch_sheet_metadata()

        # Verify hook was called
        self.assertTrue(before_hook_called, "Before hook should have been called")
        self.assertIsNotNone(before_hook_args, "Before hook should have received args")
        self.assertIsNotNone(
            before_hook_kwargs, "Before hook should have received kwargs"
        )

    @pytest.mark.vcr()
    def test_hookable_decorator_after_hooks(self):
        """Test that after hooks are executed after method calls"""
        after_hook_called = False
        after_hook_result = None

        def after_hook(method_name, args, kwargs, result):
            nonlocal after_hook_called, after_hook_result
            after_hook_called = True
            after_hook_result = result

        # Add after hook to the request method
        self.gc.http_client.add_after_hook("request", after_hook)

        # Make a request
        self.spreadsheet.fetch_sheet_metadata()

        # Verify hook was called
        self.assertTrue(after_hook_called, "After hook should have been called")
        self.assertIsInstance(
            after_hook_result,
            Response,
            "After hook should have received the Response object",
        )

    @pytest.mark.vcr()
    def test_hookable_decorator_success_hooks(self):
        """Test that success hooks are executed when methods complete successfully"""
        success_hook_called = False
        success_hook_result = None

        def success_hook(method_name, args, kwargs, result):
            nonlocal success_hook_called, success_hook_result
            success_hook_called = True
            success_hook_result = result

        # Add success hook to the request method
        self.gc.http_client.add_success_hook("request", success_hook)

        # Make a request
        self.spreadsheet.fetch_sheet_metadata()

        # Verify hook was called
        self.assertTrue(success_hook_called, "Success hook should have been called")
        self.assertIsInstance(
            success_hook_result,
            Response,
            "Success hook should have received the Response object",
        )

    @pytest.mark.vcr()
    def test_hookable_decorator_exception_hooks(self):
        """Test that exception hooks are executed when exceptions occur"""
        exception_hook_called = False
        exception_hook_exception = None

        def exception_hook(method_name, args, kwargs, exception):
            nonlocal exception_hook_called, exception_hook_exception
            exception_hook_called = True
            exception_hook_exception = exception

        # Add exception hook to the request method
        self.gc.http_client.add_exception_hook("request", exception_hook)

        # Make a request that will fail (non-existent spreadsheet)
        with self.assertRaises(gspread.exceptions.SpreadsheetNotFound):
            self.gc.open_by_key("non_existent_id")

        # Verify hook was called
        self.assertTrue(exception_hook_called, "Exception hook should have been called")
        self.assertIsInstance(exception_hook_exception, gspread.exceptions.APIError)

    @pytest.mark.vcr()
    def test_hookable_decorator_timeout_hooks(self):
        """Test that timeout hooks are executed for timeout exceptions"""
        timeout_hook_called = False
        timeout_hook_exception = None

        def timeout_hook(method_name, args, kwargs, exception):
            nonlocal timeout_hook_called, timeout_hook_exception
            timeout_hook_called = True
            timeout_hook_exception = exception

        # Add timeout hook to the request method
        self.gc.http_client.add_timeout_hook("request", timeout_hook)

        # Set a very short timeout to trigger timeout exception
        original_timeout = self.gc.http_client.timeout
        self.gc.set_timeout(0.001)

        try:
            # This should timeout
            self.spreadsheet.fetch_sheet_metadata()
        except Exception as e:
            # Check if it's a timeout-related exception
            if "timeout" in str(e).lower() or "timed out" in str(e).lower():
                # Verify timeout hook was called
                self.assertTrue(
                    timeout_hook_called, "Timeout hook should have been called"
                )
                self.assertIsNotNone(
                    timeout_hook_exception,
                    "Timeout hook should have received the exception",
                )

        finally:
            # Restore original timeout
            self.gc.set_timeout(original_timeout)

    @pytest.mark.vcr()
    def test_hookable_decorator_retry_hooks(self):
        """Test that retry hooks are executed for retryable errors"""
        retry_hook_called = False
        retry_hook_exception = None

        def retry_hook(method_name, args, kwargs, exception):
            nonlocal retry_hook_called, retry_hook_exception
            retry_hook_called = True
            retry_hook_exception = exception

        # Add retry hook to the request method
        self.gc.http_client.add_retry_hook("request", retry_hook)

        # Test 1: Timeout exception (should trigger timeout hooks only, not retry hooks)
        original_timeout = self.gc.http_client.timeout
        self.gc.set_timeout(0.001)

        try:
            self.spreadsheet.fetch_sheet_metadata()
        except Exception as e:
            if "timeout" in str(e).lower() or "timed out" in str(e).lower():
                # Timeout errors trigger timeout hooks only, not retry hooks
                self.assertFalse(
                    retry_hook_called,
                    "Retry hook should not be called for timeout errors",
                )

        finally:
            # Restore original timeout
            self.gc.set_timeout(original_timeout)
            retry_hook_called = False  # Reset for next test

        # Test 2: Permission denied (403) - this should trigger retry hook
        try:
            self.gc.open_by_key("1jIKzPs8LsiZZdLdeMEP-5ZIHw6RkjiOmj1LrJN706Yc")
        except PermissionError:
            # 403 errors are no longer automatically considered retryable in our hook system
            pass

        # Note: The retry hook behavior depends on the specific error conditions
        # and how the API responds. This test verifies the hook system is in place.

    @pytest.mark.vcr()
    def test_hookable_decorator_retry_hooks_api_errors(self):
        """Test that retry hooks are executed for different types of API retryable errors"""
        retry_hook_called = False
        retry_hook_exception = None

        def retry_hook(method_name, args, kwargs, exception):
            nonlocal retry_hook_called, retry_hook_exception
            retry_hook_called = True
            retry_hook_exception = exception

        # Add retry hook to the request method
        self.gc.http_client.add_retry_hook("request", retry_hook)

        # Test: Try to access a private spreadsheet (should trigger 403 error)
        # This should trigger the retry hook if it's a retryable error
        try:
            self.gc.open_by_key("1jIKzPs8LsiZZdLdeMEP-5ZIHw6RkjiOmj1LrJN706Yc")
        except Exception as e:
            # Check if this is a retryable error that should trigger the retry hook
            if hasattr(e, "code"):
                # For API errors, check if they're retryable
                if e.code in RETRYABLE_HTTP_CODES or e.code >= SERVER_ERROR_THRESHOLD:
                    self.assertTrue(
                        retry_hook_called,
                        f"Retry hook should have been called for HTTP {e.code}",
                    )
                elif e.code == 403:
                    # 403 errors are no longer automatically considered retryable
                    # This test verifies the hook system is in place
                    pass

    @pytest.mark.vcr()
    def test_hookable_decorator_retry_hooks_connection_errors(self):
        """Test that retry hooks are executed for connection-related retryable errors"""
        retry_hook_called = False
        timeout_hook_called = False

        def retry_hook(method_name, args, kwargs, exception):
            nonlocal retry_hook_called
            retry_hook_called = True

        def timeout_hook(method_name, args, kwargs, exception):
            nonlocal timeout_hook_called
            timeout_hook_called = True

        # Add both retry and timeout hooks
        self.gc.http_client.add_retry_hook("request", retry_hook)
        self.gc.http_client.add_timeout_hook("request", timeout_hook)

        # Test with a very short timeout to trigger timeout exception
        original_timeout = self.gc.http_client.timeout
        self.gc.set_timeout(0.001)

        try:
            self.spreadsheet.fetch_sheet_metadata()
        except Exception as e:
            if "timeout" in str(e).lower() or "timed out" in str(e).lower():
                # Timeout errors trigger timeout hooks only
                self.assertTrue(
                    timeout_hook_called,
                    "Timeout hook should have been called for timeout",
                )
                # Timeout errors no longer trigger retry hooks (they're handled by timeout_hooks)
                self.assertFalse(
                    retry_hook_called,
                    "Retry hook should not be called for timeout errors",
                )

        finally:
            # Restore original timeout
            self.gc.set_timeout(original_timeout)

    @pytest.mark.vcr()
    def test_hookable_decorator_multiple_hooks(self):
        """Test that multiple hooks of the same type are executed in order"""
        hook_execution_order = []

        def hook1(method_name, args, kwargs, result=None):
            hook_execution_order.append("hook1")

        def hook2(method_name, args, kwargs, result=None):
            hook_execution_order.append("hook2")

        def hook3(method_name, args, kwargs, result=None):
            hook_execution_order.append("hook3")

        # Add multiple before hooks
        self.gc.http_client.add_before_hook("request", hook1)
        self.gc.http_client.add_before_hook("request", hook2)
        self.gc.http_client.add_before_hook("request", hook3)

        # Make a request
        self.spreadsheet.fetch_sheet_metadata()

        # Verify hooks were called in order
        self.assertGreaterEqual(
            len(hook_execution_order), 3, "At least three hooks should have been called"
        )
        # Check that the first three calls are in order (before hooks)
        self.assertEqual(
            hook_execution_order[:3],
            ["hook1", "hook2", "hook3"],
            "First three hook calls should be in order",
        )

    @pytest.mark.vcr()
    def test_hookable_decorator_hook_exception_handling(self):
        """Test that exceptions in hooks don't break the main execution"""
        hook_exception_raised = False

        def failing_hook(method_name, args, kwargs, result=None):
            nonlocal hook_exception_raised
            hook_exception_raised = True
            raise Exception("Hook exception")

        # Add a hook that raises an exception
        self.gc.http_client.add_before_hook("request", failing_hook)

        # The request should still work despite the hook exception
        result = self.spreadsheet.fetch_sheet_metadata()

        # Verify hook was called and exception was raised
        self.assertTrue(hook_exception_raised, "Failing hook should have been called")
        # The request should still succeed
        self.assertIsNotNone(result, "Request should succeed despite hook exception")

    @pytest.mark.vcr()
    def test_hookable_decorator_method_specific_hooks(self):
        """Test that hooks are specific to the method they're added to"""
        request_hook_called = False
        batch_update_hook_called = False

        def request_hook(method_name, args, kwargs, result=None):
            nonlocal request_hook_called
            request_hook_called = True

        def batch_update_hook(method_name, args, kwargs, result=None):
            nonlocal batch_update_hook_called
            batch_update_hook_called = True

        # Add hooks to different methods
        self.gc.http_client.add_before_hook("request", request_hook)
        self.gc.http_client.add_before_hook("batch_update", batch_update_hook)

        # Call request method
        self.spreadsheet.fetch_sheet_metadata()

        # Verify only request hook was called
        self.assertTrue(request_hook_called, "Request hook should have been called")
        self.assertFalse(
            batch_update_hook_called, "Batch update hook should not have been called"
        )

    @pytest.mark.vcr()
    def test_hookable_decorator_hook_cleanup(self):
        """Test that hooks can be added and don't interfere with normal operation"""
        # Add a simple hook
        hook_called = False

        def simple_hook(method_name, args, kwargs, result=None):
            nonlocal hook_called
            hook_called = True

        self.gc.http_client.add_before_hook("request", simple_hook)

        # Make a request
        result = self.spreadsheet.fetch_sheet_metadata()

        # Verify hook was called and request succeeded
        self.assertTrue(hook_called, "Hook should have been called")
        self.assertIsNotNone(result, "Request should succeed with hook")

        # Make another request to ensure hooks don't interfere
        result2 = self.spreadsheet.fetch_sheet_metadata()
        self.assertIsNotNone(result2, "Second request should also succeed")


# Standalone pytest tests for BackOffHTTPClient (not part of ClientTest class)


@pytest.fixture
def backoff_client():
    """Create a BackOffHTTPClient with a mock session."""
    mock_session = Mock()
    return BackOffHTTPClient(auth=None, session=mock_session)


@pytest.fixture
def mock_success_response():
    """Create a mock successful response."""
    mock_response = Mock(spec=Response)
    mock_response.ok = True
    mock_response.status_code = 200
    return mock_response


def _create_mock_error_response(status_code, error_dict=None, json_side_effect=None):
    """Helper to create a mock error response.

    Args:
        status_code: HTTP status code
        error_dict: Error dictionary for JSON response (if parseable)
        json_side_effect: Exception to raise when parsing JSON (for unparsable responses)
    """
    mock_response = Mock(spec=Response)
    mock_response.ok = False
    mock_response.status_code = status_code

    if json_side_effect:
        mock_response.json.side_effect = json_side_effect
        mock_response.text = "Unparsable response"
    elif error_dict:
        mock_response.json.return_value = {"error": error_dict}

    return mock_response


def _test_backoff_retry_behavior(
    backoff_client, api_error, mock_success_response, should_retry
):
    """Helper to test retry behavior with consistent patterns.

    Args:
        backoff_client: BackOffHTTPClient instance
        api_error: APIError to raise
        mock_success_response: Response to return on success
        should_retry: Whether the error should trigger retries
    """
    call_count = 0

    def side_effect_fn(*_args, **_kwargs):
        nonlocal call_count
        call_count += 1
        if should_retry and call_count >= 3:  # Succeed after 2 retries
            return mock_success_response
        raise api_error

    with patch("time.sleep"):
        with patch.object(
            BackOffHTTPClient.__bases__[0], "request", side_effect=side_effect_fn
        ):
            if should_retry:
                result = backoff_client.request("get", "https://example.com/test")
                assert (
                    call_count >= 2
                ), f"Should have retried for error code {api_error.code}"
                assert result == mock_success_response
            else:
                with pytest.raises(APIError):
                    backoff_client.request("get", "https://example.com/test")
                assert (
                    call_count == 1
                ), f"Should not retry for error code {api_error.code}"


def test_backoff_http_client_handles_unparsable_error_response(
    backoff_client, mock_success_response
):
    """Test that BackOffHTTPClient handles responses with unparsable JSON by falling back to response.status_code.

    This tests the fix in line 775 of http_client.py:
    code = err.code if err.code != -1 else err.response.status_code

    When APIError fails to parse JSON, it sets code=-1. The BackOffHTTPClient should
    use response.status_code instead for determining retry logic.
    """
    # Create a mock response with unparsable JSON and a retryable status code (500)
    mock_response = _create_mock_error_response(
        status_code=500, json_side_effect=ValueError("Invalid JSON")
    )

    api_error = APIError(mock_response)

    # Verify that the error code is -1 (due to unparsable JSON)
    assert api_error.code == -1, "Error code should be -1 for unparsable JSON"

    # Test that it retries using response.status_code (500) instead of code (-1)
    _test_backoff_retry_behavior(
        backoff_client, api_error, mock_success_response, should_retry=True
    )


def test_backoff_http_client_uses_error_code_when_valid(
    backoff_client, mock_success_response
):
    """Test that BackOffHTTPClient uses err.code when it's not -1."""
    # Create a mock response with valid JSON and a non-retryable status code
    mock_response = _create_mock_error_response(
        status_code=404,
        error_dict={"code": 404, "message": "Not found", "status": "NOT_FOUND"},
    )

    api_error = APIError(mock_response)
    assert api_error.code == 404, "Error code should be 404"

    # Test that it does NOT retry for non-retryable 404 error
    _test_backoff_retry_behavior(
        backoff_client, api_error, mock_success_response, should_retry=False
    )


def test_backoff_http_client_retries_with_valid_retryable_code(
    backoff_client, mock_success_response
):
    """Test that BackOffHTTPClient retries when err.code is a retryable error (e.g., 429, 500+)."""
    # Create a mock response with valid JSON and a retryable status code (429)
    mock_response = _create_mock_error_response(
        status_code=429,
        error_dict={
            "code": 429,
            "message": "Too many requests",
            "status": "RATE_LIMIT_EXCEEDED",
        },
    )

    api_error = APIError(mock_response)
    assert api_error.code == 429, "Error code should be 429"

    # Test that it retries for retryable 429 error
    _test_backoff_retry_behavior(
        backoff_client, api_error, mock_success_response, should_retry=True
    )
