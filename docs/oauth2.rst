Authentication
==============

To access spreadsheets your application needs to authenticate itself with the Google Sheets API. Choose from the following options.

#. Create an :ref:`API key <api-key>` if you’d like to only open public spreadsheets.
#. (or) Create a :ref:`OAuth Client ID <oauth-client-id>` if you’d like to access spreadsheets on behalf of end users (including yourself).

   - When your application runs, it will prompt the user to authorize it.

#. (or) Create a :ref:`Service Account <service-account>` to access spreadsheets as a standalone bot.

   - Service accounts get their own email address, so can be authorized by sharing the Sheet with the account in the same way it is shared with a person.
   - Service accounts don't need any explicit permissions to access Sheets that are shared to "anyone with the URL".

An API Key is the easiest option, but to access private Sheets you need authorization. To provide that interactively, use an OAuth Client ID. To pre-configure authorization, use a Service Account.


.. _enable-api-access:

Enable API Access for a Project
-------------------------------

1. Head to `Google Developers Console <https://console.developers.google.com/>`_ and create a new project (or select the one you already have).

2. In the box labeled "Search for APIs and Services", search for "Google Drive API" and enable it.

3. In the box labeled "Search for APIs and Services", search for "Google Sheets API" and enable it.


.. _service-account:

For Bots: Using Service Account
-------------------------------

A service account is a special type of Google account intended to represent a non-human user that needs to authenticate and be authorized to access data in Google APIs [sic].

Since it's a separate account, by default it does not have access to any spreadsheet until you share it with this account. Just like any other Google account.

Here's how to get one:

1. :ref:`enable-api-access` if you haven't done it yet.

2. Go to "APIs & Services > Credentials" and choose "Create credentials > Service account key".

3. Fill out the form

4. Click "Create" and "Done".

5. Press "Manage service accounts" above Service Accounts.

6. Press on **⋮** near recently created service account and select "Manage keys" and then click on "ADD KEY > Create new key".

7. Select JSON key type and press "Create".

You will automatically download a JSON file with credentials. It may look like this:

::

    {
        "type": "service_account",
        "project_id": "api-project-XXX",
        "private_key_id": "2cd … ba4",
        "private_key": "-----BEGIN PRIVATE KEY-----\nNrDyLw … jINQh/9\n-----END PRIVATE KEY-----\n",
        "client_email": "473000000000-yoursisdifferent@developer.gserviceaccount.com",
        "client_id": "473 … hd.apps.googleusercontent.com",
        ...
    }

Remember the path to the downloaded credentials file. Also, in the next step you'll need the value of *client_email* from this file.

6. Very important! Go to your spreadsheet and share it with a *client_email* from the step above. Just like you do with any other Google account. If you don't do this, you'll get a ``gspread.exceptions.SpreadsheetNotFound`` exception when trying to access this spreadsheet from your application or a script.

7. Move the downloaded file to ``~/.config/gspread/service_account.json``. Windows users should put this file to ``%APPDATA%\gspread\service_account.json``.

8. Create a new Python file with this code:

::

    import gspread

    gc = gspread.service_account()

    sh = gc.open("Example spreadsheet")

    print(sh.sheet1.get('A1'))

Ta-da!

.. NOTE::
    If you want to store the credentials file somewhere else, specify the path to `service_account.json` in :meth:`~gspread.service_account`:
    ::

        gc = gspread.service_account(filename='path/to/the/downloaded/file.json')

    Make sure you store the credentials file in a safe place.

For the curious, under the hood :meth:`~gspread.service_account` loads your credentials and authorizes gspread. Similarly to the code
that has been used for authentication prior to the gspread version 3.6:

::

    from google.oauth2.service_account import Credentials

    scopes = [
        'https://www.googleapis.com/auth/spreadsheets',
        'https://www.googleapis.com/auth/drive'
    ]

    credentials = Credentials.from_service_account_file(
        'path/to/the/downloaded/file.json',
        scopes=scopes
    )

    gc = gspread.authorize(credentials)

There is also the option to pass credentials as a dictionary:

