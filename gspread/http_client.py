"""
gspread.http_client
~~~~~~~~~~~~~~

This module contains HTTPClient class responsible for communicating with
Google API.

"""
from http import HTTPStatus
from typing import IO, Any, List, Mapping, MutableMapping, Optional, Tuple, Type, Union

from google.auth.credentials import Credentials  # type: ignore
from google.auth.transport.requests import AuthorizedSession  # type: ignore
from requests import Response, Session

from .exceptions import APIError
from .utils import convert_credentials

ParamsType = MutableMapping[str, Optional[Union[str, int, bool, float]]]


class HTTPClient:
    """An instance of this class communicates with Google API.

    :param auth: An OAuth2 credential object. Credential objects
        created by `google-auth <https://github.com/googleapis/google-auth-library-python>`_.

    This class is not intended to be created manually.
    It will be created by the gspread.Client class.
    """

    def __init__(self, auth: Credentials, session = None) -> None:

        if session is not None:
            self.session = session
        else:
            self.auth: Credentials = convert_credentials(auth)
            self.session: Session = AuthorizedSession(self.auth)

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
        files: Optional[IO] = None,
        headers: Optional[Mapping[str, str]] = None,
    ) -> Response:
        response = getattr(self.session, method)(
            endpoint,
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
