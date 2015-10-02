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

import time

from .exceptions import HTTPError


class HTTPSession(object):

    """Handles HTTP activity while keeping headers persisting across requests.

       :param headers: A dict with initial headers.

       :param tries: (optional) If > 1, try again until that number of times
                                is reached.

    """

    def __init__(self, headers=None, tries=1):
        self.headers = headers or {}
        self.connections = {}
        self.tries = tries

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
        if not self.connections.get(uri.scheme + uri.netloc):
            if uri.scheme == 'https':
                self.connections[
                    uri.scheme + uri.netloc] = client.HTTPSConnection(uri.netloc)
            else:
                self.connections[
                    uri.scheme + uri.netloc] = client.HTTPConnection(uri.netloc)

        request_headers = self.headers.copy()

        if headers:
            for k, v in headers.items():
                if v is None:
                    del request_headers[k]
                else:
                    request_headers[k] = v

        attempts = 0
        while True:
            # Either we'll break out (if no Exception) or we'll reach
            #  the max number of tries and raise an Exception
            try:
                self.connections[
                    uri.scheme + uri.netloc].request(
                        method, url, data, headers=request_headers)
                response = self.connections[
                    uri.scheme + uri.netloc].getresponse()
                if response.status > 399:
                    attempts +=1
                    time.sleep(1)
                    if attempts == self.tries:
                        break
                    # No exception, but still want to retry
                    # Since we got a response, we don't need to close
                    #  the connection (as we do below if there's an exception)
                    continue                
            except client.HTTPException as e:
                # In the case where no response was received, 
                #  We need to close the connection before we retry
                # See https://docs.python.org/2/library/httplib.html
                self.connections[uri.scheme + uri.netloc].close()
                attempts += 1
                time.sleep(1)
                if attempts >= self.tries:
                    raise
            else:
                break
            
        if response.status > 399:
            raise HTTPError(response.status, "%s: %s" % (response.status, response.read()))
        return response

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
