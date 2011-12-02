import gdata.spreadsheet
import gdata.spreadsheet.service

class Client(object):
    def __init__(self, email, password, source='gspread Client'):
        self._gd_client = gdata.spreadsheet.service.SpreadsheetsService()
        self._gd_client.email = email
        self._gd_client.password = password
        self._gd_client.source = source

    def login(self):
        self._gd_client.ProgrammaticLogin()

    def open(self, book_name):
        feed = self._gd_client.GetSpreadsheetsFeed()
        sp_entries = filter(lambda x: x.content.text.strip() == book_name, feed.entry)
        return Book(self, sp_entries[0])

    def open_all(self, book_name=None):
        pass


class Book(object):
    def __init__(self, client, gdata_book_object):
        self._client = client
        self.gdata_book_object = gdata_book_object
        self._sheet_list = []

    def sheet_by_name(self, sheet_name):
        pass

    def _fetch_sheets(self):
        gdata_client = self._client._gd_client
        id_parts = self.gdata_book_object.id.text.split('/')
        self._gdata_book_key = id_parts[-1]
        feed = gdata_client.GetWorksheetsFeed(self._gdata_book_key)
        self._sheet_list = [Sheet(self, e.id.text.split('/')[-1]) for e in feed.entry]

    def sheets(self):
        if not self._sheet_list:
            self._fetch_sheets()
        return self._sheet_list[:]

    def get_sheet(self, sheet_index):
        if not self._sheet_list:
            self._fetch_sheets()
        return self._sheet_list[sheet_index]


class Sheet(object):
    def __init__(self, book_obj, gdata_sheet_id):
        self._book_obj = book_obj
        self._gdata_sheet_id = gdata_sheet_id

    def row(self, rowx):
        pass

    def cell(self, rowx, colx):
        pass

    def get_rows(self):
        gdata_client = self._book_obj._client._gd_client
        feed = gdata_client.GetCellsFeed(self._book_obj._gdata_book_key, self._gdata_sheet_id)

        rows = {}
        for f in feed.entry:
            rows.setdefault(int(f.cell.row), []).append(f.cell)

        rows_list = []
        for r in sorted(rows.keys()):
            rows_list.append(rows[r])

        simple_rows_list = []
        for r in rows_list:
            simple_row = []
            for c in r:
                simple_row.append(c.text)
            simple_rows_list.append(simple_row)

        return simple_rows_list

    def col_values(self, colx):
        gdata_client = self._book_obj._client._gd_client
        feed = gdata_client.GetCellsFeed(self._book_obj._gdata_book_key, self._gdata_sheet_id)

        cells = {}
        for f in feed.entry:
            if int(f.cell.col) == colx:
                cells[int(f.cell.row)] = f.cell

        last_index = max(cells.keys())
        vals = []
        for i in range(last_index):
            c = cells.get(i)
            vals.append(c.text if c else None)

        return vals

    def update_cell(self, rowx, colx, val):
        gdata_client = self._book_obj._client._gd_client

        entry = gdata_client.UpdateCell(row=rowx, col=colx, inputValue=val,
            key=self._book_obj._gdata_book_key, wksht_id=self._gdata_sheet_id)

        return isinstance(entry, gdata.spreadsheet.SpreadsheetsCell)
