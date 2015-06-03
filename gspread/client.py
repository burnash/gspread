# -*- coding: utf-8 -*-

"""
gspread.client
~~~~~~~~~~~~~~

This module contains Client class responsible for communicating with
Google Data API.

"""
import re
<<<<<<< 46798d67c38d2cf8e1c751b684897cdc98598205
<<<<<<< a69cd84f789e21aa91b9c488abd3dc4ac39c8361
import json

try:
    import xml.etree.cElementTree as ElementTree
except:
    from xml.etree import ElementTree
=======
<<<<<<< HEAD
>>>>>>> Update README.md
=======
import warnings
<<<<<<< HEAD
=======

try:
    from urllib import urlencode
except ImportError:
    from urllib.parse import urlencode
>>>>>>> # This is a combination of 2 commits.
<<<<<<< 46798d67c38d2cf8e1c751b684897cdc98598205
=======
>>>>>>> Update README.md
>>>>>>> Update README.md

from xml.etree import ElementTree
>>>>>>> # This is a combination of 2 commits.

from . import __version__
from . import urlencode
from .ns import _ns
from .httpsession import HTTPSession, HTTPError
from .models import Spreadsheet
from .urls import construct_url
from .utils import finditem
from .exceptions import (SpreadsheetNotFound, NoValidUrlKeyFound,
                         UpdateCellError, RequestError)


AUTH_SERVER = 'https://www.google.com'
SPREADSHEETS_SERVER = 'spreadsheets.google.com'

_url_key_re_v1 = re.compile(r'key=([^&#]+)')
_url_key_re_v2 = re.compile(r'spreadsheets/d/([^&#]+)/edit')


class Client(object):

    """An instance of this class communicates with Google Data API.

<<<<<<< a69cd84f789e21aa91b9c488abd3dc4ac39c8361
    :param auth: An OAuth2 credential object. Credential objects are those created by the
=======
    :param auth: A tuple containing an *email* and a *password* used for ClientLogin
                 authentication or an OAuth2 credential object. Credential objects are those created by the
>>>>>>> # This is a combination of 2 commits.
                 oauth2client library. https://github.com/google/oauth2client
    :param http_session: (optional) A session object capable of making HTTP requests while persisting headers.
                                    Defaults to :class:`~gspread.httpsession.HTTPSession`.

<<<<<<< 46798d67c38d2cf8e1c751b684897cdc98598205
<<<<<<< a69cd84f789e21aa91b9c488abd3dc4ac39c8361
=======
<<<<<<< HEAD
>>>>>>> Update README.md
    >>> c = gspread.Client(auth=OAuthCredentialObject)
=======
    >>> c = gspread.Client(auth=('user@example.com', 'qwertypassword'))
<<<<<<< HEAD

    or

    >>> c = gspread.Client(auth=OAuthCredentialObject)

<<<<<<< 95d918ab8c3e881f4363e5f5a50e98f79c768ddf
=======
=======
    
    or
    
    >>> c = gspread.Client(auth=OAuthCredentialObject)
    
>>>>>>> # This is a combination of 2 commits.
>>>>>>> # This is a combination of 2 commits.

=======
    >>> c = gspread.Client(auth=('user@example.com', 'qwertypassword'))
<<<<<<< HEAD

    or

    >>> c = gspread.Client(auth=OAuthCredentialObject)

=======
    
    or
    
    >>> c = gspread.Client(auth=OAuthCredentialObject)
    
>>>>>>> # This is a combination of 2 commits.

>>>>>>> Update README.md
    """
    def __init__(self, auth, http_session=None):
        self.auth = auth
        self.session = http_session or HTTPSession()

<<<<<<< 46798d67c38d2cf8e1c751b684897cdc98598205
<<<<<<< a69cd84f789e21aa91b9c488abd3dc4ac39c8361
=======
<<<<<<< HEAD
=======
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

>>>>>>> Update README.md
>>>>>>> Update README.md
    def _ensure_xml_header(self, data):
        if data.startswith(b'<?xml'):
            return data
        else:
            return b'<?xml version="1.0" encoding="utf8"?>' + data
=======
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
>>>>>>> # This is a combination of 2 commits.

    def login(self):
<<<<<<< 46798d67c38d2cf8e1c751b684897cdc98598205
<<<<<<< 95d918ab8c3e881f4363e5f5a50e98f79c768ddf
=======
<<<<<<< HEAD
>>>>>>> Update README.md
        """Authorize client."""
        if not self.auth.access_token or \
                (hasattr(self.auth, 'access_token_expired') and self.auth.access_token_expired):
            import httplib2
