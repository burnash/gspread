# -*- coding: utf-8 -*-

"""
gspread.client
~~~~~~~~~~~~~~

This module contains Client class responsible for communicating with
Google Data API.

"""
import json

try:
    import xml.etree.cElementTree as ElementTree
except:
    from xml.etree import ElementTree

from . import urlencode
from .ns import _ns
from .httpsession import HTTPSession
from .exceptions import RequestError
from .models import Spreadsheet
from .urls import (
    construct_url,
    DRIVE_FILES_API_V2_URL,
    DRIVE_FILES_UPLOAD_API_V2_URL
)
from .utils import finditem, extract_id_from_url, is_public_url
from .exceptions import (SpreadsheetNotFound, UpdateCellError)


class Client(object):

    """An instance of this class communicates with Google Data API.

    :param auth: An OAuth2 credential object. Credential objects are those created by the
                 oauth2client library. https://github.com/google/oauth2client
                 To access public, published spreadsheets, set auth to None.  Be careful,
                 it is insufficient for the spreadsheet to simply be public, it must
                 also be published (in the sense of File->Publish to the web->Entire Document->Publish)
    :param http_session: (optional) A session object capable of making HTTP requests while persisting headers.
                                    Defaults to :class:`~gspread.httpsession.HTTPSession`.

    >>> c = gspread.Client(auth=OAuthCredentialObject)

    """
    def __init__(self, auth, http_session=None):
        self.auth = auth
        self.session = http_session or HTTPSession()

    def _ensure_xml_header(self, data):
        if data.startswith(b'<?xml'):
            return data
        else:
            return b'<?xml version="1.0" encoding="utf8"?>' + data

    def login(self):
        """Authorize client."""
        if not self.auth.access_token or \
                (hasattr(self.auth, 'access_token_expired') and self.auth.access_token_expired):
            import httplib2

            http = httplib2.Http()
            self.auth.refresh(http)

        self.session.add_header('Authorization', "Bearer " + self.auth.access_token)

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
        feed = self.get_spreadsheets_feed(hint=key)
        for elem in feed.findall(_ns('entry')):
            alter_link = finditem(lambda x: x.get('rel') == 'alternate',
                                  elem.findall(_ns('link')))
            spreadsheet_id = extract_id_from_url(alter_link.get('href'))
            if spreadsheet_id == key:
                return Spreadsheet(self, elem)

            if is_public_url(alter_link.get('href')):
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
        return self.open_by_key(extract_id_from_url(url))

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

        if self.auth is None:
            raise SpreadsheetNotFound

        return result

    def get_spreadsheets_feed(self, visibility='private', projection='full', hint=None):
        if not self.auth:
            # If we have a spreadsheet key, we can try public route
            if not hint:
                # No joy, back out
                return ElementTree.Element('feed')
            url = construct_url('worksheets', spreadsheet_id=hint,
                                visibility='public', projection='full')
            r = self.session.get(url)
            # Construct a single-entry feed in the expected format
            feed = ElementTree.Element('feed')
            try:
                entry = ElementTree.Element(_ns('entry'))
                for elem in ElementTree.fromstring(r.content):
                    entry.append(elem)
                feed.append(entry)
            except ElementTree.ParseError:
                # we get a html error page if sheet is public-but-not-published
                return ElementTree.Element('feed')
            return feed

        url = construct_url('spreadsheets',
                            visibility=visibility, projection=projection)

        r = self.session.get(url)
        return ElementTree.fromstring(r.content)

    def get_worksheets_feed(self, spreadsheet,
                            visibility='private', projection='full'):
        if not self.auth:
            # fall back to public
            visibility = 'public'
        url = construct_url('worksheets', spreadsheet,
                            visibility=visibility, projection=projection)

        r = self.session.get(url)
        return ElementTree.fromstring(r.content)

    def get_cells_feed(self, worksheet,
                       visibility='private', projection='full', params=None):

        if not self.auth:
            # fall back to public
            visibility = 'public'
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

    def del_spreadsheet(self, file_id):
        """Deletes a spreadsheet.

        :param file_id: a spreadsheet ID (aka file ID.)
        """
        url = '{0}/{1}'.format(
            DRIVE_FILES_API_V2_URL,
            file_id
        )

        self.session.delete(url)

    def del_worksheet(self, worksheet):
        url = construct_url(
            'worksheet',
            worksheet,
            'private',
            'full',
            worksheet_version=worksheet.version
        )
        self.session.delete(url)

    def get_cells_cell_id_feed(self, worksheet, cell_id,
                               visibility='private', projection='full'):
        url = construct_url('cells_cell_id', worksheet, cell_id=cell_id,
                            visibility=visibility, projection=projection)

        r = self.session.get(url)
        return ElementTree.fromstring(r.content)

    def put_feed(self, url, data):
        headers = {'Content-Type': 'application/atom+xml',
                   'If-Match': '*'}
        data = self._ensure_xml_header(data)

        try:
            r = self.session.put(url, data, headers=headers)
        except RequestError as ex:
            if ex[0] == 403:
                raise UpdateCellError(ex[1])
            else:
                raise

        return ElementTree.fromstring(r.content)

    def post_feed(self, url, data):
        headers = {'Content-Type': 'application/atom+xml'}
        data = self._ensure_xml_header(data)

        r = self.session.post(url, data, headers=headers)

        return ElementTree.fromstring(r.content)

    def post_cells(self, worksheet, data):
        headers = {'Content-Type': 'application/atom+xml',
                   'If-Match': '*'}
        data = self._ensure_xml_header(data)
        url = construct_url('cells_batch', worksheet)
        r = self.session.post(url, data, headers=headers)

        return ElementTree.fromstring(r.content)

    def create(self, title):
        """Creates a new spreadsheet.

        :param title: A title of a new spreadsheet.

        :returns: a :class:`~gspread.Spreadsheet` instance.

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

        headers = {'Content-Type': 'application/json'}
        data = {
            'title': title,
            'mimeType': 'application/vnd.google-apps.spreadsheet'
        }
        r = self.session.post(
            DRIVE_FILES_API_V2_URL,
            json.dumps(data),
            headers=headers
        )
        spreadsheet_id = r.json()['id']
        return self.open_by_key(spreadsheet_id)

    def import_csv(self, file_id, data):
        """Imports data into the first page of the spreadsheet.

        :param data: A CSV string of data.
        """
        headers = {'Content-Type': 'text/csv'}
        url = '{0}/{1}'.format(DRIVE_FILES_UPLOAD_API_V2_URL, file_id)

        self.session.put(
            url,
            data=data,
            params={
                'uploadType': 'media',
                'convert': True
            },
            headers=headers
        )

    def list_permissions(self, file_id):
        """Retrieve a list of permissions for a file.

        :param file_id: a spreadsheet ID (aka file ID.)
        """
        url = '{0}/{1}/permissions'.format(DRIVE_FILES_API_V2_URL, file_id)
        headers = {'Content-Type': 'application/json'}

        r = self.session.get(url, headers=headers)

        return r.json()['items']

    def insert_permission(
        self,
        file_id,
        value,
        perm_type,
        role,
        notify=True,
        email_message=None
    ):
        """Creates a new permission for a file.

        :param file_id: a spreadsheet ID (aka file ID.)
        :param value: user or group e-mail address, domain name
                      or None for 'default' type.
        :param perm_type: the account type.
               Allowed values are: ``user``, ``group``, ``domain``,
               ``anyone``
        :param role: the primary role for this user.
               Allowed values are: ``owner``, ``writer``, ``reader``

        :param notify: Whether to send an email to the target user/domain.
        :param email_message: an email message to be sent if notify=True.

        Examples::

            # Give write permissions to otto@example.com

            gc.insert_permission(
                '0BmgG6nO_6dprnRRUWl1UFE',
                'otto@example.org',
                perm_type='user',
                role='writer'
            )

            # Make the spreadsheet publicly readable

            gc.insert_permission(
                '0BmgG6nO_6dprnRRUWl1UFE',
                None,
                perm_type='anyone',
                role='reader'
            )

        """

        url = '{0}/{1}/permissions'.format(DRIVE_FILES_API_V2_URL, file_id)

        data = {
            'value': value,
            'type': perm_type,
            'role': role,
        }

        params = {
            'sendNotificationEmails': notify,
            'emailMessage': email_message
        }

        headers = {'Content-Type': 'application/json'}

        self.session.post(
            url,
            json.dumps(data),
            params=params,
            headers=headers
        )

    def remove_permission(self, file_id, permission_id):
        """Deletes a permission from a file.

        :param file_id: a spreadsheet ID (aka file ID.)
        :param permission_id: an ID for the permission.
        """
        url = '{0}/{1}/permissions/{2}'.format(
            DRIVE_FILES_API_V2_URL,
            file_id,
            permission_id
        )
        headers = {'Content-Type': 'application/json'}

        self.session.delete(url, headers=headers)


def authorize(credentials):
    """Login to Google API using OAuth2 credentials.
    This is a shortcut function which instantiates :class:`Client`
    and performs login right away.
    :returns: :class:`Client` instance.
    """
    client = Client(auth=credentials)
    client.login()
    return client


def public():
    """Prepare to access public, published spreadsheets.

    No private spreadsheets will be accessible , for that you
    need to authorize or login instead.

    :returns: :class:`Client` instance.

    """
    return Client(auth=None)
