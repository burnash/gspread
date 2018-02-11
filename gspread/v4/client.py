import requests

from ..utils import finditem

from ..exceptions import SpreadsheetNotFound
from .exceptions import APIError
from .models import Spreadsheet


class Client(object):
    """An instance of this class communicates with Google Data API.

    :param auth: An OAuth2 credential object. Credential objects are those created by the
                 oauth2client library. https://github.com/google/oauth2client
    :param http_session: (optional) A session object capable of making HTTP requests while persisting headers.
                                    Defaults to :class:`~gspread.httpsession.HTTPSession`.

    >>> c = gspread.v4.Client(auth=OAuthCredentialObject)

    """
    def __init__(self, auth, http_session=None):
        self.auth = auth
        self.session = http_session or requests.Session()

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
            files=None):
        # url = '%s%s' % (self.api_base_url, endpoint)

        response = getattr(self.session, method)(
            endpoint, json=json, params=params, data=data, files=files
        )

        if response.ok:
            return response
        else:
            raise APIError(response)

    def list_spreadsheet_files(self):
        url = (
            "https://www.googleapis.com/drive/v3/files"
            "?q=mimeType%3D'application%2Fvnd.google-apps.spreadsheet'"
        )
        r = self.request('get', url)
        return r.json()['files']

    def open(self, title):
        try:
            properties = finditem(
                lambda x: x['name'] == title,
                self.list_spreadsheet_files()
            )

            return Spreadsheet(self, properties)
        except StopIteration:
            raise SpreadsheetNotFound

    def open_by_key(self, key):
        raise NotImplementedError

    def open_by_url(self, url):
        raise NotImplementedError

    def openall(self, title=None):
        raise NotImplementedError

