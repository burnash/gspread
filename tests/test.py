import os
import unittest
import ConfigParser

import gspread

class ClientTest(unittest.TestCase):

    def setUp(self):
        creds_filename = "account_credentials.cfg"
        try:
            config_filename = os.path.join(os.path.dirname(__file__), creds_filename)
            config = ConfigParser.ConfigParser()
            config.readfp(open(config_filename))
            self.email = config.get('Google Account', 'email')
            self.password = config.get('Google Account', 'password')
        except IOError:
            msg = "Can't find %s for reading google account credentials. " \
                  "You can create it from %s.example in tests/ directory."
            raise Exception(msg % (creds_filename, creds_filename))

    def test_instantiate(self):
        gc = gspread.Client(self.email, self.password)
        self.assertTrue(isinstance(gc, gspread.Client))

    def test_login_and_open_book(self):
        gc = gspread.Client(self.email, self.password)
        gc.login()
        book = gc.open('test1')
        self.assertTrue(isinstance(book, gspread.Book))

        self.book = book

        sheet = book.get_sheet(0)
        self.assertTrue(isinstance(sheet, gspread.Sheet))


if __name__ == '__main__':
    unittest.main()
