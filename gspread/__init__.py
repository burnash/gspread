from xml.etree import ElementTree

from .httpsession import HTTPSession


AUTH_SERVER = 'https://www.google.com'
SPREADSHEETS_SERVER = 'spreadsheets.google.com'
ATOM_NS = 'http://www.w3.org/2005/Atom'
SPREADSHEET_NS = 'http://schemas.google.com/spreadsheets/2006'


def _ns(name):
    return '{%s}%s' % (ATOM_NS, name)

def _ns1(name):
    return '{%s}%s' % (SPREADSHEET_NS, name)


class Client(object):
    """A client class for communicating with Google's Date API.

    auth param is a tuple containing an email and a password.
    http_session is session object capable of making HTTP requests while
    persisting headers. Defaults to gspread.httpsession.HTTPSession.

    """
    def __init__(self, auth, http_session=None):
        self.auth = auth

        if not http_session:
            self.session = HTTPSession()

    def _get_auth_token(self, content):
        for line in content.splitlines():
            if line.startswith('Auth='):
                return line[5:]
        return None

    def login(self):
        """Authorize client using ClientLogin.

        This method is using API described at:
        http://code.google.com/apis/accounts/docs/AuthForInstalledApps.html

        """
        source = 'burnash-gspread-0.0.1'
        service = 'wise'

        data = {'Email': self.auth[0],
                'Passwd': self.auth[1],
                'accountType': 'HOSTED_OR_GOOGLE',
                'service': service,
                'source': source}

        url = AUTH_SERVER + '/accounts/ClientLogin'

        r = self.session.post(url, data)
        content = r.read()

        if r.code == 200:
            token = self._get_auth_token(content)
            auth_header = "GoogleLogin auth=%s" % token
            self.session.add_header('Authorization', auth_header)

        elif r.code == 403:
            if content.strip() == 'Error=BadAuthentication':
                raise Exception("Incorrect username or password")
            else:
                raise Exception("Unable to authenticate. %s code" % r.code)
        else:
            raise Exception("Unable to authenticate. %s code" % r.code)

    def open(self, title):
        """Open a spreadsheet with specified title.

        If there's more than one spreadsheet with same title the first one
        will be opened.

        """
        feed = self.get_spreadsheets_feed()

        for elem in feed.findall(_ns('entry')):
            title = elem.find(_ns('title')).text
            if title.strip() == title:
                id_parts = elem.find(_ns('id')).text.split('/')
                key = id_parts[-1]
                return Spreadsheet(self, key)

    def get_spreadsheets_feed(self, visibility='private', projection='full'):
        uri = ('https://%s/feeds/spreadsheets/%s/%s'
            % (SPREADSHEETS_SERVER, visibility, projection))

        r = self.session.get(uri)
        return ElementTree.fromstring(r.read())

    def get_worksheets_feed(self, key, visibility='private', projection='full'):
        uri = ('https://%s/feeds/worksheets/%s/%s/%s'
            % (SPREADSHEETS_SERVER, key, visibility, projection))

        r = self.session.get(uri)
        return ElementTree.fromstring(r.read())

    def get_cells_feed(self, key, worksheet_key, cell=None,
                       visibility='private', projection='full'):
        uri = ('https://%s/feeds/cells/%s/%s/%s/%s'
            % (SPREADSHEETS_SERVER, key, worksheet_key, visibility, projection))

        if cell != None:
            uri = '%s/%s' % (uri, cell)

        r = self.session.get(uri)
        return ElementTree.fromstring(r.read())

    def put_cell(self, url, data):
        headers = {'Content-Type': 'application/atom+xml'}
        data = "<?xml version='1.0' encoding='UTF-8'?>%s" % data
        r = self.session.put(url, data, headers=headers)

        return ElementTree.fromstring(r.read())


