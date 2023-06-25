"""
gspread.client
~~~~~~~~~~~~~~

This module contains Client class responsible for managing spreadsheet files

"""

from typing import Any, Dict, List, Optional, Union

from google.auth.credentials import Credentials
from requests import Response

from .exceptions import SpreadsheetNotFound, UnSupportedExportFormat
from .http_client import HTTPClient, HTTPClientType, ParamsType
from .spreadsheet import Spreadsheet
from .urls import (
    DRIVE_FILES_API_V3_COMMENTS_URL,
    DRIVE_FILES_API_V3_URL,
    DRIVE_FILES_UPLOAD_API_V2_URL,
)
from .utils import ExportFormat, MimeType, extract_id_from_url, finditem


class Client:
    """An instance of this class Manages Spreadsheet files

    It is used to:
        - open/create/list/delete spreadsheets
        - create/delete/list spreadsheet permission
        - etc

    It is the gspread entry point.
    It will handle creating necessary :class:`~gspread.models.Spreadsheet` instances.
    """

    def __init__(
        self, auth: Credentials, http_client: HTTPClientType = HTTPClient
    ) -> None:
        self.http_client = http_client(auth)

    def list_spreadsheet_files(
        self, title: Optional[str] = None, folder_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """List all the spreadsheet files

        Will list all spreadsheet files owned by/shared with this user account.

        :param str title: Filter only spreadsheet files with this title
        :param str folder_id: Only look for spreadsheet files in this folder
            The parameter ``folder_id`` can be obtained from the URL when looking at
            a folder in a web browser as follow:
            ``https://drive.google.com/drive/u/0/folders/<folder_id>``
        """
        files = []
        page_token = ""
        url = DRIVE_FILES_API_V3_URL

        q = 'mimeType="{}"'.format(MimeType.google_sheets)
        if title:
            q += ' and name = "{}"'.format(title)
        if folder_id:
            q += ' and parents in "{}"'.format(folder_id)

        params: ParamsType = {
            "q": q,
            "pageSize": 1000,
            "supportsAllDrives": True,
            "includeItemsFromAllDrives": True,
            "fields": "kind,nextPageToken,files(id,name,createdTime,modifiedTime)",
        }

        while page_token is not None:
            if page_token:
                params["pageToken"] = page_token

            res = self.http_client.request("get", url, params=params).json()
            files.extend(res["files"])
            page_token = res.get("nextPageToken", None)

        return files

    def open(self, title: str, folder_id: Optional[str] = None) -> Spreadsheet:
        """Opens a spreadsheet.

        :param str title: A title of a spreadsheet.
        :param str folder_id: (optional) If specified can be used to filter
            spreadsheets by parent folder ID.
        :returns: a :class:`~gspread.models.Spreadsheet` instance.

        If there's more than one spreadsheet with same title the first one
        will be opened.

        :raises gspread.SpreadsheetNotFound: if no spreadsheet with
                                             specified `title` is found.

        >>> gc.open('My fancy spreadsheet')
        """
        try:
            properties = finditem(
                lambda x: x["name"] == title,
                self.list_spreadsheet_files(title, folder_id),
            )

            # Drive uses different terminology
            properties["title"] = properties["name"]

            return Spreadsheet(self.http_client, properties)
        except StopIteration:
            raise SpreadsheetNotFound

    def open_by_key(self, key: str) -> Spreadsheet:
        """Opens a spreadsheet specified by `key` (a.k.a Spreadsheet ID).

        :param str key: A key of a spreadsheet as it appears in a URL in a browser.
        :returns: a :class:`~gspread.models.Spreadsheet` instance.

        >>> gc.open_by_key('0BmgG6nO_6dprdS1MN3d3MkdPa142WFRrdnRRUWl1UFE')
        """
        return Spreadsheet(self.http_client, {"id": key})

    def open_by_url(self, url: str) -> Spreadsheet:
        """Opens a spreadsheet specified by `url`.

        :param str url: URL of a spreadsheet as it appears in a browser.

        :returns: a :class:`~gspread.models.Spreadsheet` instance.

        :raises gspread.SpreadsheetNotFound: if no spreadsheet with
                                             specified `url` is found.

        >>> gc.open_by_url('https://docs.google.com/spreadsheet/ccc?key=0Bm...FE&hl')
        """
        return self.open_by_key(extract_id_from_url(url))

    def openall(self, title: Optional[str] = None) -> List[Spreadsheet]:
        """Opens all available spreadsheets.

        :param str title: (optional) If specified can be used to filter
            spreadsheets by title.

        :returns: a list of :class:`~gspread.models.Spreadsheet` instances.
        """
        spreadsheet_files = self.list_spreadsheet_files(title)

        if title:
            spreadsheet_files = [
                spread for spread in spreadsheet_files if title == spread["name"]
            ]

        return [
            Spreadsheet(self.http_client, dict(title=x["name"], **x))
            for x in spreadsheet_files
        ]

    def create(self, title: str, folder_id: Optional[str] = None) -> Spreadsheet:
        """Creates a new spreadsheet.

        :param str title: A title of a new spreadsheet.

        :param str folder_id: Id of the folder where we want to save
            the spreadsheet.

        :returns: a :class:`~gspread.models.Spreadsheet` instance.

        """
        payload = {
            "name": title,
            "mimeType": MimeType.google_sheets,
        }

        params: ParamsType = {
            "supportsAllDrives": True,
        }

        if folder_id is not None:
            payload["parents"] = [folder_id]

        r = self.http_client.request(
            "post", DRIVE_FILES_API_V3_URL, json=payload, params=params
        )
        spreadsheet_id = r.json()["id"]
        return self.open_by_key(spreadsheet_id)

    def export(self, file_id: str, format: str = ExportFormat.PDF) -> bytes:
        """Export the spreadsheet in the given format.

        :param str file_id: The key of the spreadsheet to export

        :param str format: The format of the resulting file.
            Possible values are:

                * ``ExportFormat.PDF``
                * ``ExportFormat.EXCEL``
                * ``ExportFormat.CSV``
                * ``ExportFormat.OPEN_OFFICE_SHEET``
                * ``ExportFormat.TSV``
                * ``ExportFormat.ZIPPED_HTML``

            See `ExportFormat`_ in the Drive API.

        :type format: :namedtuple:`~gspread.utils.ExportFormat`

        :returns bytes: The content of the exported file.

        .. _ExportFormat: https://developers.google.com/drive/api/guides/ref-export-formats
        """

        if format not in ExportFormat:
            raise UnSupportedExportFormat

        url = "{}/{}/export".format(DRIVE_FILES_API_V3_URL, file_id)

        params: ParamsType = {"mimeType": format}

        r = self.http_client.request("get", url, params=params)
        return r.content

    def copy(
        self,
        file_id: str,
        title: Optional[str] = None,
        copy_permissions: bool = False,
        folder_id: Optional[str] = None,
        copy_comments: bool = True,
    ) -> Spreadsheet:
        """Copies a spreadsheet.

        :param str file_id: A key of a spreadsheet to copy.
        :param str title: (optional) A title for the new spreadsheet.

        :param bool copy_permissions: (optional) If True, copy permissions from
            the original spreadsheet to the new spreadsheet.

        :param str folder_id: Id of the folder where we want to save
            the spreadsheet.

        :param bool copy_comments: (optional) If True, copy the comments from
            the original spreadsheet to the new spreadsheet.

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
        url = "{}/{}/copy".format(DRIVE_FILES_API_V3_URL, file_id)

        payload = {
            "name": title,
            "mimeType": MimeType.google_sheets,
        }

        if folder_id is not None:
            payload["parents"] = [folder_id]

        params: ParamsType = {"supportsAllDrives": True}
        r = self.http_client.request("post", url, json=payload, params=params)
        spreadsheet_id = r.json()["id"]

        new_spreadsheet = self.open_by_key(spreadsheet_id)

        if copy_permissions is True:
            original = self.open_by_key(file_id)

            permissions = original.list_permissions()
            for p in permissions:
                if p.get("deleted"):
                    continue

                new_spreadsheet.share(
                    email_address=p["emailAddress"],
                    perm_type=p["type"],
                    role=p["role"],
                    notify=False,
                )

        if copy_comments is True:
            source_url = DRIVE_FILES_API_V3_COMMENTS_URL % (file_id)
            page_token = ""
            comments = []
            params = {
                "fields": "comments/content,comments/anchor,nextPageToken",
                "includeDeleted": False,
                "pageSize": 100,  # API limit to maximum 100
            }

            while page_token is not None:
                params["pageToken"] = page_token
                res = self.http_client.request("get", source_url, params=params).json()

                comments.extend(res["comments"])
                page_token = res.get("nextPageToken", None)

            destination_url = DRIVE_FILES_API_V3_COMMENTS_URL % (new_spreadsheet.id)
            # requesting some fields in the response is mandatory from the API.
            # choose 'id' randomly out of all the fields, but no need to use it for now.
            params = {"fields": "id"}
            for comment in comments:
                self.http_client.request(
                    "post", destination_url, json=comment, params=params
                )

        return new_spreadsheet

    def del_spreadsheet(self, file_id: str) -> None:
        """Deletes a spreadsheet.

        :param str file_id: a spreadsheet ID (a.k.a file ID).
        """
        url = "{}/{}".format(DRIVE_FILES_API_V3_URL, file_id)

        params: ParamsType = {"supportsAllDrives": True}
        self.http_client.request("delete", url, params=params)

    def import_csv(self, file_id: str, data: Union[str, bytes]) -> None:
        """Imports data into the first page of the spreadsheet.

        :param str file_id:
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
        # Make sure we send utf-8
        if type(data) is str:
            payload = data.encode("utf-8")

        headers = {"Content-Type": "text/csv"}
        url = "{}/{}".format(DRIVE_FILES_UPLOAD_API_V2_URL, file_id)

        self.http_client.request(
            "put",
            url,
            data=bytes(payload),
            params={
                "uploadType": "media",
                "convert": True,
                "supportsAllDrives": True,
            },
            headers=headers,
        )

    def list_permissions(self, file_id: str) -> List[Dict[str, Union[str, bool]]]:
        """Retrieve a list of permissions for a file.

        :param str file_id: a spreadsheet ID (aka file ID).
        """
        url = "{}/{}/permissions".format(DRIVE_FILES_API_V3_URL, file_id)

        params: ParamsType = {
            "supportsAllDrives": True,
            "fields": "nextPageToken,permissions",
        }

        token = ""

        permissions = []

        while token is not None:
            if token:
                params["pageToken"] = token

            r = self.http_client.request("get", url, params=params).json()
            permissions.extend(r["permissions"])

            token = r.get("nextPageToken", None)

        return permissions

    def insert_permission(
        self,
        file_id: str,
        value: Optional[str],
        perm_type: Optional[str],
        role: Optional[str],
        notify: bool = True,
        email_message: Optional[str] = None,
        with_link: bool = False,
    ) -> Response:
        """Creates a new permission for a file.

        :param str file_id: a spreadsheet ID (aka file ID).
        :param value: user or group e-mail address, domain name
            or None for 'default' type.
        :type value: str, None
        :param str perm_type: (optional) The account type.
            Allowed values are: ``user``, ``group``, ``domain``, ``anyone``
        :param str role: (optional) The primary role for this user.
            Allowed values are: ``owner``, ``writer``, ``reader``
        :param bool notify: (optional) Whether to send an email to the target
            user/domain.
        :param str email_message: (optional) An email message to be sent
            if ``notify=True``.
        :param bool with_link: (optional) Whether the link is required for this
            permission to be active.

        :returns dict: the newly created permission

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

        url = "{}/{}/permissions".format(DRIVE_FILES_API_V3_URL, file_id)
        payload = {
            "type": perm_type,
            "role": role,
            "withLink": with_link,
        }
        params: ParamsType = {
            "supportsAllDrives": "true",
        }

        if perm_type == "domain":
            payload["domain"] = value
        elif perm_type in {"user", "group"}:
            payload["emailAddress"] = value
            params["sendNotificationEmail"] = notify
            params["emailMessage"] = email_message
        elif perm_type == "anyone":
            pass
        else:
            raise ValueError("Invalid permission type: {}".format(perm_type))

        return self.http_client.request("post", url, json=payload, params=params)

    def remove_permission(self, file_id: str, permission_id: str) -> None:
        """Deletes a permission from a file.

        :param str file_id: a spreadsheet ID (aka file ID.)
        :param str permission_id: an ID for the permission.
        """
        url = "{}/{}/permissions/{}".format(
            DRIVE_FILES_API_V3_URL, file_id, permission_id
        )

        params: ParamsType = {"supportsAllDrives": True}
        self.http_client.request("delete", url, params=params)