=======
        warnings.warn("""
            ClientLogin is deprecated:
            https://developers.google.com/identity/protocols/AuthForInstalledApps?csw=1

            Authorization with email and password will stop working on April 20, 2015.

            Please use oAuth2 authorization instead:
            http://gspread.readthedocs.org/en/latest/oauth2.html

        """, Warning)

        """Authorize client using ClientLogin protocol.

        The credentials provided in `auth` parameter to class' constructor will be used.

        This method is using API described at:
        http://code.google.com/apis/accounts/docs/AuthForInstalledApps.html
>>>>>>> # This is a combination of 2 commits.

<<<<<<< a69cd84f789e21aa91b9c488abd3dc4ac39c8361
            http = httplib2.Http()
            self.auth.refresh(http)

        self.session.add_header('Authorization', "Bearer " + self.auth.access_token)
=======
<<<<<<< 46798d67c38d2cf8e1c751b684897cdc98598205
=======
        warnings.warn("""
            ClientLogin is deprecated:
            https://developers.google.com/identity/protocols/AuthForInstalledApps?csw=1

            Authorization with email and password will stop working on April 20, 2015.

            Please use oAuth2 authorization instead:
            http://gspread.readthedocs.org/en/latest/oauth2.html

        """, Warning)

        """Authorize client using ClientLogin protocol.

        The credentials provided in `auth` parameter to class' constructor will be used.

        This method is using API described at:
        http://code.google.com/apis/accounts/docs/AuthForInstalledApps.html

        :raises AuthenticationError: if login attempt fails.

        """
        source = 'burnash-gspread-%s' % __version__
        service = 'wise'

>>>>>>> Update README.md
        if hasattr(self.auth, 'access_token'):
            if not self.auth.access_token or \
                    (hasattr(self.auth, 'access_token_expired') and self.auth.access_token_expired):
                import httplib2
<<<<<<< HEAD

                http = httplib2.Http()
                self.auth.refresh(http)

            self.session.add_header('Authorization', "Bearer " + self.auth.access_token)

        else:
            self._deprecation_warning()

=======
                
                http = httplib2.Http()
                self.auth.refresh(http)
                
            self.session.add_header('Authorization', "Bearer " + self.auth.access_token)
            
        else:
>>>>>>> # This is a combination of 2 commits.
            data = {'Email': self.auth[0],
                    'Passwd': self.auth[1],
                    'accountType': 'HOSTED_OR_GOOGLE',
                    'service': service,
                    'source': source}
<<<<<<< HEAD

            url = AUTH_SERVER + '/accounts/ClientLogin'

            try:
                r = self.session.post(url, data)
<<<<<<< 46798d67c38d2cf8e1c751b684897cdc98598205
                content = r.read().decode()
                token = self._get_auth_token(content)
=======
                token = self._get_auth_token(r.content)
>>>>>>> Update README.md
                auth_header = "GoogleLogin auth=%s" % token
                self.session.add_header('Authorization', auth_header)

            except HTTPError as ex:
                if ex.message.strip() == '403: Error=BadAuthentication':
                    raise AuthenticationError("Incorrect username or password")
                else:
                    raise AuthenticationError(
                        "Unable to authenticate. %s" % ex.message)
<<<<<<< 46798d67c38d2cf8e1c751b684897cdc98598205
<<<<<<< 95d918ab8c3e881f4363e5f5a50e98f79c768ddf
=======
=======
>>>>>>> Update README.md
=======
    
            url = AUTH_SERVER + '/accounts/ClientLogin'
    
            try:
                r = self.session.post(url, data)
                content = r.read().decode()
                token = self._get_auth_token(content)
                auth_header = "GoogleLogin auth=%s" % token
                self.session.add_header('Authorization', auth_header)
    
            except HTTPError as ex:
                if ex.code == 403:
                    content = ex.read().decode()
                    if content.strip() == 'Error=BadAuthentication':
                        raise AuthenticationError("Incorrect username or password")
                    else:
                        raise AuthenticationError(
                            "Unable to authenticate. %s code" % ex.code)
    
                else:
                    raise AuthenticationError(
                        "Unable to authenticate. %s code" % ex.code)
>>>>>>> # This is a combination of 2 commits.
<<<<<<< 46798d67c38d2cf8e1c751b684897cdc98598205
>>>>>>> # This is a combination of 2 commits.
=======
>>>>>>> Update README.md
>>>>>>> Update README.md

    def open(self, title):
        """Opens a spreadsheet.

        :param title: A title of a spreadsheet.

        :returns: a :class:`~gspread.Spreadsheet` instance.

        If there's more than one spreadsheet with same title the first one
        will be opened.

        :raises gspread.SpreadsheetNotFound: if no spreadsheet with
                                             specified `title` is found.

        >>> c = gspread.authorize(credentials)
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
        """Opens a spreadsheet specified by `key`.

        :param key: A key of a spreadsheet as it appears in a URL in a browser.

        :returns: a :class:`~gspread.Spreadsheet` instance.

        :raises gspread.SpreadsheetNotFound: if no spreadsheet with
                                             specified `key` is found.

        >>> c = gspread.authorize(credentials)
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
        """Opens a spreadsheet specified by `url`.

        :param url: URL of a spreadsheet as it appears in a browser.

        :returns: a :class:`~gspread.Spreadsheet` instance.

        :raises gspread.SpreadsheetNotFound: if no spreadsheet with
                                             specified `url` is found.

        >>> c = gspread.authorize(credentials)
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
        """Opens all available spreadsheets.

        :param title: (optional) If specified can be used to filter
                      spreadsheets by title.

        :returns: a list of :class:`~gspread.Spreadsheet` instances.

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
        return ElementTree.fromstring(r.content)

    def get_worksheets_feed(self, spreadsheet,
                            visibility='private', projection='full'):
        url = construct_url('worksheets', spreadsheet,
                            visibility=visibility, projection=projection)

        r = self.session.get(url)
        return ElementTree.fromstring(r.content)

    def get_cells_feed(self, worksheet,
                       visibility='private', projection='full', params=None):

        url = construct_url('cells', worksheet,
                            visibility=visibility, projection=projection)

        if params:
            params = urlencode(params)
            url = '%s?%s' % (url, params)

        r = self.session.get(url)
        return ElementTree.fromstring(r.content)

    def get_feed(self, url):
        r = self.session.get(url)
        return ElementTree.fromstring(r.content)

    def del_worksheet(self, worksheet):
        url = construct_url(
            'worksheet', worksheet, 'private', 'full', worksheet_version=worksheet.version)
<<<<<<< 46798d67c38d2cf8e1c751b684897cdc98598205
        r = self.session.delete(url)
<<<<<<< 95d918ab8c3e881f4363e5f5a50e98f79c768ddf
=======
<<<<<<< HEAD
=======
>>>>>>> # This is a combination of 2 commits.
=======
<<<<<<< HEAD
        self.session.delete(url)
=======
        r = self.session.delete(url)
<<<<<<< HEAD
=======
>>>>>>> Update README.md
        # Even though there is nothing interesting in the response body
        # we have to read it or the next request from this session will get a
        # httplib.ResponseNotReady error.
        r.read()
<<<<<<< 46798d67c38d2cf8e1c751b684897cdc98598205
<<<<<<< 95d918ab8c3e881f4363e5f5a50e98f79c768ddf
=======
>>>>>>> # This is a combination of 2 commits.
>>>>>>> # This is a combination of 2 commits.
=======
>>>>>>> # This is a combination of 2 commits.
>>>>>>> Update README.md
>>>>>>> Update README.md

    def get_cells_cell_id_feed(self, worksheet, cell_id,
                               visibility='private', projection='full'):
        url = construct_url('cells_cell_id', worksheet, cell_id=cell_id,
                            visibility=visibility, projection=projection)

        r = self.session.get(url)
        return ElementTree.fromstring(r.content)

    def put_feed(self, url, data):
        headers = {'Content-Type': 'application/atom+xml',
                   'If-Match': '*'}
<<<<<<< HEAD
<<<<<<< 46798d67c38d2cf8e1c751b684897cdc98598205
=======
        data = self._ensure_xml_header(data)
=======
<<<<<<< HEAD
>>>>>>> Update README.md
        data = self._ensure_xml_header(data)
=======
        data = self._add_xml_header(data)
>>>>>>> # This is a combination of 2 commits.
<<<<<<< 46798d67c38d2cf8e1c751b684897cdc98598205
=======
>>>>>>> Update README.md
>>>>>>> Update README.md

        try:
            r = self.session.put(url, data, headers=headers)
        except HTTPError as ex:
<<<<<<< 46798d67c38d2cf8e1c751b684897cdc98598205
<<<<<<< 95d918ab8c3e881f4363e5f5a50e98f79c768ddf
<<<<<<< 0f67973a7427fb0d14703e22f8f1308f0dfd6af5
            if getattr(ex, 'code', None) == 403:
=======
            if ex.code == 403:
<<<<<<< 7e91ce60c91237a29536f0b2f609ab27a82d3d68
>>>>>>> Squashing all the commits to simpy things for merge
=======
=======
<<<<<<< HEAD
            if getattr(ex, 'code', None) == 403:
=======
            if ex.code == 403:
>>>>>>> # This is a combination of 2 commits.
>>>>>>> # This is a combination of 2 commits.
=======
<<<<<<< HEAD
            if getattr(ex, 'code', None) == 403:
=======
<<<<<<< HEAD
            if getattr(ex, 'code', None) == 403:
=======
            if ex.code == 403:
>>>>>>> # This is a combination of 2 commits.
>>>>>>> Update README.md
>>>>>>> Update README.md
                raise UpdateCellError(ex.message)
            else:
                raise

        return ElementTree.fromstring(r.content)

    def post_feed(self, url, data):
        headers = {'Content-Type': 'application/atom+xml'}
        data = self._ensure_xml_header(data)

        try:
            r = self.session.post(url, data, headers=headers)
        except HTTPError as ex:
            raise RequestError(ex.message)

        return ElementTree.fromstring(r.content)

    def post_cells(self, worksheet, data):
        headers = {'Content-Type': 'application/atom+xml',
                   'If-Match': '*'}
<<<<<<< HEAD
        data = self._ensure_xml_header(data)
=======
<<<<<<< 46798d67c38d2cf8e1c751b684897cdc98598205
        data = self._add_xml_header(data)
>>>>>>> # This is a combination of 2 commits.
=======
<<<<<<< HEAD
        data = self._ensure_xml_header(data)
=======
        data = self._add_xml_header(data)
>>>>>>> # This is a combination of 2 commits.
>>>>>>> Update README.md
>>>>>>> Update README.md
        url = construct_url('cells_batch', worksheet)
        r = self.session.post(url, data, headers=headers)

        return ElementTree.fromstring(r.content)
<<<<<<< HEAD

=======

    def create(self, title):
        """Creates a new spreadsheet.

        :param title: A title of a new spreadsheet.

