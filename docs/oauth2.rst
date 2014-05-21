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

    import gspread
    from oauth2client.client import SignedJwtAssertionCredentials
    
    scope = ['https://spreadsheets.google.com/feeds', 'https://docs.google.com/feeds']
    
    credentials = SignedJwtAssertionCredentials('developer@example.com', SIGNED_KEY, scope)
    
    gc = gspread.authorize(credentials)
    wks = gc.open("Where is the money Lebowski?").sheet1
    
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
        
