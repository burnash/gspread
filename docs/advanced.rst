Advanced Usage
==============

Request Hooks
---------------------

The ``gspread`` http_client object has the ability to add callback function hooks on request events.

- Before the method executes ``add_before_hook``
- After successful execution ``add_success_hook``
- When exceptions occur ``add_exception_hook``
- When timeouts occur ``add_timeout_hook``
- When retryable errors occur (http codes that signal retryable errors) ``add_retry_hook``
- After execution regardless of success/failure ``add_after_hook``

Callback hooks allow for things like logging to occur in the consuming code.

    import logging

    log = logging.getLogger(__name__)

    def before_callback(method_name, args, kwargs, result):
        log.info(f"Request started: {args[0].upper()}: {args[1]}")

    def after_callback(method_name, args, kwargs, result):
        log.info(f"Request ended: OK? {result.ok}")

    ...

    gc = gspread.authorize(creds)
    gc.http_client.add_before_hook("request", before_callback)
    gc.http_client.add_after_callback("request", after_callback)

    gc.open_by_key(sheets_doc_key)

Example Output:

    INFO  __main__ Request started: GET: https://sheets.googleapis.com/v4/spreadsheets/19DxqGsxQyCyNWS_kbDnvvWaZS5ahWCOzQSB0j-yHzOU
    INFO  __main__ Request ended: OK? True

Custom Authentication
---------------------

Google Colaboratory
~~~~~~~~~~~~~~~~~~~

If you familiar with the Jupyter Notebook, `Google Colaboratory <https://colab.research.google.com/>`_ is probably the easiest way to get started using gspread::

    from google.colab import auth
    auth.authenticate_user()

    import gspread
    from google.auth import default
    creds, _ = default()

    gc = gspread.authorize(creds)

See the full example in the `External data: Local Files, Drive, Sheets, and Cloud Storage <https://colab.research.google.com/notebooks/io.ipynb#scrollTo=sOm9PFrT8mGG>`_ notebook.


Using Authlib
~~~~~~~~~~~~~

Using ``Authlib`` instead of ``google-auth``. Similar to `google.auth.transport.requests.AuthorizedSession <https://google-auth.readthedocs.io/en/latest/reference/google.auth.transport.requests.html#google.auth.transport.requests.AuthorizedSession>`_ Authlib's ``AssertionSession`` can automatically refresh tokens.::

    import json
    from gspread import Client
    from authlib.integrations.requests_client import AssertionSession

    def create_assertion_session(conf_file, scopes, subject=None):
        with open(conf_file, 'r') as f:
            conf = json.load(f)

        token_url = conf['token_uri']
        issuer = conf['client_email']
        key = conf['private_key']
        key_id = conf.get('private_key_id')

        header = {'alg': 'RS256'}
        if key_id:
            header['kid'] = key_id

        # Google puts scope in payload
        claims = {'scope': ' '.join(scopes)}
        return AssertionSession(
            grant_type=AssertionSession.JWT_BEARER_GRANT_TYPE,
            token_endpoint=token_url,
            issuer=issuer,
            audience=token_url,
            claims=claims,
            subject=subject,
            key=key,
            header=header,
        )

    scopes = [
        'https://www.googleapis.com/auth/spreadsheets',
        'https://www.googleapis.com/auth/drive',
    ]
    session = create_assertion_session('your-google-conf.json', scopes)
    gc = Client(None, session)

    wks = gc.open("Where is the money Lebowski?").sheet1

    wks.update_acell('B2', "it's down there somewhere, let me take another look.")

    # Fetch a cell range
    cell_list = wks.range('A1:B7')
