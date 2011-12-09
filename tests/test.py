import os
import unittest
import ConfigParser

import gspread

class ClientTest(unittest.TestCase):

    def setUp(self):
        config_filename = os.path.join(os.path.dirname(__file__), "account_credentials.cfg")
        config = ConfigParser.ConfigParser()
        config.readfp(open(config_filename))
        self.config = config

    def test_login(self):
        print self.config.get('Google Account', 'email')


if __name__ == '__main__':
    unittest.main()
