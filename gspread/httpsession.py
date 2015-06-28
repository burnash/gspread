# -*- coding: utf-8 -*-

"""
gspread.httpsession
~~~~~~~~~~~~~~~~~~~

This module contains a class for working with http sessions.

"""

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


from .exceptions import HTTPError


class HTTPSession(object):

    """Handles HTTP activity while keeping headers persisting across requests.

       :param headers: A dict with initial headers.
    """

    def __init__(self, headers=None):
        self.headers = headers or {}
        self.connections = {}
        self.lastresponse = None

    def request(self, method, url, data=None, headers=None):
        if data and not isinstance(data, basestring):
            data = urlencode(data)

        if data is not None:
            data = data.encode()

        # If we have data and Content-Type is not set, set it...
        if data and not headers.get('Content-Type', None):
            headers['Content-Type'] = 'application/x-www-form-urlencoded'
        # If connection for this scheme+location is not established, establish
        # it.
        uri = urlparse(url)
        
        # A utility method to acquire the connection/client on demand.
        def get_connection():
            if uri.scheme == 'https':
                return client.HTTPSConnection(uri.netloc)
            else:
                return client.HTTPConnection(uri.netloc)
            
        # Get the connection for this uri if not already acquired, and store in session connections.
        if not self.connections.get(uri.scheme + uri.netloc):
            self.connections[uri.scheme + uri.netloc] = get_connection()
            
        # A utility method to call client methods a second time, in case of an initial
        # failure, by re-acquiring the connection.
        def try_again(func, *args, **kwargs):
          try:
              return func(*args, **kwargs)
          except:
              self.connections[uri.scheme + uri.netloc] = get_connection()
              return func(*args, **kwargs)

        request_headers = self.headers.copy()

        if headers:
            for k, v in headers.items():
                if v is None:
                    del request_headers[k]
                else:
                    request_headers[k] = v
        
        try_again(self.connections[uri.scheme + uri.netloc].request, method, url, data, headers=request_headers)
        thisresponse = getattr(self.connections[uri.scheme + uri.netloc], 'getresponse')()

        if thisresponse.status > 399:
            raise HTTPError("%s: %s" % (thisresponse.status, thisresponse.read()))
        # Store this response as an attribute representing the last response.
        self.lastresponse = thisresponse
        return thisresponse

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
