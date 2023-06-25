"""
gspread.http_client
~~~~~~~~~~~~~~

This module contains HTTPClient class responsible for communicating with
Google API.

"""
from http import HTTPStatus
from typing import IO, Any, List, Mapping, MutableMapping, Optional, Tuple, Type, Union

from google.auth.credentials import Credentials
from google.auth.transport.requests import AuthorizedSession
from requests import Response, Session

from .exceptions import APIError
from .urls import (
    DRIVE_FILES_API_V3_URL,
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
from .utils import convert_credentials, quote

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

    def set_timeout(self, timeout: Union[float, Tuple[float, float]]) -> None:
        """How long to wait for the server to send
        data before giving up, as a float, or a ``(connect timeout,
        read timeout)`` tuple.

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
        self, id: str, sheet_id: str, destination_spreadsheet_id: str
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

    def _get_file_drive_metadata(self, id: str) -> Any:
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
        HTTPStatus.FORBIDDEN,  # Drive API return a 403 Forbidden on usage rate limit exceeded
        HTTPStatus.REQUEST_TIMEOUT,  # in case of a timeout
        HTTPStatus.TOO_MANY_REQUESTS,  # sheet API usage rate limit exceeded
    ]
    _NR_BACKOFF: int = 0
    _MAX_BACKOFF: int = 128  # arbitrary maximum backoff
    _MAX_BACKOFF_REACHED: bool = False  # Stop after reaching _MAX_BACKOFF

    def request(self, *args: Any, **kwargs: Any) -> Response:
        try:
            return super().request(*args, **kwargs)
        except APIError as err:
            data = err.response.json()
            code = data["error"]["code"]

            # check if error should retry
            if code in self._HTTP_ERROR_CODES and self._MAX_BACKOFF_REACHED is False:
                self._NR_BACKOFF += 1
                wait = min(2**self._NR_BACKOFF, self._MAX_BACKOFF)

                if wait >= self._MAX_BACKOFF:
                    self._MAX_BACKOFF_REACHED = True

                import time

                time.sleep(wait)

                # make the request again
                response = self.request(*args, **kwargs)

                # reset counters for next time
                self._NR_BACKOFF = 0
                self._MAX_BACKOFF_REACHED = False

                return response

            # failed too many times, raise APIEerror
            raise err


HTTPClientType = Type[HTTPClient]
