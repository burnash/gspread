# -*- coding: utf-8 -*-

"""
gspread.client
~~~~~~~~~~~~~~

This module contains Client class responsible for communicating with
Google API.

"""

import requests

from .utils import finditem
from .utils import extract_id_from_url

from .exceptions import SpreadsheetNotFound
from .exceptions import APIError
from .models import Spreadsheet

from .urls import (
    DRIVE_FILES_API_V2_URL,
    DRIVE_FILES_UPLOAD_API_V2_URL
)


class Client(object):
    """An instance of this class communicates with Google API.

    :param auth: An OAuth2 credential object. Credential objects
                 are those created by the oauth2client library.
                 https://github.com/google/oauth2client
    :param session: (optional) A session object capable of making HTTP requests
                    while persisting some parameters across requests.
                    Defaults to `requests.Session <http://docs.python-requests.org/en/master/api/#request-sessions>`_.

    >>> c = gspread.Client(auth=OAuthCredentialObject)

    """
    def __init__(self, auth, session=None):
        self.auth = auth
        self.session = session or requests.Session()

    def login(self):
        """Authorize client."""
        if not self.auth.access_token or \
                (hasattr(self.auth, 'access_token_expired') and self.auth.access_token_expired):
            import httplib2

            http = httplib2.Http()
            self.auth.refresh(http)

        self.session.headers.update({
            'Authorization': 'Bearer %s' % self.auth.access_token
        })

    def request(
            self,
            method,
            endpoint,
            params=None,
            data=None,
            json=None,
            files=None,
            headers=None):

        response = getattr(self.session, method)(
            endpoint,
            json=json,
            params=params,
            data=data,
            files=files,
            headers=headers
        )

        if response.ok:
            return response
        else:
            raise APIError(response)

    def list_spreadsheet_files(self):
        files = []
        page_token = ''
        url = "https://www.googleapis.com/drive/v3/files"
        params = {
            'q': "mimeType='application/vnd.google-apps.spreadsheet'",
            "pageSize": 1000,
            'supportsTeamDrives': True,
            'includeTeamDriveItems': True,
        }

        while page_token is not None:
            if page_token:
                params['pageToken'] = page_token

            res = self.request('get', url, params=params).json()
            files.extend(res['files'])
            page_token = res.get('nextPageToken', None)

        return files

    def open(self, title):
        """Opens a spreadsheet.

        :param title: A title of a spreadsheet.

        :returns: a :class:`~gspread.models.Spreadsheet` instance.

        If there's more than one spreadsheet with same title the first one
        will be opened.

        :raises gspread.SpreadsheetNotFound: if no spreadsheet with
                                             specified `title` is found.

        >>> c = gspread.authorize(credentials)
        >>> c.open('My fancy spreadsheet')

        """
        try:
            properties = finditem(
                lambda x: x['name'] == title,
                self.list_spreadsheet_files()
            )

            # Drive uses different terminology
            properties['title'] = properties['name']

            return Spreadsheet(self, properties)
        except StopIteration:
            raise SpreadsheetNotFound

    def open_by_key(self, key):
        """Opens a spreadsheet specified by `key`.

        :param key: A key of a spreadsheet as it appears in a URL in a browser.

        :returns: a :class:`~gspread.models.Spreadsheet` instance.

        >>> c = gspread.authorize(credentials)
        >>> c.open_by_key('0BmgG6nO_6dprdS1MN3d3MkdPa142WFRrdnRRUWl1UFE')

        """
        return Spreadsheet(self, {'id': key})

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

        :returns: a list of :class:`~gspread.models.Spreadsheet` instances.

        """
        spreadsheet_files = self.list_spreadsheet_files()

        return [
            Spreadsheet(self, dict(title=x['name'], **x))
            for x in spreadsheet_files
        ]

    def create(self, title):
        """Creates a new spreadsheet.

        :param title: A title of a new spreadsheet.

        :returns: a :class:`~gspread.models.Spreadsheet` instance.

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
        payload = {
            'title': title,
            'mimeType': 'application/vnd.google-apps.spreadsheet'
        }
        r = self.request(
            'post',
            DRIVE_FILES_API_V2_URL,
            json=payload
        )
        spreadsheet_id = r.json()['id']
        return self.open_by_key(spreadsheet_id)

    def del_spreadsheet(self, file_id):
        """Deletes a spreadsheet.

        :param file_id: a spreadsheet ID (aka file ID.)
        """
        url = '{0}/{1}'.format(
            DRIVE_FILES_API_V2_URL,
            file_id
        )

        self.request('delete', url)

    def import_csv(self, file_id, data):
        """Imports data into the first page of the spreadsheet.

        :param data: A CSV string of data.
        """
        headers = {'Content-Type': 'text/csv'}
        url = '{0}/{1}'.format(DRIVE_FILES_UPLOAD_API_V2_URL, file_id)

        self.request(
            'put',
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

        r = self.request('get', url)

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

        payload = {
            'value': value,
            'type': perm_type,
            'role': role,
        }

        params = {
            'sendNotificationEmails': notify,
            'emailMessage': email_message
        }

        self.request(
            'post',
            url,
            json=payload,
            params=params
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

        self.request('delete', url)
