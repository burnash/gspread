# -*- coding: utf-8 -*-

"""
gspread.client
~~~~~~~~~~~~~~

This module contains Client class responsible for communicating with
Google Data API.

"""
import re
import warnings

from xml.etree import ElementTree

from . import __version__
from . import urlencode
from .ns import _ns
from .httpsession import HTTPSession, HTTPError
from .models import Spreadsheet
from .urls import construct_url
from .utils import finditem
from .exceptions import (AuthenticationError, SpreadsheetNotFound,
                         NoValidUrlKeyFound, UpdateCellError,
                         RequestError)


AUTH_SERVER = 'https://www.google.com'
SPREADSHEETS_SERVER = 'spreadsheets.google.com'

_url_key_re_v1 = re.compile(r'key=([^&#]+)')
_url_key_re_v2 = re.compile(r'spreadsheets/d/([^&#]+)/edit')


class Client(object):

    """An instance of this class communicates with Google Data API.

    :param auth: A tuple containing an *email* and a *password* used for ClientLogin
                 authentication or an OAuth2 credential object. Credential objects are those created by the
                 oauth2client library. https://github.com/google/oauth2client
    :param http_session: (optional) A session object capable of making HTTP requests while persisting headers.
                                    Defaults to :class:`~gspread.httpsession.HTTPSession`.

    >>> c = gspread.Client(auth=('user@example.com', 'qwertypassword'))

    or

    >>> c = gspread.Client(auth=OAuthCredentialObject)


    """
    def __init__(self, auth, http_session=None):
        self.auth = auth
        self.session = http_session or HTTPSession()

    def _get_auth_token(self, content):
        for line in content.splitlines():
            if line.startswith('Auth='):
                return line[5:]
        return None

    def _deprecation_warning(self):
        warnings.warn("""
            ClientLogin is deprecated:
            https://developers.google.com/identity/protocols/AuthForInstalledApps?csw=1

            Authorization with email and password will stop working on April 20, 2015.

            Please use oAuth2 authorization instead:
            http://gspread.readthedocs.org/en/latest/oauth2.html

        """, Warning)

    def _add_xml_header(self, data):
        return "<?xml version='1.0' encoding='UTF-8'?>%s" % data.decode()

    def login(self):
        """Authorize client using ClientLogin protocol.

        The credentials provided in `auth` parameter to class' constructor will be used.

        This method is using API described at:
        http://code.google.com/apis/accounts/docs/AuthForInstalledApps.html

        :raises AuthenticationError: if login attempt fails.

        """
        source = 'burnash-gspread-%s' % __version__
        service = 'wise'

        if hasattr(self.auth, 'access_token'):
            if not self.auth.access_token or \
                    (hasattr(self.auth, 'access_token_expired') and self.auth.access_token_expired):
                import httplib2

                http = httplib2.Http()
                self.auth.refresh(http)

            self.session.add_header('Authorization', "Bearer " + self.auth.access_token)

        else:
            self._deprecation_warning()

            data = {'Email': self.auth[0],
                    'Passwd': self.auth[1],
                    'accountType': 'HOSTED_OR_GOOGLE',
                    'service': service,
                    'source': source}

            url = AUTH_SERVER + '/accounts/ClientLogin'

            try:
                r = self.session.post(url, data)
                content = r.read().decode()
                token = self._get_auth_token(content)
                auth_header = "GoogleLogin auth=%s" % token
                self.session.add_header('Authorization', auth_header)

            except HTTPError as ex:
                if ex.message.strip() == '403: Error=BadAuthentication':
                    raise AuthenticationError("Incorrect username or password")
                else:
                    raise AuthenticationError(
                        "Unable to authenticate. %s" % ex.message)

    def open(self, title):
        """Opens a spreadsheet, returning a :class:`~gspread.Spreadsheet` instance.

        :param title: A title of a spreadsheet.

        If there's more than one spreadsheet with same title the first one
        will be opened.

        :raises gspread.SpreadsheetNotFound: if no spreadsheet with
                                             specified `title` is found.

        >>> c = gspread.Client(auth=('user@example.com', 'qwertypassword'))
        >>> c.login()
        >>> c.open('My fancy spreadsheet')

        """
        feed = self.get_spreadsheets_feed()

        for elem in feed.findall(_ns('entry')):
            elem_title = elem.find(_ns('title')).text
            if elem_title.strip() == title:
                return Spreadsheet(self, elem)
        else:
            raise SpreadsheetNotFound

    def open_by_key(self, key):
        """Opens a spreadsheet specified by `key`, returning a :class:`~gspread.Spreadsheet` instance.

        :param key: A key of a spreadsheet as it appears in a URL in a browser.

        :raises gspread.SpreadsheetNotFound: if no spreadsheet with
                                             specified `key` is found.

        >>> c = gspread.Client(auth=('user@example.com', 'qwertypassword'))
        >>> c.login()
        >>> c.open_by_key('0BmgG6nO_6dprdS1MN3d3MkdPa142WFRrdnRRUWl1UFE')

        """
        feed = self.get_spreadsheets_feed()
        for elem in feed.findall(_ns('entry')):
            alter_link = finditem(lambda x: x.get('rel') == 'alternate',
                                  elem.findall(_ns('link')))
            m = _url_key_re_v1.search(alter_link.get('href'))
            if m and m.group(1) == key:
                return Spreadsheet(self, elem)

            m = _url_key_re_v2.search(alter_link.get('href'))
            if m and m.group(1) == key:
                return Spreadsheet(self, elem)

        else:
            raise SpreadsheetNotFound

    def open_by_url(self, url):
        """Opens a spreadsheet specified by `url`,
           returning a :class:`~gspread.Spreadsheet` instance.

        :param url: URL of a spreadsheet as it appears in a browser.

        :raises gspread.SpreadsheetNotFound: if no spreadsheet with
                                             specified `url` is found.

        >>> c = gspread.Client(auth=('user@example.com', 'qwertypassword'))
        >>> c.login()
        >>> c.open_by_url('https://docs.google.com/spreadsheet/ccc?key=0Bm...FE&hl')

        """
        m1 = _url_key_re_v1.search(url)
        if m1:
            return self.open_by_key(m1.group(1))

        else:
            m2 = _url_key_re_v2.search(url)
            if m2:
                return self.open_by_key(m2.group(1))

            else:
                raise NoValidUrlKeyFound

    def openall(self, title=None):
        """Opens all available spreadsheets,
           returning a list of a :class:`~gspread.Spreadsheet` instances.

        :param title: (optional) If specified can be used to filter
                      spreadsheets by title.

        """
        feed = self.get_spreadsheets_feed()
        result = []
        for elem in feed.findall(_ns('entry')):
            if title is not None:
                elem_title = elem.find(_ns('title')).text
                if elem_title.strip() != title:
                    continue
            result.append(Spreadsheet(self, elem))

        return result

    def get_spreadsheets_feed(self, visibility='private', projection='full'):
        url = construct_url('spreadsheets',
                            visibility=visibility, projection=projection)

        r = self.session.get(url)
        return ElementTree.fromstring(r.read())

    def get_worksheets_feed(self, spreadsheet,
                            visibility='private', projection='full'):
        url = construct_url('worksheets', spreadsheet,
                            visibility=visibility, projection=projection)

        r = self.session.get(url)
        return ElementTree.fromstring(r.read())

    def get_cells_feed(self, worksheet,
                       visibility='private', projection='full', params=None):

        url = construct_url('cells', worksheet,
                            visibility=visibility, projection=projection)

        if params:
            params = urlencode(params)
            url = '%s?%s' % (url, params)

        r = self.session.get(url)
        return ElementTree.fromstring(r.read())

    def get_feed(self, url):
        r = self.session.get(url)
        return ElementTree.fromstring(r.read())

    def del_worksheet(self, worksheet):
        url = construct_url(
            'worksheet', worksheet, 'private', 'full', worksheet_version=worksheet.version)
        r = self.session.delete(url)
        # Even though there is nothing interesting in the response body
        # we have to read it or the next request from this session will get a
        # httplib.ResponseNotReady error.
        r.read()

    def get_cells_cell_id_feed(self, worksheet, cell_id,
                               visibility='private', projection='full'):
        url = construct_url('cells_cell_id', worksheet, cell_id=cell_id,
                            visibility=visibility, projection=projection)

        r = self.session.get(url)
        return ElementTree.fromstring(r.read())

    def put_feed(self, url, data):
        headers = {'Content-Type': 'application/atom+xml',
                   'If-Match': '*'}
        data = self._add_xml_header(data)

        try:
            r = self.session.put(url, data, headers=headers)
        except HTTPError as ex:
            if ex.code == 403:
                message = ex.read().decode()
                raise UpdateCellError(message)
            else:
                raise ex

        return ElementTree.fromstring(r.read())

    def post_feed(self, url, data):
        headers = {'Content-Type': 'application/atom+xml'}
        data = self._add_xml_header(data)

        try:
            r = self.session.post(url, data, headers=headers)
        except HTTPError as ex:
            message = ex.read().decode()
            raise RequestError(message)

        return ElementTree.fromstring(r.read())

    def post_cells(self, worksheet, data):
        headers = {'Content-Type': 'application/atom+xml',
                   'If-Match': '*'}
        data = self._add_xml_header(data)
        url = construct_url('cells_batch', worksheet)
        r = self.session.post(url, data, headers=headers)

        return ElementTree.fromstring(r.read())


def login(email, password):
    """Login to Google API using `email` and `password`.

    This is a shortcut function which instantiates :class:`Client`
    and performs login right away.

    :returns: :class:`Client` instance.

    """
    client = Client(auth=(email, password))
    client.login()
    return client

def authorize(credentials):
    """Login to Google API using OAuth2 credentials.

    This is a shortcut function which instantiates :class:`Client`
    and performs login right away.

    :returns: :class:`Client` instance.

    """
    client = Client(auth=credentials)
    client.login()
    return client

