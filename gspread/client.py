# -*- coding: utf-8 -*-

"""
gspread.client
~~~~~~~~~~~~~~

This module contains Client class responsible for communicating with
Google API.

"""

from google.auth.transport.requests import AuthorizedSession

from .exceptions import APIError, SpreadsheetNotFound
from .models import Spreadsheet
from .utils import convert_credentials, extract_id_from_url, finditem

from .urls import (
    DRIVE_FILES_API_V2_URL,
    DRIVE_FILES_API_V3_URL,
    DRIVE_FILES_UPLOAD_API_V2_URL,
)


class Client(object):
    """An instance of this class communicates with Google API.

    :param auth: An OAuth2 credential object. Credential objects
        created by `google-auth <https://github.com/googleapis/google-auth-library-python>`_.

    :param session: (optional) A session object capable of making HTTP requests
        while persisting some parameters across requests.
        Defaults to `google.auth.transport.requests.AuthorizedSession <https://google-auth.readthedocs.io/en/latest/reference/google.auth.transport.requests.html#google.auth.transport.requests.AuthorizedSession>`_.

    >>> c = gspread.Client(auth=OAuthCredentialObject)
    """

    def __init__(self, auth, session=None):
        if auth is not None:
            self.auth = convert_credentials(auth)
            self.session = session or AuthorizedSession(self.auth)
        else:
            self.session = session

    def login(self):
        from google.auth.transport.requests import Request

        self.auth.refresh(Request(self.session))

        self.session.headers.update(
            {'Authorization': 'Bearer %s' % self.auth.token}
        )

    def request(
        self,
        method,
        endpoint,
        params=None,
        data=None,
        json=None,
        files=None,
        headers=None,
    ):
        response = getattr(self.session, method)(
            endpoint,
            json=json,
            params=params,
            data=data,
            files=files,
            headers=headers,
        )

        if response.ok:
            return response
        else:
            raise APIError(response)

    def list_spreadsheet_files(self, title=None):
        files = []
        page_token = ''
        url = DRIVE_FILES_API_V3_URL

        q = 'mimeType="application/vnd.google-apps.spreadsheet"'
        if title:
            q += ' and name = "{}"'.format(title)

        params = {
            'q': q,
            'pageSize': 1000,
            'supportsAllDrives': True,
            'includeItemsFromAllDrives': True,
            'fields': 'kind,nextPageToken,files(id,name,createdTime,modifiedTime)',
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

        :param str title: A title of a spreadsheet.
        :returns: a :class:`~gspread.models.Spreadsheet` instance.

        If there's more than one spreadsheet with same title the first one
        will be opened.

        :raises gspread.SpreadsheetNotFound: if no spreadsheet with
                                             specified `title` is found.

        >>> gc.open('My fancy spreadsheet')
        """
        try:
            properties = finditem(
                lambda x: x['name'] == title,
                self.list_spreadsheet_files(title),
            )

            # Drive uses different terminology
            properties['title'] = properties['name']

            return Spreadsheet(self, properties)
        except StopIteration:
            raise SpreadsheetNotFound

    def open_by_key(self, key):
        """Opens a spreadsheet specified by `key` (a.k.a Spreadsheet ID).

        :param str key: A key of a spreadsheet as it appears in a URL in a browser.
        :returns: a :class:`~gspread.models.Spreadsheet` instance.

        >>> gc.open_by_key('0BmgG6nO_6dprdS1MN3d3MkdPa142WFRrdnRRUWl1UFE')
        """
        return Spreadsheet(self, {'id': key})

    def open_by_url(self, url):
        """Opens a spreadsheet specified by `url`.

        :param str url: URL of a spreadsheet as it appears in a browser.

        :returns: a :class:`~gspread.models.Spreadsheet` instance.

        :raises gspread.SpreadsheetNotFound: if no spreadsheet with
                                             specified `url` is found.

        >>> gc.open_by_url('https://docs.google.com/spreadsheet/ccc?key=0Bm...FE&hl')
        """
        return self.open_by_key(extract_id_from_url(url))

    def openall(self, title=None):
        """Opens all available spreadsheets.

        :param str title: (optional) If specified can be used to filter
            spreadsheets by title.

        :returns: a list of :class:`~gspread.models.Spreadsheet` instances.
        """
        spreadsheet_files = self.list_spreadsheet_files(title)

        if title:
            spreadsheet_files = [
                spread
                for spread in spreadsheet_files
                if title == spread["name"]
            ]

        return [
            Spreadsheet(self, dict(title=x['name'], **x))
            for x in spreadsheet_files
        ]

    def create(self, title, folder_id=None):
        """Creates a new spreadsheet.

        :param str title: A title of a new spreadsheet.

        :param str folder_id: Id of the folder where we want to save
            the spreadsheet.

        :returns: a :class:`~gspread.models.Spreadsheet` instance.

        """
        payload = {
            'name': title,
            'mimeType': 'application/vnd.google-apps.spreadsheet',
        }

        params = {
            "supportsAllDrives": True,
        }

        if folder_id is not None:
            payload['parents'] = [folder_id]

        r = self.request('post', DRIVE_FILES_API_V3_URL, json=payload, params=params)
        spreadsheet_id = r.json()['id']
        return self.open_by_key(spreadsheet_id)

    def copy(self, file_id, title=None, copy_permissions=False, folder_id=None):
        """Copies a spreadsheet.

        :param str file_id: A key of a spreadsheet to copy.
        :param str title: (optional) A title for the new spreadsheet.

        :param bool copy_permissions: (optional) If True, copy permissions from
            the original spreadsheet to the new spreadsheet.

        :param str folder_id: Id of the folder where we want to save
            the spreadsheet.

        :returns: a :class:`~gspread.models.Spreadsheet` instance.

        .. versionadded:: 3.1.0

        .. note::

           If you're using custom credentials without the Drive scope, you need to add 
           ``https://www.googleapis.com/auth/drive`` to your OAuth scope in order to use 
           this method.

           Example::

              scope = [
                  'https://www.googleapis.com/auth/spreadsheets',
                  'https://www.googleapis.com/auth/drive'
              ]

           Otherwise, you will get an ``Insufficient Permission`` error
           when you try to copy a spreadsheet.

        """
        url = '{0}/{1}/copy'.format(DRIVE_FILES_API_V2_URL, file_id)

        payload = {
            'title': title,
            'mimeType': 'application/vnd.google-apps.spreadsheet',
        }

        if folder_id is not None:
            payload['parents'] = [{'id': folder_id}]
        
        params = {'supportsAllDrives': True}
        r = self.request('post', url, json=payload, params=params)
        spreadsheet_id = r.json()['id']

        new_spreadsheet = self.open_by_key(spreadsheet_id)

        if copy_permissions is True:
            original = self.open_by_key(file_id)

            permissions = original.list_permissions()
            for p in permissions:
                if p.get('deleted'):
                    continue
                try:
                    new_spreadsheet.share(
                        value=p['emailAddress'],
                        perm_type=p['type'],
                        role=p['role'],
                        notify=False,
                    )
                except Exception:
                    pass

        return new_spreadsheet

    def del_spreadsheet(self, file_id):
        """Deletes a spreadsheet.

        :param str file_id: a spreadsheet ID (a.k.a file ID).
        """
        url = '{0}/{1}'.format(DRIVE_FILES_API_V3_URL, file_id)

        params = {'supportsAllDrives': True}
        self.request('delete', url, params=params)

    def import_csv(self, file_id, data):
        """Imports data into the first page of the spreadsheet.

        :param str data: A CSV string of data.

        Example:

        .. code::

            # Read CSV file contents
            content = open('file_to_import.csv', 'r').read()

            gc.import_csv(spreadsheet.id, content)

        .. note::

           This method removes all other worksheets and then entirely
           replaces the contents of the first worksheet.

        """
        headers = {'Content-Type': 'text/csv'}
        url = '{0}/{1}'.format(DRIVE_FILES_UPLOAD_API_V2_URL, file_id)

        self.request(
            'put',
            url,
            data=data,
            params={
                'uploadType': 'media',
                'convert': True,
                'supportsAllDrives': True,
            },
            headers=headers,
        )

    def list_permissions(self, file_id):
        """Retrieve a list of permissions for a file.

        :param str file_id: a spreadsheet ID (aka file ID).
        """
        url = '{0}/{1}/permissions'.format(DRIVE_FILES_API_V2_URL, file_id)

        params = {'supportsAllDrives': True}
        r = self.request('get', url, params=params)

        return r.json()['items']

    def insert_permission(
        self,
        file_id,
        value,
        perm_type,
        role,
        notify=True,
        email_message=None,
        with_link=False,
    ):
        """Creates a new permission for a file.

        :param str file_id: a spreadsheet ID (aka file ID).
        :param value: user or group e-mail address, domain name
            or None for 'default' type.
        :type value: str, None
        :param str perm_type: (optional) The account type.
            Allowed values are: ``user``, ``group``, ``domain``, ``anyone``
        :param str role: (optional) The primary role for this user.
            Allowed values are: ``owner``, ``writer``, ``reader``
        :param str notify: (optional) Whether to send an email to the target
            user/domain.
        :param str email_message: (optional) An email message to be sent
            if ``notify=True``.
        :param bool with_link: (optional) Whether the link is required for this
            permission to be active.

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
            'withLink': with_link,
        }

        params = {
            'sendNotificationEmails': notify,
            'emailMessage': email_message,
            'supportsAllDrives': 'true',
        }

        self.request('post', url, json=payload, params=params)

    def remove_permission(self, file_id, permission_id):
        """Deletes a permission from a file.

        :param str file_id: a spreadsheet ID (aka file ID.)
        :param str permission_id: an ID for the permission.
        """
        url = '{0}/{1}/permissions/{2}'.format(
            DRIVE_FILES_API_V2_URL, file_id, permission_id
        )

        params = {'supportsAllDrives': True}
        self.request('delete', url, params=params)
