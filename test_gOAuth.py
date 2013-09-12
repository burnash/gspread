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

import smtplib
import gspread
import logging
import base64
import errno
import sys
import os

from oauth2 import GeneratePermissionUrl, AuthorizeTokens, RefreshToken, GenerateOAuth2String
# TestSmtpAuthentication, 
# import oauth2

parameters_file = 'test_parms.py'
try:
    from test_parms import log_file_name, log_file_path, store_path
    
    from test_parms import google_project_client_id, google_project_client_email
    from test_parms import google_project_redirect_uri, google_project_client_secret
    from test_parms import google_project_redirect_uri, google_project_client_secret

    from test_parms import users

except ImportError:
    print 'You must edit "%s.example" and save as "%s" before running the tests.' % parameters_file
    exit(-1)
SMTP_ACCESS = 'google_project_client_smtp_access_token'
SMTP_REFRESH = 'google_project_client_smtp_refresh_token'
configure_email = False
try:
    from test_parms import google_project_client_smtp_access_token
    from test_parms import google_project_client_smtp_refresh_token
    assert len(google_project_client_smtp_access_token) == 59
    assert len(google_project_client_smtp_refresh_token) == 45
except :
    configure_email = True
    print 'Will run the "email" mode to set up email requests.'

CLEAN = 'clean'
'''
SMTP = 'mail'
REQUEST = 'request'
START = 'start'
'''
NORMAL = 'normal'
EXPIRED = 'expired'

import fileinput
def update_parms_file(acc, ref):

    acc_parm = "%s = '%s'" % (SMTP_ACCESS, acc)
    a = True
    
    ref_parm = "%s = '%s'" % (SMTP_REFRESH, ref)
    r = True
    
    
    print ' ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~'
    for line in fileinput.input(parameters_file, inplace=1):
      if line.startswith(SMTP_ACCESS) :
          print acc_parm
          a = False
      elif line.startswith(SMTP_REFRESH) :
          print ref_parm
          r = False
      else :
          print line,
    
    print ' ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~'
    if a or r :
        with open(parameters_file, "a") as myfile:
            myfile.write('\n# Appended automatically . . . ')
            if a :
                myfile.write('\n%s' % acc_parm)
            if r :
                myfile.write('\n%s' % ref_parm)
            myfile.write('\n#\n')
    print ' ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~'
       
              
def prep_smtp(creds) :

    scope = 'https://mail.google.com/'
    client_id = creds['now']['client_id']
    client_email = creds['gclient'][client_id]['client_email']
    client_secret = creds['gclient'][client_id]['client_secret']

    if 1 == 1 :
        print "To be able to request authorization from your users by email, you need to authorize this program to use Google's email resender in your name.  Visit this url and follow the directions:"
        print '  %s' % GeneratePermissionUrl(client_id, scope)
        authorization_code = raw_input('Enter verification code: ')
        response = AuthorizeTokens(client_id, client_secret, authorization_code)
        access_token = response['access_token']
        refresh_token = response['refresh_token']
        
        print 'Access Token: %s' % response['access_token']
        print 'Refresh Token: %s' % response['refresh_token']
        print 'Access Token Expiration Seconds: %s' % response['expires_in']
        
    else :
        refresh_token = '1/ikIx-rOnLcPMD3kbiNiHer0qU1DNxErbSAvknsitaZA'
        access_token = 'ya29.AHES6ZS_iGGgo_qdyrJT2KW3RhnXgUkwVmnKeu_qbPNU5TqJlGh7lA'

        
    if 1 == 1 :
        print "Temporary token.................."   
        auth_string = GenerateOAuth2String(client_email, access_token, base64_encode=False)
        '''
        print 'Auth string: %s' % auth_string
        TestSmtpAuthentication(client_email, auth_string)
        '''
                
        print "That's that ....................."   

        message = 'From: %s\nTo: %s\nSubject: %s\n\n%s' % (client_email, client_email, 'Trash this email', 'just a test')
        print message

        smtp_conn = smtplib.SMTP('smtp.gmail.com', 587)
        smtp_conn.set_debuglevel(False)
        smtp_conn.ehlo('test')
        smtp_conn.starttls()
        try :
        
            smtp_conn.docmd('AUTH', 'XOAUTH2 ' + base64.b64encode(auth_string))
            print 'sending'
            smtp_conn.sendmail(client_email, client_email, message)
            print 'sent'
            
        except smtplib.SMTPSenderRefused as sr :
            if sr[0] == 530 :
                print 'Refresh required'
                access_token = RefreshToken(client_id, client_secret, refresh_token)
                print 'New token : %s'.format(access_token)
                smtp_conn.docmd('AUTH', 'XOAUTH2 ' + base64.b64encode(auth_string))
                smtp_conn.sendmail(client_email, client_email, message)
                    
        
    '''
    print '\n\n * * * * Paste these two lines into your test_parms file'
    print "google_project_client_smtp_access_token = '%s'" % access_token
    print "google_project_client_smtp_refresh_token = '%s'" % refresh_token
    '''
    
    update_parms_file(access_token, refresh_token)
    creds['gclient'][client_id]['smtp_access_token'] = access_token
    creds['gclient'][client_id]['smtp_refresh_token'] = refresh_token
        
    return creds

