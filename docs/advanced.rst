Advanced Usage
==============

Custom Authentication
---------------------

Google Colaboratory
~~~~~~~~~~~~~~~~~~~

If you familiar with the Jupyter Notebook, `Google Colaboratory <https://colab.research.google.com/>`_ is probably the easiest way to get started using gspread::

    from google.colab import auth
    auth.authenticate_user()

    import gspread
    from oauth2client.client import GoogleCredentials

    gc = gspread.authorize(GoogleCredentials.get_application_default())

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
            token_url=token_url,
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
