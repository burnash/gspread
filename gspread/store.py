credential_file = '.persargs.json'
credential_path = os.path.expanduser('~') + '/' + credential_file


'''
{
"Access_token": "ya29.AHES6ZToC-JWyvh0AQ_Kz4h3LoBA3d5EOYPFQkTjIbFwt4z90L3M2Q", 
"Redirect_URI": "urn:ietf:wg:oauth:2.0:oob", 
"Client_Id": "32686918642.apps.googleusercontent.com", 
"Client_secret": "WpSlnpIjM6zW8n915ejhN4hj", 
"Refresh_token": "1/CBzEIfaeD3fYv9qRb6hL_1XtspGQCG9JX-kPiURPleY", 
"Document_key": "0Ao882NWHcSjgdHJJSURUSE04QVhQRUxTbWJLOHJZT0E"
}
'''




class Store(object) :

    credentials = {}
    def __init__ (
            self
          , access_token = None
          , redirect_uri = 'urn:ietf:wg:oauth:2.0:oob'
          , client_id = None
          , client_secret = None
          , refresh_token = None
        ):
        
        self.credentials['access_token'] = access_token
        self.credentials['redirect_uri'] = redirect_uri
        self.credentials['client_id'] = client_id
        self.credentials['client_secret'] = client_secret
        self.credentials['refresh_token'] = refresh_token
        
    def load():

        try:
            with open(credential_path, 'rb') as fileCredentials:
                self.credentials = json.load(fileCredentials)
        except IOError:
            print "Found no credentials file : '" + credential_path + "'.  Creating one now ..."
            save(self.credentials)
            
        return self.credentials

    def save(creds):

        with open(credential_path, 'wb') as fileCredentials:
            json.dump(creds, fileCredentials)
            
        os.chmod(credential_path, 0600)

        return


