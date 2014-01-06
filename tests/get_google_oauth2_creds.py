#!/usr/bin/python
# -*- coding: utf-8 -*-
#
'''
    This script will attempt to open your web browser,
    perform OAuth 2 authentication and print out your full set
    of OAuth credentials in the form of Python variable declarations.

    It depends on Google's Python library: oauth2client.

    To install that dependency from PyPI:

    $ pip install oauth2client

    Then run this script:

    $ python get_google_oauth2_creds.py
    
    This is a combination of snippets from:
    https://developers.google.com/api-client-library/python/guide/aaa_oauth

'''
import os, sys, argparse, json
from pprint import pprint

try:
    from oauth2client.client import OAuth2WebServerFlow
    from oauth2client.tools import run_flow
    from oauth2client.file import Storage
    from oauth2client.util import 	POSITIONAL_WARNING, POSITIONAL_EXCEPTION, POSITIONAL_IGNORE
except ImportError:
    print "ImportError: Please execute the following command (with root privileges):\npip install oauth2client"
    exit(-1)

class NameSpace(object):
  def __init__(self, adict):
    self.__dict__.update(adict)

def main(id, secret, manual=True):

    flow = OAuth2WebServerFlow(client_id=id,
                               client_secret=secret,
                               scope='https://spreadsheets.google.com/feeds https://docs.google.com/feeds',
                               redirect_uri='http://example.com/auth_return')

    storage = Storage('creds.data')

    flags = NameSpace({'noauth_local_webserver': manual, 'auth_host_port' : [8080, 8090], 'auth_host_name' : 'localhost', 'logging_level' : POSITIONAL_WARNING})

    credentials = run_flow(flow, storage, flags)

    print "\n =    =    =    =    =    =    =    =    =    =    =    =    =    =   "
    print "\n\n Data for use in gspread 'nose' tests, in file test.config : "
    print " .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  . "
    print "[Google Account]"    
    print "# auth_type: UIDPwd"    
    print "auth_type: OAuth"    
    print "#"
    print "client_secret: {}".format(secret)
    print "client_id: {}".format(id)
    print "access_token: {}".format(credentials.access_token)
    print "refresh_token: {}".format(credentials.refresh_token)
    print ""

    qiktest = open('qiktest.py', 'w')
    qiktest.write("# - - - - - - - - - - - - - - - - - - - - - - - - - - -")
    qiktest.write("\n# -*- coding: utf-8 -*-")
    qiktest.write("\nimport gspread")
    qiktest.write("\n#")
    qiktest.write("\nrefresh_token = '{}'".format(credentials.refresh_token))
    qiktest.write("\nclient_secret = '{}'".format(secret))
    qiktest.write("\nclient_id = '{}'".format(id))
    qiktest.write("\n#")
    qiktest.write("\nkey_ring = {}")
    qiktest.write("\nkey_ring['grant_type'] = 'refresh_token'")
    qiktest.write("\nkey_ring['refresh_token'] = refresh_token")
    qiktest.write("\nkey_ring['client_secret'] = client_secret")
    qiktest.write("\nkey_ring['client_id'] = client_id")
    qiktest.write("\n#")
    qiktest.write("\naccess_token = '{}'".format(credentials.access_token))
    qiktest.write("\ngc = gspread.authorize(access_token, key_ring)")
    qiktest.write("\n#")
    qiktest.write("\nwkbk = gc.open_by_url('{}')".format(spreadsheet_url))
    qiktest.write("\ncnt = 1")
    qiktest.write("\nprint 'Found sheets:'")
    qiktest.write("\nfor sheet in wkbk.worksheets():")
    qiktest.write("\n    print ' - Sheet #{}: Id = {}  Title = {}'.format(cnt, sheet.id, sheet.title)")
    qiktest.write("\n    cnt += 1")
    qiktest.write("\n#")
    qiktest.write("\n# - - - - - - - - - - - - - - - - - - - - - - - - - - -")
    qiktest.close()
    #
    print "\n\n   A simple example file called qiktest.py was written to disk."
    print "   It lists the names of the sheets in the target spreadsheet."
    print "   Test it with:"
    print "      $  python qiktest.py\n\n\n"

if __name__ == '__main__':

    json_files = []
    files = [f for f in os.listdir('.') if os.path.isfile(f)]
    cnt = 0;
    for f in files:
        if f.endswith('.json'):
            cnt += 1;
            json_files.append(f)
            
    theFile = None
    client_id = None
    client_secret = None
    if cnt < 1:
        print '\n\nCould not find exactly one (1) expected json file (named like "client_secret_*.json" for example).'
        print 'You get such a file from https://cloud.google.com/console in the sub-section :'
        print '   - APIs & auth '
        print '      - Credentials '
        print '          - Client ID for native application'
        print '             - [Download JSON]\n\n'
        client_id = raw_input('Paste your Google "Client ID" : ')
        client_secret = raw_input('Paste your Google "Client Secret" : ')
        
    else:
        theFile = json_files[0]
        if cnt > 1:
            print '\n\nPlease type the number of the json file that contains the credentials you want to try.'
            cnt = 0
            for jf in json_files:
                cnt += 1;
                print '{}) -- {}'.format(cnt, jf)
            theFile = json_files[int(raw_input('Which? ')) - 1 ]
        
        json_data = open(theFile)
        oauth_creds = json.load(json_data)['installed']
        client_id = oauth_creds['client_id']
        client_secret = oauth_creds['client_secret']
        json_data.close()
        print '\n The file "{}" contains :\n'.format(theFile)
        print '               Client id : {}'.format(client_id)
        print '               Client secret : {}\n'.format(client_secret)
    
    print 'Identify the Google spreadsheet you want to use; use the full URL ("http://" etc, etc) '
    spreadsheet_url  = raw_input('Paste the full URL here : ')
    #
    manual = raw_input("Shall we try to open a page in your browser?  (Y/y)  : ") not in "Yy"
    
    main(client_id, client_secret, manual)
