# -*- coding: utf-8 -*-

"""
gspread.httpsession
~~~~~~~~~~~~~~~~~~~

This module contains a class for working with http sessions.

"""

import os

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


class HTTPError(Exception):
    def __init__(self, response):
        self.code = response.status
        self.response = response

    def read(self):
        return self.response.read()


# urllib defines some functions to detect and extract proxies for different
# systems. Importing urllib does the job of setting 2 commodity functions
import urllib


class HTTPSession(object):
    """Handles HTTP activity while keeping headers persisting across requests.

       :param headers: A dict with initial headers.
    """
    def __init__(self, headers=None):
        self.headers = headers or {}
        self.connections = {}

    def request(self, method, url, data=None, headers=None):
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
            self._setup_connection(uri.scheme, uri.netloc)

        request_headers = self.headers.copy()

        if headers:
            for k, v in headers.items():
                if v is None:
                    del request_headers[k]
                else:
                    request_headers[k] = v

        self.connections[uri.scheme+uri.netloc].request(method, url, data, headers=request_headers)
        response = self.connections[uri.scheme+uri.netloc].getresponse()

        if response.status > 399:
            raise HTTPError(response)
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

    def _setup_connection(self, protocol, netloc):
        """Takes care of managing proxies if any. This is a first attempt to
        manage proxies. Authentication is not yet taken into account. This all
        stuff is not tested yet.

        Parameters
        ----------
        protocol: str
            http or https
        netloc: str
            url to connect to

        Returns
        -------
        HTTP(S)Session
            properly set up in case of proxies
        """
        proxies = urllib.getproxies()
        # We process proxy if a proxy is defined for this protocol and the
        # netloc to connect to is not in the bypass list.
        if protocol in proxies and urllib.proxy_bypass(netloc) == 0:
            proxy = proxies[protocol]
            urltype, proxyhost = urllib.splittype(proxy)
            host, selector = urllib.splithost(proxyhost)
            host, port = urllib.splitport(host)
            if protocol == 'https':
                self.connections[protocol+netloc] = client.HTTPSConnection(host, port)
                self.connections[protocol+netloc].set_tunnel(netloc, 443)
            else:
                self.connections[protocol+netloc] = client.HTTPSConnection(host, port)
                self.connections[protocol+netloc].set_tunnel(netloc, 80)
        else:
            if protocol == 'https':
                self.connections[protocol+netloc] = client.HTTPSConnection(netloc)
            else:
                self.connections[protocol+netloc] = client.HTTPConnection(netloc)
