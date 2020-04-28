Advanced Usage
==============

Custom Authentication
---------------------

Using Authlib
~~~~~~~~~~~~~

Using ``Authlib`` instead of ``google-auth``. Authlib has an ``AssertionSession`` which can automatically refresh tokens.::

    import json
    from gspread import Client
    from authlib.client import AssertionSession

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