<<<<<<< a69cd84f789e21aa91b9c488abd3dc4ac39c8361
        :returns: a :class:`~gspread.Spreadsheet` instance.
=======
    This is a shortcut function which instantiates :class:`Client`
    and performs login right away.
>>>>>>> # This is a combination of 2 commits.

        .. note::

           In order to use this method, you need to add
           ``https://www.googleapis.com/auth/drive`` to your oAuth scope.

           Example::

              scope = [
                  'https://spreadsheets.google.com/feeds',
                  'https://www.googleapis.com/auth/drive'
              ]

           Otherwise you will get an ``Insufficient Permission`` error
           when you try to create a new spreadsheet.

        """

        create_url = 'https://www.googleapis.com/drive/v2/files'
        headers = {'Content-Type': 'application/json'}
        data = {
            'title': title,
            'mimeType': 'application/vnd.google-apps.spreadsheet'
        }
        r = self.session.post(create_url, json.dumps(data), headers=headers)
        spreadsheet_id = r.json()['id']
        return self.open_by_key(spreadsheet_id)


def authorize(credentials):
    """Login to Google API using OAuth2 credentials.
    This is a shortcut function which instantiates :class:`Client`
    and performs login right away.
    :returns: :class:`Client` instance.
    """
    client = Client(auth=credentials)
    client.login()
    return client
<<<<<<< HEAD

<<<<<<< 46798d67c38d2cf8e1c751b684897cdc98598205
=======
def login(email, password):
    """Login to Google API using `email` and `password`.

    This is a shortcut function which instantiates :class:`Client`
    and performs login right away.

    :returns: :class:`Client` instance.

    """
    client = Client(auth=(email, password))
    client.login()
    return client
<<<<<<< HEAD
>>>>>>> Update README.md

>>>>>>> Update README.md
=======
    
>>>>>>> # This is a combination of 2 commits.
def authorize(credentials):
    """Login to Google API using OAuth2 credentials.

    This is a shortcut function which instantiates :class:`Client`
    and performs login right away.

    :returns: :class:`Client` instance.

    """
    client = Client(auth=credentials)
    client.login()
    return client
<<<<<<< HEAD
<<<<<<< 46798d67c38d2cf8e1c751b684897cdc98598205
<<<<<<< 95d918ab8c3e881f4363e5f5a50e98f79c768ddf
<<<<<<< HEAD
<<<<<<< HEAD
    
=======

>>>>>>> 109de9d... added worksheet export #12
=======
>>>>>>> 120bad7... Squashing all the commits to simpy things for merge
=======
>>>>>>> d078bae... Fix bug:
=======
=======
    
>>>>>>> # This is a combination of 2 commits.
>>>>>>> # This is a combination of 2 commits.
=======
=======
<<<<<<< HEAD
=======
    
>>>>>>> # This is a combination of 2 commits.
>>>>>>> Update README.md
>>>>>>> Update README.md