::

    import gspread
    
    credentials = {
        "type": "service_account",
        "project_id": "api-project-XXX",
        "private_key_id": "2cd … ba4",
        "private_key": "-----BEGIN PRIVATE KEY-----\nNrDyLw … jINQh/9\n-----END PRIVATE KEY-----\n",
        "client_email": "473000000000-yoursisdifferent@developer.gserviceaccount.com",
        "client_id": "473 … hd.apps.googleusercontent.com",
        ...
    }

    gc = gspread.service_account_from_dict(credentials)

    sh = gc.open("Example spreadsheet")

    print(sh.sheet1.get('A1'))

.. NOTE::
   Older versions of gspread have used `oauth2client <https://github.com/google/oauth2client>`_. Google has
   `deprecated <https://google-auth.readthedocs.io/en/latest/oauth2client-deprecation.html>`_
   it in favor of `google-auth`. If you're still using `oauth2client` credentials, the library will convert
   these to `google-auth` for you, but you can change your code to use the new credentials to make sure nothing
   breaks in the future.

.. _oauth-client-id:

For Bots Running inside GCP (Cloud Run, Cloud Functions, Cloud Build): Using Application-Default Credentials
------------------------------------------------------------------------------------------------------------

When your code runs *inside* Google Cloud, every container, function, or build already
has an **identity**—the service account the runtime is configured to use.  
Google injects a short-lived OAuth 2.0 access token for that service account, so you
don’t need to ship or mount a JSON key file.  All you have to do is:

1. :ref:`enable-api-access` if you haven’t done it yet (Sheets API **and** Drive API).

2. Attach a service account to the Cloud Run service / Cloud Function / Cloud Build step.  
   Share the target spreadsheet with the service account’s **email address**  
   (e.g. `my-run-sa@project.iam.gserviceaccount.com`) just as you would with a colleague.

3. Use `google.auth.default()` to pick up the in-runtime credentials and hand them to gspread:

   ::

       import google.auth
       import gspread

       SCOPES = [
           "https://www.googleapis.com/auth/spreadsheets",
           "https://www.googleapis.com/auth/drive",
       ]

       creds, _ = google.auth.default(scopes=SCOPES)
       gc = gspread.authorize(creds)

       sh = gc.open_by_key("1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms")
       print(sh.sheet1.get("A1"))

   * No `GOOGLE_APPLICATION_CREDENTIALS` environment variable.  
   * No JSON key copied into the container.  
   * Tokens are rotated automatically by the platform.

4. **Local testing:** run

   ::

       gcloud auth application-default login \
           --scopes=https://www.googleapis.com/auth/drive,\
           https://www.googleapis.com/auth/spreadsheets

   to emulate the same Application-Default Credentials flow on your laptop.

.. note::
   If you forget to pass the Sheets **and** Drive scopes when calling
   ``google.auth.default(scopes=...)`` you will get a *403: insufficient
   permissions* error even though the code is running on GCP.  Always include
   both scopes.

.. warning::
   ADC proves *who* your code is, but Sheets access is still controlled by the
   spreadsheet’s share list.  Make sure the service account is listed there,
   otherwise you’ll see ``gspread.exceptions.SpreadsheetNotFound``.

For End Users: Using OAuth Client ID
------------------------------------

