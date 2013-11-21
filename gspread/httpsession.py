# -*- coding: utf-8 -*-

"""
gspread.httpsession
~~~~~~~~~~~~~~~~~~~

This module contains a class for working with http sessions.

"""

import time
from json import loads

try:
    import httplib as client
    from urlparse import urlparse
    from urllib import urlencode
except ImportError:
    from http import client
    from urllib.parse import urlparse
    from urllib.parse import urlencode

try:
    unicode
except NameError:
    basestring = unicode = str


GOOGLE_OAUTH_TOKEN_REFRESH_URL = "https://accounts.google.com/o/oauth2/token"
GOOGLEZ_TOKEN_EXPIRY_PHRASE = "token expired"
DELAY_BETWEEN_REFRESH_ATTEMPTS = 5 # seconds
NUMBER_OF_REFRESH_ATTEMPTS = 5

class HTTPError(Exception):
    def __init__(self, response):
        self.code = response.status
        self.response = response

    def read(self):
        return self.response.read()


class HTTPSession(object):
    """Handles HTTP activity while keeping headers persisting across requests.

       :param headers: A dict with initial headers.
    """
    def __init__(self, headers=None):
        self.headers = headers or {}
        self.connections = {}

    def _reqst_(self, method, url, data=None, headers=None):
        if data and not isinstance(data, basestring):
            data = urlencode(data)

        if data is not None:
            data = data.encode()

        # If we have data and Content-Type is not set, set it...
        if data and not headers.get('Content-Type', None):
            headers['Content-Type'] = 'application/x-www-form-urlencoded'
        # If connection for this scheme+location is not established, establish it.
        uri = urlparse(url)
        if not self.connections.get(uri.scheme+uri.netloc):
            if uri.scheme == 'https':
                self.connections[uri.scheme+uri.netloc] = client.HTTPSConnection(uri.netloc)
            else:
                self.connections[uri.scheme+uri.netloc] = client.HTTPConnection(uri.netloc)

        request_headers = self.headers.copy()

        if headers:
            for k, v in headers.items():
                if v is None:
                    del request_headers[k]
                else:
                    request_headers[k] = v

        self.connections[uri.scheme+uri.netloc].request(method, url, data, headers=request_headers)
        response = self.connections[uri.scheme+uri.netloc].getresponse()

        return response

    def request(self, method, url, data=None, headers=None):

        uri = urlparse(url)
        # print "Calling Anton's request handler."
        response = self._reqst_(method, url, data, headers)

        if response.status < 400:
            return response

        # print "Status : {}. Reason : {}.".format(response.status, response.reason)
        if GOOGLEZ_TOKEN_EXPIRY_PHRASE not in response.reason:
                raise HTTPError(response)

        # print "Force replacement of stored connection : {}://{}".format(uri.scheme, uri.netloc)
        self.connections[uri.scheme+uri.netloc] = None

        tries = NUMBER_OF_REFRESH_ATTEMPTS
        while tries > 0 :

            access_token = self.refresh_authorization()
            print "Remember new access token : {}.".format(access_token)
            self.headers['Authorization'] = 'Bearer %s' % access_token

            # print "Calling Anton's request handler."
            response = self._reqst_(method, url, data, headers)

            if response.status < 400:
                return response

            if tries < NUMBER_OF_REFRESH_ATTEMPTS :
                time.sleep(DELAY_BETWEEN_REFRESH_ATTEMPTS)
                # print 'Trying again to refresh. {} tries remain.'.format(tries - 1)
            tries -= 1

        raise HTTPError(response)

    def get(self, url, **kwargs):
        return self.request('GET', url, **kwargs)

    def delete(self, url, **kwargs):
        return self.request('DELETE', url, **kwargs)

    def post(self, url, data=None, headers={}):
        return self.request('POST', url, data=data, headers=headers)

    def put(self, url, data=None, **kwargs):
        return self.request('PUT', url, data=data, **kwargs)

    def add_header(self, name, value):
        self.headers[name] = value

    def keep_credentials(self, credentials):

        '''
        Expects a dict of credentials prepared as follows:

        credentials['grant_type'] = 'refresh_token'
        credentials['refresh_token'] = refresh_token
        credentials['client_secret'] = client_secret
        credentials['client_id'] = client_id
        '''
        self.credentials = credentials

    def refresh_authorization(self):

        '''
        Performs a token refresh cycle as described here :
           https://developers.google.com/youtube/v3/guides/authentication#OAuth2_Refreshing_a_Token
           
        '''
        parms = urlencode(self.credentials)
        req_hdrs = {'Content-Type': 'application/x-www-form-urlencoded'}
        url = urlparse(GOOGLE_OAUTH_TOKEN_REFRESH_URL).netloc

        conn = client.HTTPSConnection(url)
        conn.request('POST', GOOGLE_OAUTH_TOKEN_REFRESH_URL, parms, headers=req_hdrs)
        response = conn.getresponse()

        return loads(response.read().decode())['access_token']

