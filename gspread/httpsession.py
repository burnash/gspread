# -*- coding: utf-8 -*-

"""
gspread.httpsession
~~~~~~~~~~~~~~~~~~~

This module contains a class for working with http sessions.

"""

import requests
import time

try:
    from urlparse import urlparse
    from urllib import urlencode
except ImportError:
    from urllib.parse import urlparse
    from urllib.parse import urlencode

try:
    unicode
except NameError:
    basestring = unicode = str


from .exceptions import HTTPError


DEFAULT_MAX_RETRIES = 4


class HTTPSession(object):

    """Handles HTTP activity while keeping headers persisting across requests.

       :param headers: A dict with initial headers.
       :param max_retries: How many times to retry a request when encountering
                           HTTP status code 500 error responses. Default is 4.

    """

    def __init__(self, headers=None, max_retries=None):
        self.headers = headers or {}
        self.requests_session = requests.Session()
        self.max_retries = DEFAULT_MAX_RETRIES if max_retries is None else max_retries

    def request(self, method, url, data=None, headers=None):
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

        done = False
        tries = 0
        while not done:
            tries += 1
            try:
                func = getattr(self.requests_session, method.lower())
            except AttributeError:
                raise Exception("HTTP method '{}' is not supported".format(method))
            response = func(url, data=data, headers=request_headers)

            if response.status_code == 500 and tries <= self.max_retries:
                # Usually a transient error, let's try exponential backoff
                time_sleep = 2 ** tries
                time.sleep(time_sleep)

            elif response.status_code > 399:
                raise HTTPError(response.status_code, "{}: {}".format(
                    response.status_code, response.content))

            else:
                done = True

        return response

    def get(self, url, **kwargs):
        return self.request('GET', url, **kwargs)

    def delete(self, url, **kwargs):
        return self.request('DELETE', url, **kwargs)

    def post(self, url, data=None, headers=None):
        headers = headers or {}
        return self.request('POST', url, data=data, headers=headers)

    def put(self, url, data=None, **kwargs):
        return self.request('PUT', url, data=data, **kwargs)

    def add_header(self, name, value):
        self.headers[name] = value
