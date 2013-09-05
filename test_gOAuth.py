#!/usr/bin/env python 
# -*- coding: utf-8 -*-
'''

   The full program is explained in the attached ReadMe.md

    Copyright (C) 2013 warehouseman.com

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU Affero General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU Affero General Public License for more details.

    You should have received a copy of the GNU Affero General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.

    Created on 2013-03-19

    @author: Martin H. Bramwell

    This module:
       This module is the main entry point for running the gOAuth generic client to Google document APIs.

'''

import gspread
import logging
import errno
import sys
import os

from test_parms import log_file_name, user_email, google_project_id
from test_parms import google_redirect_uri, secret, workbook_key, store_path

def main(stage):

    print 'Stage is {}'.format(stage)
    if stage == 'initial':
        print 'Deleting "shelve" file {}'.format(store_path)
        silentremove(store_path)
        
    logging.basicConfig(filename=log_file_name,level=logging.DEBUG)

    logging.debug(' -      -      -      -      -      -      -      ')
    
    user_id = user_email
    client_id = google_project_id
    
    now = {}
    now['user_id'] = user_id
    now['client_id'] = client_id
    now['debug'] = (stage == 'expired')
    
    oauth_credentials = {}
    oauth_credentials['now'] = now
        
    spreadsheet_key = workbook_key

    if stage == 'initial' :
    
        app = {}
        user = {}
        
        oauth_credentials['app'] = app
        oauth_credentials['user'] = user
        
        app[client_id] = {}
        
        user[user_id] = {}
        user[user_id][client_id] = {}
        
    
        redirect_uri = google_redirect_uri
        client_secret = secret

        access_token = None
        refresh_token = None

        print 'gOAuth.py | User "{}" must authorize application "{}".'.format(user_id, client_id)
        
        app[client_id]['redirect_uri'] = redirect_uri
        app[client_id]['client_secret'] = client_secret
        
        user[user_id][client_id]['access_token'] = access_token
        user[user_id][client_id]['refresh_token'] = refresh_token

    
    conn = gspread.connect(oauth_credentials)
    print ' ==   ==   ==   ==   ==   ==   ==   '
    wkbk = conn.open_by_key(spreadsheet_key)
    sht = wkbk.get_worksheet(0)
    print sht.acell('B1').value
    conn.disconnect()   

def silentremove(filename):
    
    try:
        os.remove(filename)
        print 'Deleted file {}'.format(filename)
    except OSError, e:
        if e.errno != errno.ENOENT: # errno.ENOENT = no such file or directory
            raise # re-raise exception if a different error occured


if __name__ == '__main__':

    stages = ['initial', 'normal', 'expired']
    if sys.argv[1] not in stages :
        print 'Usage : {} <test stage>\n      (where "test stage" is one of {})'.format(sys.argv[0], stages)
    else :
        main(sys.argv[1])

