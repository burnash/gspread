# -*- coding: utf-8 -*-

"""
gspread.httpsession
~~~~~~~~~~~~~~~~~~~

This module contains a class for working with http sessions.

"""

import requests
try:
    from urllib import urlencode
except ImportError:
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
        self.requests_session = requests.Session()

    def request(self, method, url, data=None, headers=None):
        if data and isinstance(data, bytes):
            data = data.decode()

        if data and not isinstance(data, basestring):
            data = urlencode(data)

        if data is not None:
<<<<<<< HEAD
            data = data.encode('utf8')
=======
<<<<<<< 46798d67c38d2cf8e1c751b684897cdc98598205
            data = data.encode()
>>>>>>> # This is a combination of 2 commits.
=======
<<<<<<< HEAD
            data = data.encode('utf8')
=======
            data = data.encode()
>>>>>>> # This is a combination of 2 commits.
>>>>>>> Update README.md
>>>>>>> Update README.md

        # If we have data and Content-Type is not set, set it...
        if data and not headers.get('Content-Type', None):
            headers['Content-Type'] = 'application/x-www-form-urlencoded'
<<<<<<< 46798d67c38d2cf8e1c751b684897cdc98598205
<<<<<<< 95d918ab8c3e881f4363e5f5a50e98f79c768ddf
<<<<<<< a69cd84f789e21aa91b9c488abd3dc4ac39c8361
=======
<<<<<<< HEAD
>>>>>>> # This is a combination of 2 commits.
=======
<<<<<<< HEAD
=======
<<<<<<< HEAD
>>>>>>> Update README.md
=======
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
>>>>>>> # This is a combination of 2 commits.
<<<<<<< 46798d67c38d2cf8e1c751b684897cdc98598205
=======
>>>>>>> Update README.md
>>>>>>> Update README.md

        request_headers = self.headers.copy()

        if headers:
            for k, v in headers.items():
                if v is None:
                    del request_headers[k]
                else:
                    request_headers[k] = v

<<<<<<< 46798d67c38d2cf8e1c751b684897cdc98598205
<<<<<<< 95d918ab8c3e881f4363e5f5a50e98f79c768ddf
<<<<<<< a69cd84f789e21aa91b9c488abd3dc4ac39c8361
=======
<<<<<<< HEAD
>>>>>>> # This is a combination of 2 commits.
=======
<<<<<<< HEAD
=======
<<<<<<< HEAD
>>>>>>> Update README.md
>>>>>>> Update README.md
        try:
            func = getattr(self.requests_session, method.lower())
        except AttributeError:
            raise Exception("HTTP method '{0}' is not supported".format(method))
        response = func(url, data=data, headers=request_headers)
<<<<<<< HEAD

        if response.status_code > 399:
            raise HTTPError(response.status_code, "{}: {}".format(
                response.status_code, response.content))
=======

<<<<<<< 0f67973a7427fb0d14703e22f8f1308f0dfd6af5
        if response.status_code > 399:
            raise HTTPError(response.status_code, "{0}: {1}".format(
                response.status_code, response.content))
=======
<<<<<<< 46798d67c38d2cf8e1c751b684897cdc98598205
<<<<<<< 95d918ab8c3e881f4363e5f5a50e98f79c768ddf
        if response.status > 399:
            raise HTTPError(response.status, "%s: %s" % (response.status, response.read()))
>>>>>>> Squashing all the commits to simpy things for merge
=======
=======
>>>>>>> # This is a combination of 2 commits.
=======
>>>>>>> Update README.md
        self.connections[
            uri.scheme + uri.netloc].request(method, url, data, headers=request_headers)
        response = self.connections[uri.scheme + uri.netloc].getresponse()

        if response.status > 399:
<<<<<<< 46798d67c38d2cf8e1c751b684897cdc98598205
<<<<<<< 95d918ab8c3e881f4363e5f5a50e98f79c768ddf
<<<<<<< 7e91ce60c91237a29536f0b2f609ab27a82d3d68
            raise HTTPError("%s: %s" % (response.status, response.read()))
>>>>>>> # This is a combination of 2 commits.
=======
=======
>>>>>>> # This is a combination of 2 commits.
            raise HTTPError(response.status, "%s: %s" % (response.status, response.read()))
>>>>>>> # This is a combination of 2 commits.
=======
            raise HTTPError(response.status, "%s: %s" % (response.status, response.read()))
>>>>>>> # This is a combination of 2 commits.
>>>>>>> Update README.md
>>>>>>> Update README.md
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
