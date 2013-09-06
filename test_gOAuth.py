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

try:
    from test_parms import log_file_name, log_file_path, user_email, google_project_id
    from test_parms import google_redirect_uri, secret, workbook_key, store_path
except ImportError:
    print 'You must edit "test_parms.py.example" and save as "test_parms.py" before running the tests.'
    exit(-1)

CLEAN = 'clean'
PREPARE = 'prepare'
NORMAL = 'normal'
EXPIRED = 'expired'

def main(stage):

    print 'Stage is {}'.format(stage)
    if stage == CLEAN :
        print 'Deleting "shelve" file {}'.format(store_path)
        silentremove(store_path)
        exit(0)
        
    if not os.path.exists(log_file_path) :
        os.makedirs(log_file_path)
    logging.basicConfig(filename=log_file_path + '/' + log_file_name,level=logging.DEBUG)

    logging.debug(' -      -      -      -      -      -      -      ')
    
    client_id = google_project_id
    
    now = {}
    now['client_id'] = client_id
    now['debug'] = (stage == EXPIRED)
    
    idxUser = 0
    try :
        idxUser = int(sys.argv[2]) - 1
    except :
        pass
        
    user_id = user_email[idxUser]
    spreadsheet_key = workbook_key[idxUser]
        
    now['user_id'] = user_id
    
    oauth_credentials = {}
    oauth_credentials['now'] = now
        
    print 'Working with :'
    print '      User : {}'.format(now['user_id'])
    print '  Workbook : {}'.format(spreadsheet_key)

    if stage == PREPARE :
    
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

def f(x):
    msg = '\n        -- "user #" is '
    return {
              1: msg + '1 only.'
            , 2: msg + '1 or 2'
        }.get(x, msg + '1 through {}'.format(x))

if __name__ == '__main__':

    '''
    print f(1)
    print f(2)
    print f(7)
    print f(5)
    exit(0)
    '''
    stages = [CLEAN, PREPARE, NORMAL, EXPIRED]
    msg = ''
    msg += 'Usage : {} <test stage> <user #>'.format(sys.argv[0])
    msg += '\n      Where :'
    msg += '\n        -- "test stage" is one of {})'.format(stages)
    
    
    if len(sys.argv) > 1 :
        if sys.argv[1] in stages :
            main(sys.argv[1])
            exit(0)
            
    print msg
    idx = 0
    for user in user_email :
        idx += 1
        print '        -- "user #"{} is {}'.format(idx, user)


