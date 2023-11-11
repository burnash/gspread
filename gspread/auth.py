"""
gspread.auth
~~~~~~~~~~~~

Simple authentication with OAuth.

"""

import json
import os
import warnings
from pathlib import Path

from google.oauth2.credentials import Credentials
from google.oauth2.service_account import Credentials as ServiceAccountCredentials
from google_auth_oauthlib.flow import InstalledAppFlow

from .client import Client
from .utils import deprecation_warning

DEFAULT_SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]

READONLY_SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets.readonly",
    "https://www.googleapis.com/auth/drive.readonly",
]


def get_config_dir(config_dir_name="gspread", os_is_windows=os.name == "nt"):
    r"""Construct a config dir path.

    By default:
        * `%APPDATA%\gspread` on Windows
        * `~/.config/gspread` everywhere else

    """
    if os_is_windows:
        return Path(os.environ["APPDATA"], config_dir_name)
    else:
        return Path(Path.home(), ".config", config_dir_name)


DEFAULT_CONFIG_DIR = get_config_dir()

DEFAULT_CREDENTIALS_FILENAME = DEFAULT_CONFIG_DIR / "credentials.json"
DEFAULT_AUTHORIZED_USER_FILENAME = DEFAULT_CONFIG_DIR / "authorized_user.json"
DEFAULT_SERVICE_ACCOUNT_FILENAME = DEFAULT_CONFIG_DIR / "service_account.json"


def authorize(credentials, client_factory=None):
    """Login to Google API using OAuth2 credentials.
    This is a shortcut/helper function which
    instantiates a client using `client_factory`.
    By default :class:`gspread.Client` is used (but could also use
    :class:`gspread.BackoffClient` to avoid rate limiting).

    :returns: An instance of the class produced by `client_factory`.
    :rtype: :class:`gspread.client.Client`
    """
    if client_factory is None:
        client_factory = Client
    else:
        deprecation_warning(
            version="6.0.0",
            msg="client_factory will be replaced by gspread.http_client types",
        )

    return client_factory(auth=credentials)


def local_server_flow(client_config, scopes, port=0):
    """Run an OAuth flow using a local server strategy.

    Creates an OAuth flow and runs `google_auth_oauthlib.flow.InstalledAppFlow.run_local_server <https://google-auth-oauthlib.readthedocs.io/en/latest/reference/google_auth_oauthlib.flow.html#google_auth_oauthlib.flow.InstalledAppFlow.run_local_server>`_.
    This will start a local web server and open the authorization URL in
    the user's browser.

    Pass this function to ``flow`` parameter of :meth:`~gspread.oauth` to run
    a local server flow.
    """
    flow = InstalledAppFlow.from_client_config(client_config, scopes)
    return flow.run_local_server(port=port)


def console_flow(client_config, scopes):
    """Run an OAuth flow using a console strategy.

    Creates an OAuth flow and runs `google_auth_oauthlib.flow.InstalledAppFlow.run_console <https://google-auth-oauthlib.readthedocs.io/en/latest/reference/google_auth_oauthlib.flow.html#google_auth_oauthlib.flow.InstalledAppFlow.run_console>`_.

    Pass this function to ``flow`` parameter of :meth:`~gspread.oauth` to run
    a console strategy.
    """
    # The console flow has been disabled by google
    # see: https://developers.googleblog.com/2022/02/making-oauth-flows-safer.html?m=1#disallowed-oob
    # now: warn the user about this
    # next: remove this deprecated method
    warnings.warn(
        "The gspread.auth.console_flow flow won't succeed.\n"
        "The OAuth out-of-band (OOB) flow is deprecated. "
        "New clients will be unable to use this flow starting on Feb 28, 2022. "
        "This flow will be deprecated for all clients on Oct 3, 2022. "
        "Migrate to an alternative flow: gspread.auth.local_server_flow"
        "see: https://developers.googleblog.com/2022/02/making-oauth-flows-safer.html?m=1#disallowed-oob"
    )
    flow = InstalledAppFlow.from_client_config(client_config, scopes)
    return flow.run_console()


def load_credentials(filename=DEFAULT_AUTHORIZED_USER_FILENAME):
    if filename.exists():
        return Credentials.from_authorized_user_file(filename)

    return None


def store_credentials(creds, filename=DEFAULT_AUTHORIZED_USER_FILENAME, strip="token"):
    filename.parent.mkdir(parents=True, exist_ok=True)
    with filename.open("w") as f:
        f.write(creds.to_json(strip))


