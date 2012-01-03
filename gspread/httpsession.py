# -*- coding: utf-8 -*-

"""
gspread.httpsession
~~~~~~~~~~~~~~~~~~~

This module contains a class for working with http sessions.

"""


try:
    import urllib2 as request
    from urllib import urlencode
    from urllib2 import HTTPError
except ImportError:
    from urllib import request
    from urllib.parse import urlencode
    from urllib.error import HTTPError

try:
    unicode
except NameError:
    basestring = unicode = str


class HTTPSession(object):
    """Handles HTTP activity while keeping headers persisting across requests.

       :param headers: A dict with initial headers.
    """
    def __init__(self, headers=None):
        self.headers = headers or {}

    def request(self, method, url, data=None, headers=None):
        if data and not isinstance(data, basestring):
            data = urlencode(data)

        req = request.Request(url, data)

        if method == 'put':
            req.get_method = lambda: 'PUT'

        request_headers = self.headers.copy()

        if headers:
            for k, v in headers.items():
                if v is None:
                    del request_headers[k]
                else:
                    request_headers[k] = v

        for k, v in request_headers.items():
            req.add_header(k, v)

        try:
            return request.urlopen(req)
        except HTTPError as e:
            raise e

    def get(self, url, **kwargs):
        return self.request('get', url, **kwargs)

    def post(self, url, data=None, **kwargs):
        return self.request('post', url, data=data, **kwargs)

    def put(self, url, data=None, **kwargs):
        return self.request('put', url, data=data, **kwargs)

    def add_header(self, name, value):
        self.headers[name] = value