This is the case where your application or a script is accessing spreadsheets on behalf of an end user. When you use this scenario, your application or a script will ask the end user (or yourself if you're running it) to grant access to the user's data.

1. :ref:`enable-api-access` if you haven't done it yet.
#. Go to "APIs & Services > OAuth Consent Screen." Click the button for "Configure Consent Screen".

  a. In the "1 OAuth consent screen" tab, give your app a name and fill the "User support email" and "Developer contact information". Click "SAVE AND CONTINUE".
  #. There is no need to fill in anything in the tab "2 Scopes", just click "SAVE AND CONTINUE".
  #. In the tab "3 Test users", add the Google account email of the end user, typically your own Google email. Click "SAVE AND CONTINUE".
  #. Double check the "4 Summary" presented and click "BACK TO DASHBOARD".

3. Go to "APIs & Services > Credentials"
#. Click "+ Create credentials" at the top, then select "OAuth client ID".
#. Select "Desktop app", name the credentials and click "Create". Click "Ok" in the "OAuth client created" popup.
#. Download the credentials by clicking the Download JSON button in "OAuth 2.0 Client IDs" section.
#. Move the downloaded file to ``~/.config/gspread/credentials.json``. Windows users should put this file to ``%APPDATA%\gspread\credentials.json``.

Create a new Python file with this code:

::

    import gspread

    gc = gspread.oauth()

    sh = gc.open("Example spreadsheet")

    print(sh.sheet1.get('A1'))

When you run this code, it launches a browser asking you for authentication. Follow the instruction on the web page. Once finished, gspread stores authorized credentials in the config directory next to `credentials.json`.
You only need to do authorization in the browser once, following runs will reuse stored credentials.

.. NOTE::
    If you want to store the credentials file somewhere else, specify the path to `credentials.json` and `authorized_user.json` in :meth:`~gspread.oauth`:
    ::

        gc = gspread.oauth(
            credentials_filename='path/to/the/credentials.json',
            authorized_user_filename='path/to/the/authorized_user.json'
        )

    Make sure you store the credentials file in a safe place.

There is also the option to pass your credentials directly as a python dict. This way you don't have to store them as files or you can store them in your favorite password
manager.

::

    import gspread

    credentials = {
        "installed": {
            "client_id": "12345678901234567890abcdefghijklmn.apps.googleusercontent.com",
            "project_id": "my-project1234",
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            ...
        }
    }
    gc, authorized_user = gspread.oauth_from_dict(credentials)

    sh = gc.open("Example spreadsheet")

    print(sh.sheet1.get('A1'))

Once authenticated you must store the returned json string containing your authenticated user information. Provide that details as a python dict
as second argument in your next `oauth` request to be directly authenticated and skip the flow.

.. NOTE::
    The second time if your authorized user has not expired, you can omit the credentials.
    Be aware, if the authorized user has expired your credentials are required to authenticate again.

::

    import gspread

    credentials = {
        "installed": {
            "client_id": "12345678901234567890abcdefghijklmn.apps.googleusercontent.com",
            "project_id": "my-project1234",
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            ...
        }
    }
    authorized_user = {
        "refresh_token": "8//ThisALONGTOkEn....",
        "token_uri": "https://oauth2.googleapis.com/token",
        "client_id": "12345678901234567890abcdefghijklmn.apps.googleusercontent.com",
        "client_secret": "MySecRet....",
        "scopes": [
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive"
        ],
        "expiry": "1070-01-01T00:00:00.000001Z"
    }
    gc, authorized_user = gspread.oauth_from_dict(credentials, authorized_user)

    sh = gc.open("Example spreadsheet")

    print(sh.sheet1.get('A1'))

.. warning::
    Security credentials file and authorized credentials contain sensitive data. **Do not share these files with others** and treat them like private keys.

    If you are concerned about giving the application access to your spreadsheets and Drive, use Service Accounts.

.. NOTE::
    The user interface of Google Developers Console may be different when you're reading this. If you find that this document is out of sync with the actual UI, please update it. Improvements to the documentation are always welcome.
    Click **Edit on GitHub** in the top right corner of the page, make it better and submit a PR.


.. _api-key:

For public spreadsheets only
----------------------------

An API key is a token that allows an application to open public spreadsheet files.

Here's how to get one:

1. :ref:`enable-api-access` if you haven't done it yet.

2. Go to "APIs & Services > Credentials" and choose "Create credentials > API key"

3. A pop-up should display your newly created key.

4. Copy the key.

5. That's it your key is created.

.. note::

   You can access your key any time later, come back to the "APIs & Services > Credentials" page,
   you'll be able to see your key again.

6. Create a new Python file with this code:

::

    import gspread

    gc = gspread.api_key("<your newly create key>")

    sh = gc.open_by_key("1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms")

    print(sh.sheet1.get('A1'))

Ta-da !

.. note::

   You can only open public keys, this means you can only open spreadsheet files
   using the methods: ``gc.open_by_key`` and ``gc.open_by_url``.

   The method ``gc.open()`` searches your private files to find the one with a matching
   name so it will never work.