class Spreadsheet(object):
    """A model for representing a spreadsheet object.

    """
    def __init__(self, client, key):
        self.client = client
        self.key = key
        self._sheet_list = []

    def sheet_by_name(self, sheet_name):
        pass

    def _fetch_sheets(self):
        feed = self.client.get_worksheets_feed(self.key)
        for elem in feed.findall(_ns('entry')):
            key = elem.find(_ns('id')).text.split('/')[-1]
            self._sheet_list.append(Worksheet(self, key))

    def worksheets(self):
        """Return a list of all worksheets in a spreadsheet."""
        if not self._sheet_list:
            self._fetch_sheets()
        return self._sheet_list[:]

    def get_worksheet(self, sheet_index):
        """Return a worksheet with index `sheet_index`.

        Indexes start from zero.

        """
        if not self._sheet_list:
            self._fetch_sheets()
        return self._sheet_list[sheet_index]


class Worksheet(object):
    """A model for worksheet object.

    """
    def __init__(self, spreadsheet, key):
        self.spreadsheet = spreadsheet
        self.client = spreadsheet.client
        self.key = key

    def _cell_addr(self, row, col):
        return 'R%sC%s' % (row, col)

    def _fetch_cells(self):
        feed = self.client.get_cells_feed(self.spreadsheet.key, self.key)
        cells_list = []
        for elem in feed.findall(_ns('entry')):
            c_elem = elem.find(_ns1('cell'))
            cells_list.append(Cell(self, c_elem.get('row'),
                                   c_elem.get('col'), c_elem.text))

        return cells_list

    def cell(self, row, col):
        """Return a Cell object.

        Fetch a cell in row `row` and column `col`.

        """
        feed = self.client.get_cells_feed(self.spreadsheet.key,
                                          self.key, self._cell_addr(row, col))
        cell_elem = feed.find(_ns1('cell'))
        return Cell(self, cell_elem.get('row'), cell_elem.get('col'),
                    cell_elem.text)

    def get_all_rows(self):
        """Return a list of lists containing worksheet's rows."""
        cells = self._fetch_cells()

        rows = {}
        for cell in cells:
            rows.setdefault(int(cell.row), []).append(cell)

        rows_list = []
        for r in sorted(rows.keys()):
            rows_list.append(rows[r])

        simple_rows_list = []
        for r in rows_list:
            simple_row = []
            for c in r:
                simple_row.append(c.value)
            simple_rows_list.append(simple_row)

        return simple_rows_list

    def row_values(self, row):
        """Return a list of all values in row `row`.

        Empty cells in this list will be rendered as None.

        """
        cells_list = self._fetch_cells()

        cells = {}
        for cell in cells_list:
            if int(cell.row) == row:
                cells[int(cell.col)] = cell

        last_index = max(cells.keys())
        vals = []
        for i in range(1, last_index + 1):
            c = cells.get(i)
            vals.append(c.value if c else None)

        return vals

    def col_values(self, col):
        """Return a list of all values in column `col`.

        Empty cells in this list will be rendered as None.

        """
        cells_list = self._fetch_cells()

        cells = {}
        for cell in cells_list:
            if int(cell.col) == col:
                cells[int(cell.row)] = cell

        last_index = max(cells.keys())
        vals = []
        for i in range(1, last_index + 1):
            c = cells.get(i)
            vals.append(c.value if c else None)

        return vals

    def update_cell(self, row, col, val):
        """Set new value to a cell."""
        feed = self.client.get_cells_feed(self.spreadsheet.key,
                                          self.key, self._cell_addr(row, col))
        cell_elem = feed.find(_ns1('cell'))
        cell_elem.set('inputValue', val)
        edit_link = filter(lambda x: x.get('rel') == 'edit',
                feed.findall(_ns('link')))[0]
        uri = edit_link.get('href')

        self.client.put_cell(uri, ElementTree.tostring(feed))


class Cell(object):
    """A model for cell object.

    """
    def __init__(self, worksheet, row, col, value):
        self.row = row
        self.col = col
        self.value = value
