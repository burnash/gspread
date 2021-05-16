# -*- coding: utf-8 -*-

import os
import itertools

from gspread.exceptions import APIError

from betamax import Betamax
from betamax.fixtures.unittest import BetamaxTestCase
from betamax_json_body_serializer import JSONBodySerializer

import gspread
from google.oauth2.service_account import Credentials as ServiceAccountCredentials
from google.oauth2.credentials import Credentials as UserCredentials


CREDS_FILENAME = os.getenv('GS_CREDS_FILENAME')

SCOPE = [
    'https://spreadsheets.google.com/feeds',
    'https://www.googleapis.com/auth/drive.file',
]
DUMMY_ACCESS_TOKEN = '<ACCESS_TOKEN>'

I18N_STR = u'Iñtërnâtiônàlizætiøn'  # .encode('utf8')

Betamax.register_serializer(JSONBodySerializer)


def sanitize_token(interaction, current_cassette):
    headers = interaction.data['request']['headers']
    token = headers.get('Authorization')

    if token is None:
        return

    interaction.data['request']['headers']['Authorization'] = [
        'Bearer %s' % DUMMY_ACCESS_TOKEN
    ]


with Betamax.configure() as config:
    config.cassette_library_dir = 'tests/cassettes'
    config.default_cassette_options['serialize_with'] = 'json_body'
    config.before_record(callback=sanitize_token)

    record_mode = os.environ.get('GS_RECORD_MODE', 'once')
    config.default_cassette_options['record_mode'] = record_mode


def read_credentials(filename):
    return ServiceAccountCredentials.from_service_account_file(filename, scopes=SCOPE)


def prefixed_counter(prefix, start=1):
    c = itertools.count(start)
    for value in c:
        yield u'%s %s' % (prefix, value)


def get_method_name(self_id):
    return self_id.split('.')[-1]


class SleepyClient(gspread.Client):
    HTTP_TOO_MANY_REQUESTS = 429
    DEFAULT_SLEEP_SECONDS = 1

    def request(
        self,
        *args,
        **kwargs
    ):
        try:
            return super().request(*args, **kwargs)
        except APIError as err:
            data = err.response.json()

            if data['error']['code'] == self.HTTP_TOO_MANY_REQUESTS:
                import time
                time.sleep(self.DEFAULT_SLEEP_SECONDS)
                return self.request(*args, **kwargs)
            else:
                raise err


class DummyCredentials(UserCredentials):
    pass


class BetamaxGspreadTest(BetamaxTestCase):
    @classmethod
    def get_temporary_spreadsheet_title(cls):
        return 'Test %s' % cls.__name__

    @classmethod
    def setUpClass(cls):
        if CREDS_FILENAME:
            from google.auth.transport.requests import Request

            cls.auth_credentials = read_credentials(CREDS_FILENAME)
            cls.base_gc = gspread.authorize(cls.auth_credentials)

            cls.auth_credentials.refresh(Request(cls.base_gc.session))

            title = 'Test %s' % cls.__name__
            cls.temporary_spreadsheet = cls.base_gc.create(title)
        else:
            cls.auth_credentials = DummyCredentials(DUMMY_ACCESS_TOKEN)

    @classmethod
    def tearDownClass(cls):
        try:
            cls.base_gc.del_spreadsheet(cls.temporary_spreadsheet.id)
        except AttributeError:
            pass

    def setUp(self):
        super(BetamaxGspreadTest, self).setUp()
        self.session.headers.update({'accept-encoding': 'identity'})
        self.gc = SleepyClient(self.auth_credentials, session=self.session)

        self.session.headers.update({
            'Authorization': 'Bearer %s' % self.auth_credentials.token
        })

        self.assertTrue(isinstance(self.gc, gspread.client.Client))


class GspreadTest(BetamaxGspreadTest):
    def _sequence_generator(self):
        return prefixed_counter(get_method_name(self.id()))
