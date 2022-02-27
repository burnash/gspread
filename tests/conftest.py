import itertools
import os
import unittest

import pytest
import vcr
from google.oauth2.credentials import Credentials as UserCredentials
from google.oauth2.service_account import Credentials as ServiceAccountCredentials

import gspread
from gspread.client import BackoffClient

CREDS_FILENAME = os.getenv("GS_CREDS_FILENAME")
RECORD_MODE = os.getenv("GS_RECORD_MODE", "none")

SCOPE = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive.file",
]
DUMMY_ACCESS_TOKEN = "<ACCESS_TOKEN>"

I18N_STR = "Iñtërnâtiônàlizætiøn"  # .encode('utf8')


def read_credentials(filename):
    return ServiceAccountCredentials.from_service_account_file(filename, scopes=SCOPE)


def prefixed_counter(prefix, start=1):
    c = itertools.count(start)
    for value in c:
        yield "{} {}".format(prefix, value)


def get_method_name(self_id):
    return self_id.split(".")[-1]


def ignore_retry_requests(response):
    SKIP_RECORD = [403, 408, 429]
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
        "path_transformer": vcr.VCR.ensure_suffix(".json"),
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
    def get_temporary_spreadsheet_title(cls, suffix=""):
        return "Test {} {}".format(cls.__name__, suffix)

    @classmethod
    def get_cassette_name(cls):
        return cls.__name__

    def _sequence_generator(self):
        return prefixed_counter(get_method_name(self.id()))


@pytest.fixture(scope="module")
def client():
    if CREDS_FILENAME:
        auth_credentials = read_credentials(CREDS_FILENAME)
    else:
        auth_credentials = DummyCredentials(DUMMY_ACCESS_TOKEN)

    gc = BackoffClient(auth_credentials)
    if not isinstance(gc, gspread.client.Client) is True:
        raise AssertionError

    return gc
