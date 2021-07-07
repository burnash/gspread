# -*- coding: utf-8 -*-

"""
gspread.auth
~~~~~~~~~~~~

Simple authentication with OAuth.

"""

import os
from google.oauth2.credentials import Credentials
from google.oauth2.service_account import (
    Credentials as ServiceAccountCredentials,
)
from google_auth_oauthlib.flow import InstalledAppFlow

from .client import Client

DEFAULT_SCOPES = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive',
]

READONLY_SCOPES = [
    'https://www.googleapis.com/auth/spreadsheets.readonly',
    'https://www.googleapis.com/auth/drive.readonly',
]


def get_config_dir(config_dir_name='gspread', os_is_windows=os.name == 'nt'):
    """Construct a config dir path.

    By default:
        * `%APPDATA%\gspread` on Windows
        * `~/.config/gspread` everywhere else

    """
    if os_is_windows:
        return os.path.join(os.environ["APPDATA"], config_dir_name)
    else:
        return os.path.join(
            os.path.expanduser('~'), '.config', config_dir_name
        )


DEFAULT_CONFIG_DIR = get_config_dir()

DEFAULT_CREDENTIALS_FILENAME = os.path.join(
    DEFAULT_CONFIG_DIR, 'credentials.json'
)
DEFAULT_AUTHORIZED_USER_FILENAME = os.path.join(
    DEFAULT_CONFIG_DIR, 'authorized_user.json'
)
DEFAULT_SERVICE_ACCOUNT_FILENAME = os.path.join(
    DEFAULT_CONFIG_DIR, 'service_account.json'
)


def local_server_flow(scopes, port=0, filename=DEFAULT_CREDENTIALS_FILENAME):
    """Run an OAuth flow using a local server strategy.

    Creates an OAuth flow and runs `google_auth_oauthlib.flow.InstalledAppFlow.run_local_server <https://google-auth-oauthlib.readthedocs.io/en/latest/reference/google_auth_oauthlib.flow.html#google_auth_oauthlib.flow.InstalledAppFlow.run_local_server>`_.
    This will start a local web server and open the authorization URL in
    the user’s browser.

    Pass this function to ``flow`` parameter of :meth:`~gspread.oauth` to run
    a local server flow.
    """
    flow = InstalledAppFlow.from_client_secrets_file(filename, scopes)
    return flow.run_local_server(port=port)


def console_flow(scopes, filename=DEFAULT_CREDENTIALS_FILENAME):
    """Run an OAuth flow using a console strategy.

    Creates an OAuth flow and runs `google_auth_oauthlib.flow.InstalledAppFlow.run_console <https://google-auth-oauthlib.readthedocs.io/en/latest/reference/google_auth_oauthlib.flow.html#google_auth_oauthlib.flow.InstalledAppFlow.run_console>`_.

    Pass this function to ``flow`` parameter of :meth:`~gspread.oauth` to run
    a console strategy.
    """
    flow = InstalledAppFlow.from_client_secrets_file(filename, scopes)
    return flow.run_console()


def load_credentials(filename=DEFAULT_AUTHORIZED_USER_FILENAME):
    if os.path.exists(filename):
        return Credentials.from_authorized_user_file(filename)

    return None


def store_credentials(
    creds, filename=DEFAULT_AUTHORIZED_USER_FILENAME, strip='token'
):
    with open(filename, 'w') as f:
        f.write(creds.to_json(strip))


