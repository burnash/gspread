"""
gspread.http_client
~~~~~~~~~~~~~~

This module contains HTTPClient class responsible for communicating with
Google API.

"""

import time
from http import HTTPStatus
from typing import (
    IO,
    Any,
    Dict,
    List,
    Mapping,
    MutableMapping,
    Optional,
    Tuple,
    Type,
    Union,
)

from google.auth.credentials import Credentials
from google.auth.transport.requests import AuthorizedSession
from requests import Response, Session

from .exceptions import APIError, UnSupportedExportFormat
from .urls import (
    DRIVE_FILES_API_V3_URL,
    DRIVE_FILES_UPLOAD_API_V2_URL,
    SPREADSHEET_BATCH_UPDATE_URL,
    SPREADSHEET_SHEETS_COPY_TO_URL,
    SPREADSHEET_URL,
    SPREADSHEET_VALUES_APPEND_URL,
    SPREADSHEET_VALUES_BATCH_CLEAR_URL,
    SPREADSHEET_VALUES_BATCH_UPDATE_URL,
    SPREADSHEET_VALUES_BATCH_URL,
    SPREADSHEET_VALUES_CLEAR_URL,
    SPREADSHEET_VALUES_URL,
)
from .utils import ExportFormat, convert_credentials, quote

ParamsType = MutableMapping[str, Optional[Union[str, int, bool, float, List[str]]]]

FileType = Optional[
    Union[
        MutableMapping[str, IO[Any]],
        MutableMapping[str, Tuple[str, IO[Any]]],
        MutableMapping[str, Tuple[str, IO[Any], str]],
        MutableMapping[str, Tuple[str, IO[Any], str, MutableMapping[str, str]]],
    ]
]


