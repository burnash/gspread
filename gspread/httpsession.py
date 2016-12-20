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


from .exceptions import RequestError


class HTTPSession(object):

    """Handles HTTP activity while keeping headers persisting across requests.

       :param headers: A dict with initial headers.
    """

    def __init__(self, headers=None):
        self.headers = headers or {}
        self.requests_session = requests.Session()

    def request(self, method, url, data=None, params=None, headers=None, files=None, json=None):
        if data and isinstance(data, bytes):
            data = data.decode()

        if data and not isinstance(data, basestring):
            data = urlencode(data)

        if data is not None:
            data = data.encode('utf8')

        # If we have data and Content-Type is not set, set it...
        if data and not headers.get('Content-Type', None):
            headers['Content-Type'] = 'application/x-www-form-urlencoded'

        request_headers = self.headers.copy()

        if headers:
            for k, v in headers.items():
                if v is None:
                    del request_headers[k]
                else:
                    request_headers[k] = v

        try:
            func = getattr(self.requests_session, method.lower())
        except AttributeError:
            raise RequestError("HTTP method '{}' is not supported".format(method))

        response = func(url, data=data, params=params, headers=request_headers, files=files, json=json)

        if response.status_code > 399:
            raise RequestError(response.status_code, "{0}: {1}".format(
                response.status_code, response.content))
        return response

    def get(self, url, params=None, **kwargs):
        return self.request('GET', url, params=params, **kwargs)

    def delete(self, url, params=None, **kwargs):
        return self.request('DELETE', url, params=params, **kwargs)

    def post(self, url, data=None, params=None, files=None, headers={}, json=None):
        return self.request('POST', url, params=params, data=data, headers=headers, files=files, json=json)

    def put(self, url, data=None, params=None,  **kwargs):
        return self.request('PUT', url, params=params, data=data, **kwargs)

    def add_header(self, name, value):
        self.headers[name] = value
