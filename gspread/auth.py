# -*- coding: utf-8 -*-

"""
gspread.auth
~~~~~~~~~~~~

Simple authentication with OAuth.

"""

import os
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

from .client import Client

DEFAULT_SCOPES = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive'
]

READONLY_SCOPES = [
    'https://www.googleapis.com/auth/spreadsheets.readonly',
    'https://www.googleapis.com/auth/drive.readonly'
]


DEFAULT_CONFIG_DIR = os.path.expanduser('~/.config/gspread')
DEFAULT_CREDENTIALS_FILENAME = os.path.join(
    DEFAULT_CONFIG_DIR,
    'credentials.json'
)
DEFAULT_AUTHORIZED_USER_FILE = os.path.join(
    DEFAULT_CONFIG_DIR,
    'authorized_user.json'
)


def _create_installed_app_flow(scopes):
    return InstalledAppFlow.from_client_secrets_file(
        DEFAULT_CREDENTIALS_FILENAME,
        scopes
    )


def local_server_flow(scopes, port=0):
    flow = _create_installed_app_flow(scopes)
    return flow.run_local_server(port=port)


def console_flow(scopes):
    flow = _create_installed_app_flow(scopes)
    return flow.run_console()


def load_credentials(filename=DEFAULT_AUTHORIZED_USER_FILE):
    if os.path.exists(filename):
        return Credentials.from_authorized_user_file(filename)

    return None


def store_credentials(
    creds,
    filename=DEFAULT_AUTHORIZED_USER_FILE,
    strip='token'
):
    with open(filename, 'w') as f:
        f.write(creds.to_json(strip))


def oauth(scopes=DEFAULT_SCOPES, flow=local_server_flow):
    creds = load_credentials()

    if not creds:
        creds = flow(scopes=scopes)
        store_credentials(creds)

    client = Client(auth=creds)
    return client
