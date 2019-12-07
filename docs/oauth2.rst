Using OAuth2 for Authentication
===============================

OAuth Credentials
-----------------

OAuth credentials can be generated in several different ways using the
`google-auth <https://github.com/googleapis/google-auth-library-python>`_ library provided by Google. If you are
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

2. Under "API & auth", in the API enable "Drive API".

.. image:: https://cloud.githubusercontent.com/assets/264674/7033107/72b75938-dd80-11e4-9a9f-54fb10820976.png
    :alt: Enabled APIs

3. Go to "Credentials" and choose "New Credentials > Service Account Key".

.. image:: https://cloud.githubusercontent.com/assets/1297699/12098271/1616f908-b319-11e5-92d8-767e8e5ec757.png
    :alt: Google Developers Console

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

4. Go to your spreadsheet and share it with a *client_email* from the step above. Otherwise you'll get a ``SpreadsheetNotFound`` exception when trying to access this spreadsheet with gspread.

5. Install `google-auth <https://github.com/googleapis/google-auth-library-python>`_:

::

    pip install --upgrade google-auth

Depending on your system setup you may need to install PyOpenSSL:

::

    pip install PyOpenSSL

6. Now you can read this file, and use the data when constructing your credentials:

::

    import gspread
    from google.oauth2 import service_account

    scope = ['https://spreadsheets.google.com/feeds',
             'https://www.googleapis.com/auth/drive']

    credentials = service_account.Credentials.from_service_account_file('gspread-april-2cd … ba4.json', scope)

    gc = gspread.authorize(credentials)

    wks = gc.open("Where is the money Lebowski?").sheet1


Custom Credentials Objects
--------------------------

If you have another method of authenticating you can easily hack a custom credentials object.

::

    class Credentials (object):
      def __init__ (self, access_token=None):
        self.access_token = access_token

      def refresh (self, http):
        # get new access_token
        # this only gets called if access_token is None
