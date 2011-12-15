# -*- coding: utf-8 -*-

"""
gspread.client
~~~~~~~~~~~~~~

This module contains Client class responsible for communicating with
Google Data API.

"""
import re
import urllib
from xml.etree import ElementTree

from . import __version__
from .ns import _ns
from .httpsession import HTTPSession
from .models import Spreadsheet
from .urls import construct_url
from .utils import finditem
from .exceptions import (AuthenticationError, SpreadsheetNotFound,
                         NoValidUrlKeyFound)

AUTH_SERVER = 'https://www.google.com'
SPREADSHEETS_SERVER = 'spreadsheets.google.com'

_url_key_re = re.compile(r'key=([^&#]+)')


class Client(object):
    """An instance of this class communicates with Google Data API.

    :param auth: A tuple containing an email and a password used for ClientLogin
                 authentication.
    :param http_session: (optional) A session object capable of making HTTP requests while
                         persisting headers. Defaults to gspread.httpsession.HTTPSession.

    """
    def __init__(self, auth, http_session=None):
        self.auth = auth

        if not http_session:
            self.session = HTTPSession()

    def _get_auth_token(self, content):
        for line in content.splitlines():
            if line.startswith('Auth='):
                return line[5:]
        return None

    def login(self):
        """Authorize client using ClientLogin.

        This method is using API described at:
        http://code.google.com/apis/accounts/docs/AuthForInstalledApps.html

        """
        source = 'burnash-gspread-%s' % __version__
        service = 'wise'

        data = {'Email': self.auth[0],
                'Passwd': self.auth[1],
                'accountType': 'HOSTED_OR_GOOGLE',
                'service': service,
                'source': source}

        url = AUTH_SERVER + '/accounts/ClientLogin'

        r = self.session.post(url, data)
        content = r.read()

        if r.code == 200:
            token = self._get_auth_token(content)
            auth_header = "GoogleLogin auth=%s" % token
            self.session.add_header('Authorization', auth_header)

        elif r.code == 403:
            if content.strip() == 'Error=BadAuthentication':
                raise AuthenticationError("Incorrect username or password")
            else:
                raise AuthenticationError("Unable to authenticate. %s code" % r.code)
        else:
            raise AuthenticationError("Unable to authenticate. %s code" % r.code)

    def open(self, title):
        """Open a spreadsheet with specified title.

        If there's more than one spreadsheet with same title the first one
        will be opened.

        """
        feed = self.get_spreadsheets_feed()

        for elem in feed.findall(_ns('entry')):
            elem_title = elem.find(_ns('title')).text
            if elem_title.strip() == title:
                return Spreadsheet(self, elem)
        else:
            raise SpreadsheetNotFound

    def open_by_key(self, key):
        feed = self.get_spreadsheets_feed()
        for elem in feed.findall(_ns('entry')):
            alter_link = finditem(lambda x: x.get('rel') == 'alternate',
                                  elem.findall(_ns('link')))
            m = _url_key_re.search(alter_link.get('href'))
            if m and m.group(1) == key:
                return Spreadsheet(self, elem)
        else:
            raise SpreadsheetNotFound

    def open_by_url(self, url):
        m = _url_key_re.search(url)
        if m:
            return self.open_by_key(m.group(1))
        else:
            raise NoValidUrlKeyFound

    def openall(self, title=None):
        """Open all spreadsheets.

        Return a list of all available spreadsheets.
        Can be filtered with title parameter.

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
            params = urllib.urlencode(params)
            url = '%s?%s' % (url, params)

        r = self.session.get(url)
        return ElementTree.fromstring(r.read())

    def get_cells_cell_id_feed(self, worksheet, cell_id,
                       visibility='private', projection='full'):
        url = construct_url('cells_cell_id', worksheet, cell_id=cell_id,
                            visibility=visibility, projection=projection)

        r = self.session.get(url)
        return ElementTree.fromstring(r.read())

    def put_cell(self, url, data):
        headers = {'Content-Type': 'application/atom+xml'}
        data = "<?xml version='1.0' encoding='UTF-8'?>%s" % data
        r = self.session.put(url, data, headers=headers)

        return ElementTree.fromstring(r.read())

    def post_cells(self, worksheet, data):
        headers = {'Content-Type': 'application/atom+xml'}
        data = "<?xml version='1.0' encoding='UTF-8'?>%s" % data
        url = construct_url('cells_batch', worksheet)
        r = self.session.post(url, data, headers=headers)

        return ElementTree.fromstring(r.read())
