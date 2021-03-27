Authentication
==============

To access spreadsheets via Google Sheets API you need to authenticate and authorize your application.

* If you plan to access spreadsheets on behalf of a bot account use :ref:`Service Account <service-account>`.
* If you'd like to access spreadsheets on behalf of end users (including yourself) use :ref:`OAuth Client ID <oauth-client-id>`.

.. _enable-api-access:

Enable API Access for a Project
-------------------------------

1. Head to `Google Developers Console <https://console.developers.google.com/project>`_ and create a new project (or select the one you already have).

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

6. Press on **⋮** near recenlty created service account and select "Manage keys" and then click on "ADD KEY > Create new key".

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
that has been used for authentication prio to the gspread version 3.6:

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


.. NOTE::
   Older versions of gspread have used `oauth2client <https://github.com/google/oauth2client>`_. Google has
   `deprecated <https://google-auth.readthedocs.io/en/latest/oauth2client-deprecation.html>`_
   it in favor of `google-auth`. If you're still using `oauth2client` credentials, the library will convert
   these to `google-auth` for you, but you can change your code to use the new credentials to make sure nothing
   breaks in the future.

.. _oauth-client-id:

For End Users: Using OAuth Client ID
------------------------------------

This is the case where your application or a script is accessing spreadsheets on behalf of an end user. When you use this scenario, your application or a script will ask the end user (or yourself if you're running it) to grant access to the user's data.

1. :ref:`enable-api-access` if you haven't done it yet.
2. Go to "APIs & Services > OAuth Consent Screen." Click the button for "Configure Consent Screen" and follow the directions to give your app a name; you don't need to fill out anything else on that screen. Click Save. 
3. Go to "APIs & Services > Credentials"
4. Click "+ Create credentials" at the top, then select "OAuth client ID".
5. Select "Desktop app", name the credentials and click "Create". Click "Ok" in the "OAuth client created" popup.
6. Download the credentials by clicking the Download JSON button in "OAuth 2.0 Client IDs" section.
7. Move the downloaded file to ``~/.config/gspread/credentials.json``. Windows users should put this file to ``%APPDATA%\gspread\credentials.json``.

Create a new Python file with this code:

::

    import gspread

    gc = gspread.oauth()

    sh = gc.open("Example spreadsheet")

    print(sh.sheet1.get('A1'))

When you run this code, it launches a browser asking you for authentication. Follow the instruction on the web page. Once finished, gspread stores authorized credentials in the config directory next to `credentials.json`.
You only need to do authorization in the browser once, following runs will reuse stored credentials.

.. attention:: Security
    Credentials file and authorized credentials contain sensitive data. **Do not share these files with others** and treat them like private keys.

    If you are concerned about giving the application access to your spreadsheets and Drive, use Service Accounts.

.. NOTE::
    The user interface of Google Developers Console may be different when you're reading this. If you find that this document is out of sync with the actual UI please fix this. Improvements to the documentation are always welcome.
    Click **Edit on GitHub** in the top right corner of the page, make it better and submit a PR.