class HTTPClient:
    """An instance of this class communicates with Google API.

    :param Credentials auth: An instance of google.auth.Credentials used to authenticate requests
        created by either:

        * gspread.auth.oauth()
        * gspread.auth.oauth_from_dict()
        * gspread.auth.service_account()
        * gspread.auth.service_account_from_dict()

    :param Session session: (Optional) An OAuth2 credential object. Credential objects
        created by `google-auth <https://github.com/googleapis/google-auth-library-python>`_.

        You can pass you own Session object, simply pass ``auth=None`` and ``session=my_custom_session``.

    This class is not intended to be created manually.
    It will be created by the gspread.Client class.
    """

    def __init__(self, auth: Credentials, session: Optional[Session] = None) -> None:
        if session is not None:
            self.session = session
        else:
            self.auth: Credentials = convert_credentials(auth)
            self.session = AuthorizedSession(self.auth)

        self.timeout: Optional[Union[float, Tuple[float, float]]] = None

    def login(self) -> None:
        from google.auth.transport.requests import Request

        self.auth.refresh(Request(self.session))

        self.session.headers.update({"Authorization": "Bearer %s" % self.auth.token})

    def set_timeout(self, timeout: Optional[Union[float, Tuple[float, float]]]) -> None:
        """How long to wait for the server to send
        data before giving up, as a float, or a ``(connect timeout,
        read timeout)`` tuple.

        Use value ``None`` to restore default timeout

        Value for ``timeout`` is in seconds (s).
        """
        self.timeout = timeout

    def request(
        self,
        method: str,
        endpoint: str,
        params: Optional[ParamsType] = None,
        data: Optional[bytes] = None,
        json: Optional[Mapping[str, Any]] = None,
        files: FileType = None,
        headers: Optional[MutableMapping[str, str]] = None,
    ) -> Response:
        response = self.session.request(
            method=method,
            url=endpoint,
            json=json,
            params=params,
            data=data,
            files=files,
            headers=headers,
            timeout=self.timeout,
        )

        if response.ok:
            return response
        else:
            raise APIError(response)

    def batch_update(self, id: str, body: Optional[Mapping[str, Any]]) -> Any:
        """Lower-level method that directly calls `spreadsheets/<ID>:batchUpdate <https://developers.google.com/sheets/api/reference/rest/v4/spreadsheets/batchUpdate>`_.

        :param dict body: `Batch Update Request body <https://developers.google.com/sheets/api/reference/rest/v4/spreadsheets/batchUpdate#request-body>`_.
        :returns: `Batch Update Response body <https://developers.google.com/sheets/api/reference/rest/v4/spreadsheets/batchUpdate#response-body>`_.
        :rtype: dict

        .. versionadded:: 3.0
        """
        r = self.request("post", SPREADSHEET_BATCH_UPDATE_URL % id, json=body)

        return r.json()

    def values_update(
        self,
        id: str,
        range: str,
        params: Optional[ParamsType] = None,
        body: Optional[Mapping[str, Any]] = None,
    ) -> Any:
        """Lower-level method that directly calls `PUT spreadsheets/<ID>/values/<range> <https://developers.google.com/sheets/api/reference/rest/v4/spreadsheets.values/update>`_.

        :param str range: The `A1 notation <https://developers.google.com/sheets/api/guides/concepts#a1_notation>`_ of the values to update.
        :param dict params: (optional) `Values Update Query parameters <https://developers.google.com/sheets/api/reference/rest/v4/spreadsheets.values/update#query-parameters>`_.
        :param dict body: (optional) `Values Update Request body <https://developers.google.com/sheets/api/reference/rest/v4/spreadsheets.values/update#request-body>`_.
        :returns: `Values Update Response body <https://developers.google.com/sheets/api/reference/rest/v4/spreadsheets.values/update#response-body>`_.
        :rtype: dict

        Example::

            sh.values_update(
                'Sheet1!A2',
                params={
                    'valueInputOption': 'USER_ENTERED'
                },
                body={
                    'values': [[1, 2, 3]]
                }
            )

        .. versionadded:: 3.0
        """
        url = SPREADSHEET_VALUES_URL % (id, quote(range))
        r = self.request("put", url, params=params, json=body)
        return r.json()

    def values_append(
        self, id: str, range: str, params: ParamsType, body: Optional[Mapping[str, Any]]
    ) -> Any:
        """Lower-level method that directly calls `spreadsheets/<ID>/values:append <https://developers.google.com/sheets/api/reference/rest/v4/spreadsheets.values/append>`_.

        :param str range: The `A1 notation <https://developers.google.com/sheets/api/guides/concepts#a1_notation>`_
                          of a range to search for a logical table of data. Values will be appended after the last row of the table.
        :param dict params: `Values Append Query parameters <https://developers.google.com/sheets/api/reference/rest/v4/spreadsheets.values/append#query-parameters>`_.
        :param dict body: `Values Append Request body <https://developers.google.com/sheets/api/reference/rest/v4/spreadsheets.values/append#request-body>`_.
        :returns: `Values Append Response body <https://developers.google.com/sheets/api/reference/rest/v4/spreadsheets.values/append#response-body>`_.
        :rtype: dict

        .. versionadded:: 3.0
        """
        url = SPREADSHEET_VALUES_APPEND_URL % (id, quote(range))
        r = self.request("post", url, params=params, json=body)
        return r.json()

    def values_clear(self, id: str, range: str) -> Any:
        """Lower-level method that directly calls `spreadsheets/<ID>/values:clear <https://developers.google.com/sheets/api/reference/rest/v4/spreadsheets.values/clear>`_.

        :param str range: The `A1 notation <https://developers.google.com/sheets/api/guides/concepts#a1_notation>`_ of the values to clear.
        :returns: `Values Clear Response body <https://developers.google.com/sheets/api/reference/rest/v4/spreadsheets.values/clear#response-body>`_.
        :rtype: dict

        .. versionadded:: 3.0
        """
        url = SPREADSHEET_VALUES_CLEAR_URL % (id, quote(range))
        r = self.request("post", url)
        return r.json()

    def values_batch_clear(
        self,
        id: str,
        params: Optional[ParamsType] = None,
        body: Optional[Mapping[str, Any]] = None,
    ) -> Any:
        """Lower-level method that directly calls `spreadsheets/<ID>/values:batchClear`

        :param dict params: (optional) `Values Batch Clear Query parameters <https://developers.google.com/sheets/api/reference/rest/v4/spreadsheets.values/batchClear#path-parameters>`_.
        :param dict body: (optional) `Values Batch Clear request body <https://developers.google.com/sheets/api/reference/rest/v4/spreadsheets.values/batchClear#request-body>`_.
        :rtype: dict
        """
        url = SPREADSHEET_VALUES_BATCH_CLEAR_URL % id
        r = self.request("post", url, params=params, json=body)
        return r.json()

    def values_get(
        self, id: str, range: str, params: Optional[ParamsType] = None
    ) -> Any:
        """Lower-level method that directly calls `GET spreadsheets/<ID>/values/<range> <https://developers.google.com/sheets/api/reference/rest/v4/spreadsheets.values/get>`_.

        :param str range: The `A1 notation <https://developers.google.com/sheets/api/guides/concepts#a1_notation>`_ of the values to retrieve.
        :param dict params: (optional) `Values Get Query parameters <https://developers.google.com/sheets/api/reference/rest/v4/spreadsheets.values/get#query-parameters>`_.
        :returns: `Values Get Response body <https://developers.google.com/sheets/api/reference/rest/v4/spreadsheets.values/get#response-body>`_.
        :rtype: dict

        .. versionadded:: 3.0
        """
        url = SPREADSHEET_VALUES_URL % (id, quote(range))
        r = self.request("get", url, params=params)
        return r.json()

    def values_batch_get(
        self, id: str, ranges: List[str], params: Optional[ParamsType] = None
    ) -> Any:
        """Lower-level method that directly calls `spreadsheets/<ID>/values:batchGet <https://developers.google.com/sheets/api/reference/rest/v4/spreadsheets.values/batchGet>`_.

        :param list ranges: List of ranges in the `A1 notation <https://developers.google.com/sheets/api/guides/concepts#a1_notation>`_ of the values to retrieve.
        :param dict params: (optional) `Values Batch Get Query parameters <https://developers.google.com/sheets/api/reference/rest/v4/spreadsheets.values/batchGet#query-parameters>`_.
        :returns: `Values Batch Get Response body <https://developers.google.com/sheets/api/reference/rest/v4/spreadsheets.values/batchGet#response-body>`_.
        :rtype: dict
        """
        if params is None:
            params = {}

        params["ranges"] = ranges

        url = SPREADSHEET_VALUES_BATCH_URL % id
        r = self.request("get", url, params=params)
        return r.json()

    def values_batch_update(
        self, id: str, body: Optional[Mapping[str, Any]] = None
    ) -> Any:
        """Lower-level method that directly calls `spreadsheets/<ID>/values:batchUpdate <https://developers.google.com/sheets/api/reference/rest/v4/spreadsheets.values/batchUpdate>`_.

        :param dict body: (optional) `Values Batch Update Request body <https://developers.google.com/sheets/api/reference/rest/v4/spreadsheets.values/batchUpdate#request-body>`_.
        :returns: `Values Batch Update Response body <https://developers.google.com/sheets/api/reference/rest/v4/spreadsheets.values/batchUpdate#response-body>`_.
        :rtype: dict
        """
        url = SPREADSHEET_VALUES_BATCH_UPDATE_URL % id
        r = self.request("post", url, json=body)
        return r.json()

    def spreadsheets_get(self, id: str, params: Optional[ParamsType] = None) -> Any:
        """A method stub that directly calls `spreadsheets.get <https://developers.google.com/sheets/api/reference/rest/v4/spreadsheets/get>`_."""
        url = SPREADSHEET_URL % id
        r = self.request("get", url, params=params)
        return r.json()

    def spreadsheets_sheets_copy_to(
        self, id: str, sheet_id: int, destination_spreadsheet_id: str
    ) -> Any:
        """Lower-level method that directly calls `spreadsheets.sheets.copyTo <https://developers.google.com/sheets/api/reference/rest/v4/spreadsheets.sheets/copyTo>`_."""
        url = SPREADSHEET_SHEETS_COPY_TO_URL % (id, sheet_id)

        body = {"destinationSpreadsheetId": destination_spreadsheet_id}
        r = self.request("post", url, json=body)
        return r.json()

    def fetch_sheet_metadata(self, id: str, params: Optional[ParamsType] = None) -> Any:
        """Similar to :method spreadsheets_get:`gspread.http_client.spreadsheets_get`,
        get the spreadsheet form the API but by default **does not get the cells data**.
        It only retrieve the the metadata from the spreadsheet.

        :param str id: the spreadsheet ID key
        :param dict params: (optional) the HTTP params for the GET request.
            By default sets the parameter ``includeGridData`` to ``false``.
        :returns: The raw spreadsheet
        :rtype: dict
        """
        if params is None:
            params = {"includeGridData": "false"}

        url = SPREADSHEET_URL % id

        r = self.request("get", url, params=params)

        return r.json()

    def get_file_drive_metadata(self, id: str) -> Any:
        """Get the metadata from the Drive API for a specific file
        This method is mainly here to retrieve the create/update time
        of a file (these metadata are only accessible from the Drive API).
        """

        url = DRIVE_FILES_API_V3_URL + "/{}".format(id)

        params: ParamsType = {
            "supportsAllDrives": True,
            "includeItemsFromAllDrives": True,
            "fields": "id,name,createdTime,modifiedTime",
        }

        res = self.request("get", url, params=params)

        return res.json()

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

        if format not in ExportFormat:
            raise UnSupportedExportFormat

        url = "{}/{}/export".format(DRIVE_FILES_API_V3_URL, file_id)

        params: ParamsType = {"mimeType": format}

        r = self.request("get", url, params=params)
        return r.content

    def insert_permission(
        self,
        file_id: str,
        email_address: Optional[str],
        perm_type: Optional[str],
        role: Optional[str],
        notify: bool = True,
        email_message: Optional[str] = None,
        with_link: bool = False,
    ) -> Response:
        """Creates a new permission for a file.

        :param str file_id: a spreadsheet ID (aka file ID).
        :param email_address: user or group e-mail address, domain name
            or None for 'anyone' type.
        :type email_address: str, None
        :param str perm_type: (optional) The account type.
            Allowed values are: ``user``, ``group``, ``domain``, ``anyone``
        :param str role: (optional) The primary role for this user.
            Allowed values are: ``owner``, ``writer``, ``reader``
        :param bool notify: Whether to send an email to the target
            user/domain. Default ``True``.
        :param str email_message: (optional) An email message to be sent
            if ``notify=True``.
        :param bool with_link: Whether the link is required for this
            permission to be active. Default ``False``.

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
            payload["domain"] = email_address
        elif perm_type in {"user", "group"}:
            payload["emailAddress"] = email_address
            params["sendNotificationEmail"] = notify
            params["emailMessage"] = email_message
        elif perm_type == "anyone":
            pass
        else:
            raise ValueError("Invalid permission type: {}".format(perm_type))

        return self.request("post", url, json=payload, params=params)

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

            r = self.request("get", url, params=params).json()
            permissions.extend(r["permissions"])

            token = r.get("nextPageToken", None)

        return permissions

    def remove_permission(self, file_id: str, permission_id: str) -> None:
        """Deletes a permission from a file.

        :param str file_id: a spreadsheet ID (aka file ID.)
        :param str permission_id: an ID for the permission.
        """
        url = "{}/{}/permissions/{}".format(
            DRIVE_FILES_API_V3_URL, file_id, permission_id
        )

        params: ParamsType = {"supportsAllDrives": True}
        self.request("delete", url, params=params)

    def import_csv(self, file_id: str, data: Union[str, bytes]) -> Any:
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
        # Make sure we send utf-8
        if isinstance(data, str):
            data = data.encode("utf-8")

        headers = {"Content-Type": "text/csv"}
        url = "{}/{}".format(DRIVE_FILES_UPLOAD_API_V2_URL, file_id)

        res = self.request(
            "put",
            url,
            data=data,
            params={
                "uploadType": "media",
                "convert": True,
                "supportsAllDrives": True,
            },
            headers=headers,
        )

        return res.json()


class BackOffHTTPClient(HTTPClient):
    """BackoffClient is a gspread client with exponential
    backoff retries.

    In case a request fails due to some API rate limits,
    it will wait for some time, then retry the request.

    This can help by trying the request after some time and
    prevent the application from failing (by raising an APIError exception).

    .. Warning::
        This Client is not production ready yet.
        Use it at your own risk !

    .. note::
        To use with the `auth` module, make sure to pass this backoff
        client factory using the ``client_factory`` parameter of the
        method used.

    .. note::
        Currently known issues are:

        * will retry exponentially even when the error should
          raise instantly. Due to the Drive API that raises
          403 (Forbidden) errors for forbidden access and
          for api rate limit exceeded."""

    _HTTP_ERROR_CODES: List[HTTPStatus] = [
        HTTPStatus.REQUEST_TIMEOUT,  # in case of a timeout
        HTTPStatus.TOO_MANY_REQUESTS,  # sheet API usage rate limit exceeded
    ]
    _NR_BACKOFF: int = 0
    _MAX_BACKOFF: int = 128  # arbitrary maximum backoff

    def request(self, *args: Any, **kwargs: Any) -> Response:
        # Check if we should retry the request
        def _should_retry(
            code: int,
            error: Mapping[str, Any],
            wait: int,
        ) -> bool:
            # Drive API return a dict object 'errors', the sheet API does not
            if "errors" in error:
                # Drive API returns a code 403 when reaching quotas/usage limits
                if (
                    code == HTTPStatus.FORBIDDEN
                    and error["errors"][0]["domain"] == "usageLimits"
                ):
                    return True

            # We retry if:
            #   - the return code is one of:
            #     - 429: too many requests
            #     - 408: request timeout
            #     - >= 500: some server error
            #   - AND we did not reach the max retry limit
            return (
                code in self._HTTP_ERROR_CODES
                or code >= HTTPStatus.INTERNAL_SERVER_ERROR
            ) and wait <= self._MAX_BACKOFF

        try:
            return super().request(*args, **kwargs)
        except APIError as err:
            code = err.code
            error = err.error

            self._NR_BACKOFF += 1
            wait = min(2**self._NR_BACKOFF, self._MAX_BACKOFF)

            # check if error should retry
            if _should_retry(code, error, wait) is True:
                time.sleep(wait)

                # make the request again
                response = self.request(*args, **kwargs)

                # reset counters for next time
                self._NR_BACKOFF = 0

                return response

            # failed too many times, raise APIEerror
            raise err


HTTPClientType = Type[HTTPClient]