def oauth(
    scopes=DEFAULT_SCOPES,
    flow=local_server_flow,
    credentials_filename=DEFAULT_CREDENTIALS_FILENAME,
    authorized_user_filename=DEFAULT_AUTHORIZED_USER_FILENAME,
):
    """Authenticate with OAuth Client ID.

    By default this function will use the local server strategy and open
    the authorization URL in the user’s browser::

        gc = gspread.oauth()

    Another option is to run a console strategy. This way, the user is
    instructed to open the authorization URL in their browser. Once the
    authorization is complete, the user must then copy & paste the
    authorization code into the application::

        gc = gspread.oauth(flow=gspread.auth.console_flow)


    ``scopes`` parameter defaults to read/write scope available in
    ``gspread.auth.DEFAULT_SCOPES``. It's read/write for Sheets
    and Drive API::

        DEFAULT_SCOPES =[
            'https://www.googleapis.com/auth/spreadsheets',
            'https://www.googleapis.com/auth/drive'
        ]

    You can also use ``gspread.auth.READONLY_SCOPES`` for read only access.
    Obviously any method of ``gspread`` that updates a spreadsheet
    **will not work** in this case::

        gc = gspread.oauth(scopes=gspread.auth.READONLY_SCOPES)

        sh = gc.open("A spreadsheet")
        sh.sheet1.update('A1', '42')   # <-- this will not work

    If you're storing your user credentials in a place other than the
    default, you may provide a path to that file like so::

        gc = gspread.oauth(
            credentials_filename='/alternative/path/credentials.json',
            authorized_user_filename='/alternative/path/authorized_user.json',
        )

    :param list scopes: The scopes used to obtain authorization.
    :param function flow: OAuth flow to use for authentication.
        Defaults to :meth:`~gspread.auth.local_server_flow`
    :param str credentials_filename: Filepath (including name) pointing to a
        credentials `.json` file.
        Defaults to DEFAULT_CREDENTIALS_FILENAME:
            * `%APPDATA%\gspread\credentials.json` on Windows
            * `~/.config/gspread/credentials.json` everywhere else
    :param str authorized_user_filename: Filepath (including name) pointing to
        an authorized user `.json` file.
        Defaults to DEFAULT_AUTHORIZED_USER_FILENAME:
            * `%APPDATA%\gspread\authorized_user.json` on Windows
            * `~/.config/gspread/authorized_user.json` everywhere else

    :rtype: :class:`gspread.Client`
    """
    creds = load_credentials(filename=authorized_user_filename)

    if not creds:
        creds = flow(filename=credentials_filename, scopes=scopes)
        store_credentials(creds, filename=authorized_user_filename)

    client = Client(auth=creds)
    return client


def service_account(
    filename=DEFAULT_SERVICE_ACCOUNT_FILENAME, scopes=DEFAULT_SCOPES
):
    """Authenticate using a service account.

    ``scopes`` parameter defaults to read/write scope available in
    ``gspread.auth.DEFAULT_SCOPES``. It's read/write for Sheets
    and Drive API::

        DEFAULT_SCOPES =[
            'https://www.googleapis.com/auth/spreadsheets',
            'https://www.googleapis.com/auth/drive'
        ]

    You can also use ``gspread.auth.READONLY_SCOPES`` for read only access.
    Obviously any method of ``gspread`` that updates a spreadsheet
    **will not work** in this case.

    :param str filename: The path to the service account json file.
    :param list scopes: The scopes used to obtain authorization.

    :rtype: :class:`gspread.Client`
    """
    creds = ServiceAccountCredentials.from_service_account_file(
        filename, scopes=scopes
    )
    return Client(auth=creds)


def service_account_from_dict(info, scopes=DEFAULT_SCOPES):
    """Authenticate using a service account (json).

    ``scopes`` parameter defaults to read/write scope available in
    ``gspread.auth.DEFAULT_SCOPES``. It's read/write for Sheets
    and Drive API::

        DEFAULT_SCOPES =[
            'https://www.googleapis.com/auth/spreadsheets',
            'https://www.googleapis.com/auth/drive'
        ]

    You can also use ``gspread.auth.READONLY_SCOPES`` for read only access.
    Obviously any method of ``gspread`` that updates a spreadsheet
    **will not work** in this case.

    :param info (Mapping[str, str]): The service account info in Google format
    :param list scopes: The scopes used to obtain authorization.

    :rtype: :class:`gspread.Client`
    """
    creds = ServiceAccountCredentials.from_service_account_info(
        info=info,
        scopes=scopes,
    )
    return Client(auth=creds)
