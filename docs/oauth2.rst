Using OAuth2 for Authorization
==============================

OAuth Credentials
-----------------

OAuth credentials can be generated in several different ways using the
`oauth2client <https://github.com/google/oauth2client>`_ library provided by Google. If you are
editing spreadsheets for yourself then the easiest way to generate credentials is to use
*Signed Credentials* stored in your application (see example below). If you plan to edit
spreadsheets on behalf of others then visit the
`Google OAuth2 documentation <https://developers.google.com/accounts/docs/OAuth2>`_ for more
information.

Using Signed Credentials
------------------------
::

1. Head to `Google Developers Console <https://console.developers.google.com/project>`_ and create a new project (or select the one you have.)

2. Under "API & auth", in the API enable "Drive API".

.. image:: https://cloud.githubusercontent.com/assets/264674/7033107/72b75938-dd80-11e4-9a9f-54fb10820976.png
    :alt: Enabled APIs

<<<<<<< 95d918ab8c3e881f4363e5f5a50e98f79c768ddf
<<<<<<< a69cd84f789e21aa91b9c488abd3dc4ac39c8361
=======
<<<<<<< HEAD
>>>>>>> # This is a combination of 2 commits.
3. Go to "Credentials" and choose "New Credentials > Service Account Key".

.. image:: https://cloud.githubusercontent.com/assets/1297699/12098271/1616f908-b319-11e5-92d8-767e8e5ec757.png
    :alt: Google Developers Console

=======
3. Go to "Credentials" and hit "Create new Client ID".

.. image:: https://cloud.githubusercontent.com/assets/264674/7033101/5d335e4a-dd80-11e4-96c0-fce81919ec2d.png
    :alt: Google Developers Console

4. Select "Service account". Hitting "Create Client ID" will generate a new Public/Private key pair.

.. image:: https://cloud.githubusercontent.com/assets/264674/7032990/6dfaceb2-dd7f-11e4-8071-1490a5b19c8e.png
    :alt: Create Client ID in Developers Console

>>>>>>> # This is a combination of 2 commits.
You will automatically download a JSON file with this data.

.. image:: https://cloud.githubusercontent.com/assets/264674/7033081/3810ddae-dd80-11e4-8945-34b4ba12f9fa.png
    :alt: Download Credentials JSON from Developers Console

This is how this file may look like:

::

    {
        "private_key_id": "2cd … ba4",
        "private_key": "-----BEGIN PRIVATE KEY-----\nNrDyLw … jINQh/9\n-----END PRIVATE KEY-----\n",
        "client_email": "473 … hd@developer.gserviceaccount.com",
        "client_id": "473 … hd.apps.googleusercontent.com",
        "type": "service_account"
    }

You'll need *client_email* and *private_key*.

<<<<<<< 1b18616bc077716ba1c8ab38db2951f62389eb60
<<<<<<< a69cd84f789e21aa91b9c488abd3dc4ac39c8361
=======
>>>>>>> small date fix in changelog from commit 0a06735a4d
5. Install `oauth2client <https://github.com/google/oauth2client>`_:

::

    pip install --upgrade oauth2client
<<<<<<< 95d918ab8c3e881f4363e5f5a50e98f79c768ddf
<<<<<<< 1b18616bc077716ba1c8ab38db2951f62389eb60

=======
    
>>>>>>> small date fix in changelog from commit 0a06735a4d
=======
<<<<<<< HEAD

=======
    
>>>>>>> # This is a combination of 2 commits.
>>>>>>> # This is a combination of 2 commits.
Depending on your system setup you may need to install PyOpenSSL:

::

    pip install PyOpenSSL

6. Now you can read this file, and use the data when constructing your credentials:
<<<<<<< 1b18616bc077716ba1c8ab38db2951f62389eb60

::

<<<<<<< HEAD
    import gspread
    from oauth2client.service_account import ServiceAccountCredentials

    scope = ['https://spreadsheets.google.com/feeds']

    credentials = ServiceAccountCredentials.from_json_keyfile_name('gspread-april-2cd … ba4.json', scope)

    gc = gspread.authorize(credentials)

    wks = gc.open("Where is the money Lebowski?").sheet1

If using oauth2client < 2.0.0
=======
5. Now you can read this file, and use the data when constructing your credentials:
>>>>>>> # This is a combination of 2 commits.
=======
>>>>>>> small date fix in changelog from commit 0a06735a4d

::

=======
>>>>>>> # This is a combination of 2 commits.
    import json
    import gspread
    from oauth2client.client import SignedJwtAssertionCredentials

    json_key = json.load(open('gspread-april-2cd … ba4.json'))
    scope = ['https://spreadsheets.google.com/feeds']

