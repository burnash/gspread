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

Head to `Google Developers Console <https://console.developers.google.com/project>`_ and create a new project (or select the one you have.)

Under "API & auth", in the API enable "Drive API". 

.. image:: https://cloud.githubusercontent.com/assets/264674/7033107/72b75938-dd80-11e4-9a9f-54fb10820976.png
    :alt: Enabled APIs

Go to "Credentials" and hit "Create new Client ID".

.. image:: https://cloud.githubusercontent.com/assets/264674/7033101/5d335e4a-dd80-11e4-96c0-fce81919ec2d.png
    :alt: Google Developers Console 

Select "Service account". Hitting "Create Client ID" will generate a new Public/Private key pair.

.. image:: https://cloud.githubusercontent.com/assets/264674/7032990/6dfaceb2-dd7f-11e4-8071-1490a5b19c8e.png
    :alt: Create Client ID in Developers Console

You will automatically download a JSON file with this data.

.. image:: https://cloud.githubusercontent.com/assets/264674/7033081/3810ddae-dd80-11e4-8945-34b4ba12f9fa.png
    :alt: Download Credentials JSON from Developers Console

This is how this file looks like:

::

    {
        "private_key_id": "2cd … ba4",
        "private_key": "-----BEGIN PRIVATE KEY-----\nNrDyLw … jINQh/9\n-----END PRIVATE KEY-----\n",
        "client_email": "473 … hd@developer.gserviceaccount.com",
        "client_id": "473 … hd.apps.googleusercontent.com",
        "type": "service_account"
    }
    
You'll need *client_email* and *private_key*.

Now you can read this file, and use the data when constructing your credentials:

::

    import json
    import gspread
    from oauth2client.client import SignedJwtAssertionCredentials

    json_key = json.load(open('gspread-april-2cd … ba4.json'))
    scope = ['https://spreadsheets.google.com/feeds']
    
    credentials = SignedJwtAssertionCredentials(json_key['client_email'], json_key['private_key'], scope)
    gc = gspread.authorize(credentials)
    
    wks = gc.open("Where is the money Lebowski?").sheet1

That's it. Don't forget to share your spreadsheet with an email you have in your json_key['client_email'].
    
    
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
        
