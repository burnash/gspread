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


from gspread import googoauth
from gspread import exceptions
import gspread

import prepSMTP

import errno
import sys
import os

# TestSmtpAuthentication, 
# import oauth2

parameters_file = 'test_parms.py'
try:
    from test_parms import log_file_name, log_file_path, store_path
    
    from test_parms import google_project_client_id, google_project_client_email
    from test_parms import google_project_redirect_uri, google_project_client_secret

    from test_parms import users

except ImportError:
    print 'You must edit "{0}.example" and save as "{0}" before running the tests.'.format(parameters_file)
    exit(-1)
    
SMTP_ACCESS = 'google_project_client_smtp_access_token'
SMTP_REFRESH = 'google_project_client_smtp_refresh_token'

gpcsat_len = 0
gpcsrt_len = 0
try:

    from test_parms import google_project_client_smtp_access_token
    from test_parms import google_project_client_smtp_refresh_token
    
    gpcsat_len = len(google_project_client_smtp_access_token)
    gpcsrt_len = len(google_project_client_smtp_refresh_token)
    
    assert gpcsat_len > 50 and gpcsat_len < 60
    assert gpcsrt_len == 45

except :

    prepSMTP.prep_smtp(True)
    print "Please repeat the command now."
    exit()
    
    

CLEAN = 'clean'
NORMAL = 'normal'
EXPIRED = 'expired'

import fileinput
    
def main(stage):
    
    print 'Doing stage : {}'.format(stage)
    if stage == CLEAN :
        print 'Deleting "shelve" file {}'.format(store_path)
        silentremove(store_path)
        return

    nickname = 0
    try :
        nickname = sys.argv[2]
    except :
        pass

    oauth_credentials = googoauth.prep_creds(
                          nickname
                        , users
                        , google_project_client_id
                        , google_project_client_secret
                        , google_project_redirect_uri
                        , google_project_client_email
                        , google_project_client_smtp_access_token
                        , google_project_client_smtp_refresh_token
                    )
                    
    oauth_credentials.now.debug = (stage == EXPIRED)

    idxUser = 0
    try :
        idxUser = sys.argv[2]
    except :
        pass
        
    user_id = users[idxUser]['user_email']

    try :
    
        conn = gspread.connect(oauth_credentials)
    
        print ' ==   ==   Reading sheet #0,  cell B2  ==   ==   '
        spreadsheet_key = users[nickname]['workbook_key']
        wkbk = conn.open_by_key(spreadsheet_key)
        sht = wkbk.get_worksheet(0)
        print sht.acell('B1').value
        
        sheet_name = 'GENERATED' 
        print ' ==   ==   Adding a sheet called %s  ==  >> ' % sheet_name
        # Get the target sheet in that workbook 
        try :
            wkbk.del_worksheet(wkbk.worksheet(sheet_name))
        except gspread.WorksheetNotFound as wsnf :
            pass
        sht = wkbk.add_worksheet(sheet_name, 5, 5)
        sht.update_acell('B2', user_id)    
        
        conn.disconnect()   
        
    except exceptions.InvalidUserClientMapping as iucm :
        if users[idxUser]['auth_method'] == 'ToBeDropped' :
            return
        raise exceptions.InvalidUserClientMapping(iucm)
        
    return


def silentremove(filename):
    
    try:
        os.remove(filename)
        print 'Deleted file {}'.format(filename)
    except OSError, e:
        if e.errno != errno.ENOENT: # errno.ENOENT = no such file or directory
            raise # re-raise exception if a different error occured


if __name__ == '__main__':

    TEST_STAGE = 'test stage'
    USER = 'user nickname'
    stages = [CLEAN, NORMAL, EXPIRED]
    msg = ''
    msg += 'Usage : %s <%s> <%s>' % (sys.argv[0], TEST_STAGE, USER)
    msg += '\n      Where :'
    msg += '\n        -- "%s" is one of %s)' % (TEST_STAGE, stages)
    
    
    if len(sys.argv) > 1 :
        if sys.argv[1] in stages :
            main(sys.argv[1])