def prep_creds() :

    redirect_uri = google_project_redirect_uri
    client_secret = google_project_client_secret
    client_id = google_project_client_id
    client_email = google_project_client_email

    
    now = {}
    now['client_id'] = client_id

    gclient = {}
    gclient[client_id] = {}
    gclient[client_id]['redirect_uri'] = redirect_uri
    gclient[client_id]['client_secret'] = client_secret
    gclient[client_id]['client_email'] = client_email
    
    if not configure_email :
        smtp_access_token = google_project_client_smtp_access_token
        smtp_refresh_token = google_project_client_smtp_refresh_token
        
        gclient[client_id]['smtp_access_token'] = smtp_access_token
        gclient[client_id]['smtp_refresh_token'] = smtp_refresh_token
    
    creds = {}
    creds['now'] = now
    creds['gclient'] = gclient
        
    return creds

    
def main(stage):

    oauth_credentials = prep_creds()
    
    print 'Doing stage : {}'.format(stage)
    if stage == CLEAN :
        print 'Deleting "shelve" file {}'.format(store_path)
        silentremove(store_path)
        exit(0)
        
    if configure_email :
        print 'Getting Google SMTP authorization'
        oauth_credentials = prep_smtp(oauth_credentials)
        
    if not os.path.exists(log_file_path) :
        os.makedirs(log_file_path)
    logging.basicConfig(filename=log_file_path + '/' + log_file_name,level=logging.DEBUG)

    logging.debug(' -      -      -      -      -      -      -      ')
    
    client_id = oauth_credentials['now']['client_id']
    
    idxUser = 0
    try :
        idxUser = sys.argv[2]
    except :
        pass
        
    this_user = users[idxUser]
    user_id = this_user['user_email']
    method = this_user['auth_method']
    spreadsheet_key = this_user['workbook_key']
        
    oauth_credentials['now']['user_id'] = user_id
    oauth_credentials['now']['debug'] = (stage == EXPIRED)
    
    logging.info(' -- Working with :\n      User : %s\n  Workbook : %s' % (oauth_credentials['now']['user_id'], spreadsheet_key))

    method_title = {'InstalledApp' : 'an installed application', 'ForDevices' : 'a device', 'ToBeDropped' : 'removed from database'}
    
    '''
    if stage == REQUEST :
    
        user = {}
        user[user_id] = {}
        user[user_id][client_id] = {}

        print '* * * * test_gOAuth.py\n* * * *    User "{}" must authorize the project client "{}"\n* * * *       as "{}", as described here : https://developers.google.com/accounts/docs/OAuth2{}.'.format(user_id, client_id, method_title[method], method)
        
        user[user_id][client_id]['access_token'] = None
        user[user_id][client_id]['refresh_token'] = None
        user[user_id][client_id]['auth_method'] = method

        oauth_credentials['user'] = user

    else :
    '''
    user = {}
    user[user_id] = {}
    user[user_id][client_id] = {}

    print '* * * * test_gOAuth.py\n* * * *    User "{}" must authorize the project client "{}"\n* * * *       as "{}", as described here : https://developers.google.com/accounts/docs/OAuth2{}.'.format(user_id, client_id, method_title[method], method)
    
    user[user_id][client_id]['auth_method'] = method

    oauth_credentials['user'] = user

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
    update_parms_file('aaaaaaaaaaaaaaaa', 'rrrrrrrrrrrrrrrrrr')
    exit(0)

    print f(1)
    print f(2)
    print f(7)
    print f(5)
    exit(0)
    '''
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
            exit(0)
            
    print msg
    for user in users :
        print '        -- "%s" is %s' % (USER, user)