<<<<<<< 95d918ab8c3e881f4363e5f5a50e98f79c768ddf
<<<<<<< a69cd84f789e21aa91b9c488abd3dc4ac39c8361
=======
<<<<<<< HEAD
>>>>>>> # This is a combination of 2 commits.
    credentials = SignedJwtAssertionCredentials(json_key['client_email'], json_key['private_key'].encode(), scope)

=======
    try:
        credentials = SignedJwtAssertionCredentials(json_key['client_email'], json_key['private_key'], scope)
    except TypeError:
        credentials = SignedJwtAssertionCredentials(json_key['client_email'], bytes(json_key['private_key'], 'utf-8'), scope)
>>>>>>> # This is a combination of 2 commits.
    gc = gspread.authorize(credentials)

    wks = gc.open("Where is the money Lebowski?").sheet1

<<<<<<< 95d918ab8c3e881f4363e5f5a50e98f79c768ddf
<<<<<<< 1b18616bc077716ba1c8ab38db2951f62389eb60
<<<<<<< a69cd84f789e21aa91b9c488abd3dc4ac39c8361
=======
<<<<<<< HEAD
>>>>>>> # This is a combination of 2 commits.
**Note**: Python2 users do not need to encode ``json_key['private_key']`` due to ``str`` and ``bytes`` not being differentiated.


7. Go to Google Sheets and share your spreadsheet with an email you have in your ``json_key['client_email']``. Otherwise you'll get a ``SpreadsheetNotFound`` exception when trying to open it.

=======
=======
<<<<<<< HEAD
>>>>>>> small date fix in changelog from commit 0a06735a4d
6. Go to Google Sheets and share your spreadsheet with an email you have in your ``json_key['client_email']``. Otherwise you'll get a ``SpreadsheetNotFound`` exception when trying to open it.
<<<<<<< HEAD

=======
**Note**: Python 3 users need to cast ``json_key['private_key']`` to ``bytes``. Otherwise you'll get ``TypeError: expected bytes, not str`` exception. Replace the line with ``SignedJwtAssertionCredentials`` call with this:

::

    credentials = SignedJwtAssertionCredentials(json_key['client_email'], bytes(json_key['private_key'], 'utf-8'), scope)


7. Go to Google Sheets and share your spreadsheet with an email you have in your ``json_key['client_email']``. Otherwise you'll get a ``SpreadsheetNotFound`` exception when trying to open it.
>>>>>>> bd23436... Added requirements to the instruction #236

=======
    
>>>>>>> # This is a combination of 2 commits.
Troubleshooting
---------------

oauth2client.client.CryptoUnavailableError: No crypto library available
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If you're getting the "No crypto library available" exception, make sure you have ``PyOpenSSL`` library installed in your environment.
=======
<<<<<<< HEAD
6. Go to Google Sheets and share your spreadsheet with an email you have in your ``json_key['client_email']``. Otherwise you'll get a ``SpreadsheetNotFound`` exception when trying to open it.

=======
**Note**: Python 3 users need to cast ``json_key['private_key']`` to ``bytes``. Otherwise you'll get ``TypeError: expected bytes, not str`` exception. Replace the line with ``SignedJwtAssertionCredentials`` call with this:

::

    credentials = SignedJwtAssertionCredentials(json_key['client_email'], bytes(json_key['private_key'], 'utf-8'), scope)


7. Go to Google Sheets and share your spreadsheet with an email you have in your ``json_key['client_email']``. Otherwise you'll get a ``SpreadsheetNotFound`` exception when trying to open it.
>>>>>>> bd23436... Added requirements to the instruction #236
>>>>>>> # This is a combination of 2 commits.

<<<<<<< a69cd84f789e21aa91b9c488abd3dc4ac39c8361
=======
    
>>>>>>> c7e2983... Troubleshooting No crypto library available exception. 
>>>>>>> # This is a combination of 2 commits.
Custom Credentials Objects
--------------------------

If you have another method of authenicating you can easily hack a custom credentials object.

::

    class Credentials (object):
      def __init__ (self, access_token=None):
        self.access_token = access_token

      def refresh (self, http):
        # get new access_token
        # this only gets called if access_token is None
<<<<<<< 95d918ab8c3e881f4363e5f5a50e98f79c768ddf
<<<<<<< a69cd84f789e21aa91b9c488abd3dc4ac39c8361
=======
<<<<<<< HEAD
>>>>>>> # This is a combination of 2 commits.
=======

>>>>>>> # This is a combination of 2 commits.