def oauth(
    scopes=DEFAULT_SCOPES,
    flow=local_server_flow,
    credentials_filename=DEFAULT_CREDENTIALS_FILENAME,
    authorized_user_filename=DEFAULT_AUTHORIZED_USER_FILENAME,
    client_factory=None,
):
    r"""Authenticate with OAuth Client ID.

    By default this function will use the local server strategy and open
    the authorization URL in the user's browser::

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
    :type client_factory: :class:`gspread.ClientFactory`
    :param client_factory: A factory function that returns a client class.
        Defaults to :class:`gspread.Client` (but could also use
        :class:`gspread.BackoffClient` to avoid rate limiting)

    :rtype: :class:`gspread.client.Client`
    """
    if client_factory is None:
        client_factory = Client
    else:
        deprecation_warning(
            version="6.0.0",
            msg="client_factory will be replaced by gspread.http_client types",
        )

    authorized_user_filename = Path(authorized_user_filename)
    creds = load_credentials(filename=authorized_user_filename)

    if not type(creds) is Credentials:
        with open(credentials_filename) as json_file:
            client_config = json.load(json_file)
        creds = flow(client_config=client_config, scopes=scopes)
        store_credentials(creds, filename=authorized_user_filename)

    return client_factory(auth=creds)


def oauth_from_dict(
    credentials=None,
    authorized_user_info=None,
    scopes=DEFAULT_SCOPES,
    flow=local_server_flow,
    client_factory=None,
):
    r"""Authenticate with OAuth Client ID.

    By default this function will use the local server strategy and open
    the authorization URL in the user's browser::

        gc = gspread.oauth_from_dict()

    Another option is to run a console strategy. This way, the user is
    instructed to open the authorization URL in their browser. Once the
    authorization is complete, the user must then copy & paste the
    authorization code into the application::

        gc = gspread.oauth_from_dict(flow=gspread.auth.console_flow)


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

        gc = gspread.oauth_from_dict(scopes=gspread.auth.READONLY_SCOPES)

        sh = gc.open("A spreadsheet")
        sh.sheet1.update('A1', '42')   # <-- this will not work

    This function requires you to pass the credentials directly as
    a python dict. After the first authentication the function returns
    the authenticated user info, this can be passed again to authenticate
    the user without the need to run the flow again.

    ..
        code block below must be explicitly announced using code-block

    .. code-block:: python

        gc = gspread.oauth_from_dict(
                credentials=my_creds,
                authorized_user_info=my_auth_user
        )

    :param dict credentials: The credentials from google cloud platform
    :param dict authorized_user_info: The authenticated user
        if already authenticated.
    :param list scopes: The scopes used to obtain authorization.
    :param function flow: OAuth flow to use for authentication.
        Defaults to :meth:`~gspread.auth.local_server_flow`
    :type client_factory: :class:`gspread.ClientFactory`
    :param client_factory: A factory function that returns a client class.
        Defaults to :class:`gspread.Client` (but could also use
        :class:`gspread.BackoffClient` to avoid rate limiting)

    :rtype: (`gspread.client.Client`, str)
    """
    if client_factory is None:
        client_factory = Client
    else:
        deprecation_warning(
            version="6.0.0",
            msg="client_factory will be replaced by gspread.http_client types",
        )

    creds = None
    if authorized_user_info is not None:
        creds = Credentials.from_authorized_user_info(authorized_user_info, scopes)

    if not creds:
        creds = flow(client_config=credentials, scopes=scopes)

    client = client_factory(auth=creds)

    # must return the creds to the user
    # must strip the token an use the dedicated method from Credentials
    # to return a dict "safe to store".
    return (client, creds.to_json("token"))


def service_account(
    filename=DEFAULT_SERVICE_ACCOUNT_FILENAME,
    scopes=DEFAULT_SCOPES,
    client_factory=None,
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
    :type client_factory: :class:`gspread.ClientFactory`
    :param client_factory: A factory function that returns a client class.
        Defaults to :class:`gspread.Client` (but could also use
        :class:`gspread.BackoffClient` to avoid rate limiting)

    :rtype: :class:`gspread.client.Client`
    """
    if client_factory is None:
        client_factory = Client
    else:
        deprecation_warning(
            version="6.0.0",
            msg="client_factory will be replaced by gspread.http_client types",
        )
    creds = ServiceAccountCredentials.from_service_account_file(filename, scopes=scopes)
    return client_factory(auth=creds)


def service_account_from_dict(info, scopes=DEFAULT_SCOPES, client_factory=None):
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
    :type client_factory: :class:`gspread.ClientFactory`
    :param client_factory: A factory function that returns a client class.
        Defaults to :class:`gspread.Client` (but could also use
        :class:`gspread.BackoffClient` to avoid rate limiting)

    :rtype: :class:`gspread.client.Client`
    """
    if client_factory is None:
        client_factory = Client
    else:
        deprecation_warning(
            version="6.0.0",
            msg="client_factory will be replaced by gspread.http_client types",
        )

    creds = ServiceAccountCredentials.from_service_account_info(
        info=info,
        scopes=scopes,
    )
    return client_factory(auth=creds)
