import io
import itertools
import os
import unittest
from typing import Any, Dict, Generator, Optional, Tuple

import pytest
from google.auth.credentials import Credentials
from google.oauth2.credentials import Credentials as UserCredentials
from google.oauth2.service_account import Credentials as ServiceAccountCredentials
from requests import Response
from vcr import VCR
from vcr.errors import CannotOverwriteExistingCassetteException

import gspread
from gspread.client import Client
from gspread.http_client import BackOffHTTPClient

CREDS_FILENAME = os.getenv("GS_CREDS_FILENAME")
RECORD_MODE = os.getenv("GS_RECORD_MODE", "none")

SCOPE = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive.file",
]
DUMMY_ACCESS_TOKEN = "<ACCESS_TOKEN>"

I18N_STR = "Iñtërnâtiônàlizætiøn"  # .encode('utf8')


def read_credentials(filename: str) -> Credentials:
    return ServiceAccountCredentials.from_service_account_file(filename, scopes=SCOPE)


def prefixed_counter(prefix: str, start: int = 1) -> Generator[str, None, None]:
    c = itertools.count(start)
    for value in c:
        yield "{} {}".format(prefix, value)


def get_method_name(self_id: str) -> str:
    return self_id.split(".")[-1]


def ignore_retry_requests(
    response: Dict[str, Dict[str, int]]
) -> Optional[Dict[str, Dict[str, int]]]:
    SKIP_RECORD = [408, 429]
    if response["status"]["code"] in SKIP_RECORD:
        return None  # do not record

    return response


@pytest.fixture(scope="module")
def vcr_config():
    return {
        "match_on": ["uri", "method"],  # match each query using the uri and the method
        "decode_compressed_response": True,  # decode requests to save clear content
        "record_mode": RECORD_MODE,
        "serializer": "json",
        "path_transformer": VCR.ensure_suffix(".json"),
        "before_record_response": ignore_retry_requests,
        "ignore_hosts": [
            "oauth2.googleapis.com",  # skip oauth requests, in replay mode we don't use them
        ],
        "filter_headers": [
            ("authorization", DUMMY_ACCESS_TOKEN)  # hide token from the recording
        ],
    }


class DummyCredentials(UserCredentials):
    pass


class GspreadTest(unittest.TestCase):
    @classmethod
    def get_temporary_spreadsheet_title(cls, suffix: str = "") -> str:
        return "Test {} {}".format(cls.__name__, suffix)

    @classmethod
    def get_cassette_name(cls) -> str:
        return cls.__name__

    def _sequence_generator(self) -> Generator[str, None, None]:
        return prefixed_counter(get_method_name(self.id()))


class VCRHTTPClient(BackOffHTTPClient):
    def request(self, *args: Any, **kwargs: Any) -> Response:
        try:
            return super().request(*args, **kwargs)
        except CannotOverwriteExistingCassetteException as e:
            if CREDS_FILENAME is None or RECORD_MODE is None:
                raise RuntimeError(
                    """

cannot make new HTTP requests in replay-mode. Please run tests with env variables CREDS_FILENAME and RECORD_MODE
Please refer to contributing guide for details:

https://github.com/burnash/gspread/blob/master/.github/CONTRIBUTING.md
"""
                )

            # necessary env variables were provided, this is a real error
            # like missing access rights on the actual file/folder where to save the cassette
            raise e


class InvalidJsonApiErrorClient(VCRHTTPClient):
    """Special HTTP client that always raises an exception due to 500 error with
    an invalid JSON body.
    In this case for now it returns some HTML to simulate the use of the wrong HTTP endpoint.
    """

    ERROR_MSG = bytes("<html><body><h1>Failed</h1></body></html>", "utf-8")

    def request(self, *args: Any, **kwargs: Any) -> Response:
        resp = Response()
        # fake an HTML response instead of a valid JSON response.
        # urllib3 expect 'raw' to be bytes.
        resp.raw = io.BytesIO(self.ERROR_MSG)
        resp.status_code = 500
        resp.encoding = "text/html"

        # now raise the APIError exception as the regular HTTP client would
        raise gspread.exceptions.APIError(resp)


@pytest.fixture(scope="module")
def client() -> Client:
    if CREDS_FILENAME is not None:
        auth_credentials = read_credentials(CREDS_FILENAME)
    else:
        auth_credentials = DummyCredentials(DUMMY_ACCESS_TOKEN)

    gc = Client(auth=auth_credentials, http_client=VCRHTTPClient)
    if not isinstance(gc, gspread.client.Client) is True:
        raise AssertionError

    return gc


def invalid_json_client() -> Tuple[Client, bytes]:
    """Returns an HTTP client that always returns an invalid JSON payload
    and the expected error message from the raised exception.
    """
    return (
        Client(
            auth=DummyCredentials(DUMMY_ACCESS_TOKEN),
            http_client=InvalidJsonApiErrorClient,
        ),
        InvalidJsonApiErrorClient.ERROR_MSG,
    )
