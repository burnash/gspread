Using OAuth2 for Authentication
===============================

OAuth Credentials
-----------------

OAuth credentials can be generated in several different ways using the
`google-auth <https://github.com/googleapis/google-auth-library-python>`_ library. If you are
editing spreadsheets for yourself then the easiest way to generate credentials is to use
*Signed Credentials* stored in your application (see example below). If you plan to edit
spreadsheets on behalf of others then visit the
`Google OAuth2 documentation <https://developers.google.com/accounts/docs/OAuth2>`_ for more
information.

.. NOTE::
   In previous versions `oauth2client <https://github.com/google/oauth2client>`_ was used. Google has
   `deprecated <https://google-auth.readthedocs.io/en/latest/oauth2client-deprecation.html>`_
   that in favor of `google-auth`. If you're still using `oauth2client` credentials, the library will convert
   these to `google-auth` for you, but you can change your code to use the new credentials to make sure nothing
   breaks in the future.

Using Signed Credentials
------------------------
::

1. Head to `Google Developers Console <https://console.developers.google.com/project>`_ and create a new project (or select the one you have.)

2. Under "APIs & Services > Library", search for "Drive API" and enable it.
    
3. Under "APIs & Services > Library", search for "Sheets API" and enable it.

4. Go to "APIs & Services > Credentials" and choose "Create credentials > Service account key".

You will automatically download a JSON file with this data.

.. image:: https://cloud.githubusercontent.com/assets/264674/7033081/3810ddae-dd80-11e4-8945-34b4ba12f9fa.png
    :alt: Download Credentials JSON from Developers Console

This is how this file may look like:

::

    {
        "private_key_id": "2cd … ba4",
        "private_key": "-----BEGIN PRIVATE KEY-----\nNrDyLw … jINQh/9\n-----END PRIVATE KEY-----\n",
        "client_email": "473000000000-yoursisdifferent@developer.gserviceaccount.com",
        "client_id": "473 … hd.apps.googleusercontent.com",
        "type": "service_account"
    }

In the next step you'll need the value of *client_email* from the file.

5. Go to your spreadsheet and share it with a *client_email* from the step above. Otherwise you'll get a ``gspread.exceptions.SpreadsheetNotFound`` exception when trying to access this spreadsheet with gspread.

6. Install `google-auth <https://github.com/googleapis/google-auth-library-python>`_:

::

    pip install --upgrade google-auth


7. Now you can read this file, and use the data when constructing your credentials:

::

    import gspread
    from google.oauth2.service_account import Credentials

    scope = ['https://spreadsheets.google.com/feeds',
             'https://www.googleapis.com/auth/drive']

    credentials = Credentials.from_service_account_file('gspread-april-2cd … ba4.json', scopes=scope)

    gc = gspread.authorize(credentials)

    wks = gc.open("Where is the money Lebowski?").sheet1


Custom Credentials Objects
--------------------------

If you have another method of authenticating you can easily hack a custom credentials object.

::

    class Credentials (object):
      def __init__ (self, token=None, expiry=None):
        self.token = token
        self.expiry = expiry

      def refresh (self, http):
        # get new token
        # this only gets called if token is None or if expired

      @property
      def expired(self) -> bool:
        # check if token is expired using expiry
