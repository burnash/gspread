"""
gspread.client
~~~~~~~~~~~~~~

This module contains Client class responsible for managing spreadsheet files

"""

from datetime import datetime
from http import HTTPStatus
from typing import Any, Dict, List, Optional, Tuple, Union

from google.auth.credentials import Credentials
from requests import Response, Session

from .exceptions import APIError, SpreadsheetNotFound
from .http_client import HTTPClient, HTTPClientType, ParamsType
from .spreadsheet import Spreadsheet
from .urls import DRIVE_FILES_API_V3_COMMENTS_URL, DRIVE_FILES_API_V3_URL
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
        self,
        auth: Credentials,
        session: Optional[Session] = None,
        http_client: HTTPClientType = HTTPClient,
    ) -> None:
        self.http_client = http_client(auth, session)

    @property
    def expiry(self) -> Optional[datetime]:
        """Returns the expiry date of the curenlty loaded credentials

        :returns: (optional) datetime the expiry date time object.

        .. note::

           It only applies to gspread client created using oauth
        """
        return self.http_client.auth.expiry

    def set_timeout(
        self, timeout: Optional[Union[float, Tuple[float, float]]] = None
    ) -> None:
        """How long to wait for the server to send
        data before giving up, as a float, or a ``(connect timeout,
        read timeout)`` tuple.

        Use value ``None`` to restore default timeout

        Value for ``timeout`` is in seconds (s).
        """
        self.http_client.set_timeout(timeout)

    def get_file_drive_metadata(self, id: str) -> Any:
        """Get the metadata from the Drive API for a specific file
        This method is mainly here to retrieve the create/update time
        of a file (these metadata are only accessible from the Drive API).
        """
        return self.http_client.get_file_drive_metadata(id)

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

        :returns: a list of dicts containing the keys id, name, createdTime and modifiedTime.
        """
        files, _ = self._list_spreadsheet_files(title=title, folder_id=folder_id)
        return files

    def _list_spreadsheet_files(
        self, title: Optional[str] = None, folder_id: Optional[str] = None
    ) -> Tuple[List[Dict[str, Any]], Response]:
        files = []
        page_token = ""
        url = DRIVE_FILES_API_V3_URL

        query = f'mimeType="{MimeType.google_sheets}"'
        if title:
            query += f' and name = "{title}"'
        if folder_id:
            query += f' and parents in "{folder_id}"'

        params: ParamsType = {
            "q": query,
            "pageSize": 1000,
            "supportsAllDrives": True,
            "includeItemsFromAllDrives": True,
            "fields": "kind,nextPageToken,files(id,name,createdTime,modifiedTime)",
        }

        while True:
            if page_token:
                params["pageToken"] = page_token

            response = self.http_client.request("get", url, params=params)
            response_json = response.json()
            files.extend(response_json["files"])

            page_token = response_json.get("nextPageToken", None)

            if page_token is None:
                break

        return files, response

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
        spreadsheet_files, response = self._list_spreadsheet_files(title, folder_id)
        try:
            properties = finditem(
                lambda x: x["name"] == title,
                spreadsheet_files,
            )
        except StopIteration as ex:
            raise SpreadsheetNotFound(response) from ex

        # Drive uses different terminology
        properties["title"] = properties["name"]

        return Spreadsheet(self.http_client, properties)

    def open_by_key(self, key: str) -> Spreadsheet:
        """Opens a spreadsheet specified by `key` (a.k.a Spreadsheet ID).

        :param str key: A key of a spreadsheet as it appears in a URL in a browser.
        :returns: a :class:`~gspread.models.Spreadsheet` instance.

        >>> gc.open_by_key('0BmgG6nO_6dprdS1MN3d3MkdPa142WFRrdnRRUWl1UFE')
        """
        try:
            spreadsheet = Spreadsheet(self.http_client, {"id": key})
        except APIError as ex:
            if ex.response.status_code == HTTPStatus.NOT_FOUND:
                raise SpreadsheetNotFound(ex.response) from ex
            if ex.response.status_code == HTTPStatus.FORBIDDEN:
                raise PermissionError from ex
            raise ex
        return spreadsheet

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
        payload: Dict[str, Any] = {
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

        :type format: :class:`~gspread.utils.ExportFormat`

        :returns bytes: The content of the exported file.

        .. _ExportFormat: https://developers.google.com/drive/api/guides/ref-export-formats
        """

        return self.http_client.export(file_id=file_id, format=format)

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

        payload: Dict[str, Any] = {
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

                # In case of domain type the domain extract the domain
                # In case of user/group extract the emailAddress
                # Otherwise use None for type 'Anyone'

                email_or_domain = ""
                if str(p["type"]) == "domain":
                    email_or_domain = str(p["domain"])
                elif str(p["type"]) in ("user", "group"):
                    email_or_domain = str(p["emailAddress"])

                new_spreadsheet.share(
                    email_address=email_or_domain,
                    perm_type=str(p["type"]),
                    role=str(p["role"]),
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

    def import_csv(self, file_id: str, data: Union[str, bytes]) -> Any:
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
        return self.http_client.import_csv(file_id, data)

    def list_permissions(self, file_id: str) -> List[Dict[str, Union[str, bool]]]:
        """Retrieve a list of permissions for a file.

        :param str file_id: a spreadsheet ID (aka file ID).
        """
        return self.http_client.list_permissions(file_id)

    def insert_permission(
        self,
        file_id: str,
        value: Optional[str] = None,
        perm_type: Optional[str] = None,
        role: Optional[str] = None,
        notify: bool = True,
        email_message: Optional[str] = None,
        with_link: bool = False,
    ) -> Response:
        """Creates a new permission for a file.

        :param str file_id: a spreadsheet ID (aka file ID).
        :param value: user or group e-mail address, domain name
            or None for 'anyone' type.
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
        return self.http_client.insert_permission(
            file_id, value, perm_type, role, notify, email_message, with_link
        )

    def remove_permission(self, file_id: str, permission_id: str) -> None:
        """Deletes a permission from a file.

        :param str file_id: a spreadsheet ID (aka file ID.)
        :param str permission_id: an ID for the permission.
        """
        self.http_client.remove_permission(file_id, permission_id)
