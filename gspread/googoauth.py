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
       This module contains routines for OAuth usage of "gspread".


'''
import os
import time
import shelve
import urllib, urllib2

import logging
import inspect

import json

import base64
import smtplib

from .exceptions import InvalidUserClientMapping

# from oauth2 import 
from goauth2_helper import GeneratePermissionUrl, AuthorizeTokens, RefreshToken, GenerateOAuth2String

SCOPE = 'https://spreadsheets.google.com/feeds/'

# This the Google OAuth client project authorized to access users data, which we are currently using.
theCurrentOAuthClient = '' 
theCurrentEndUser = '' 

# This is the shelve file where our OAuth arguments persist between executions 
store = {}
store_file = '.tknStore.db'
store_path = os.path.expanduser('~') + '/' + store_file

log_file_name = 'gOAuth.log'
log_file_path = './logs'
store_file = '.tknStore.db'
store_path = os.path.expanduser('~') + '/' + store_file

def close_store():
    """ Remove the 'shelve' daemon from memory.
    """
    if store :
        store.close()

def make_store():
    """ Create a 'shelve' repository.
    """
    global store
    store = shelve.open(store_path, writeback = True)
    

def sanity_check(credentials):

    global theCurrentOAuthClient
    global theCurrentEndUser

    if not store :
        make_store()

    if not os.path.exists(log_file_path) :
        os.makedirs(log_file_path)
    logging.basicConfig(filename=log_file_path + '/' + log_file_name,level=logging.DEBUG)

    logging.debug(' -      -      -      -      -      -      -      ')

    '''
    print '\n\n  =    =    =    =    Credentials    =    =    =    =    =    =    =  '
    pretty(credentials)
    print '  .    .    .    .    .    .  Store  .    .    .    .    .    .    .    .  '
    pretty(store)
    print '  =    =    =    =    =    =    =    =    =    =    =    =    =    =  \n\n'
    '''
    
    logging.debug('\n\n  =    =    =    =    =    =    =    =    =    =    =    =    =    =  ')
    logging.debug('{}.{}()\n\nDump credentials :\n{} \n\nDump store : \n\n{}'
                                    .format(__name__, inspect.stack()[0][3], credentials, store))
    logging.debug('  =    =    =    =    =    =    =    =    =    =    =    =    =    =  \n\n')

    assert hasattr(credentials, 'now')
    assert hasattr(credentials.now, 'client_id')
    assert hasattr(credentials.now, 'user_id')

    theCurrentOAuthClient = credentials.now.client_id
    theCurrentEndUser = credentials.now.user_id
    
    if theCurrentEndUser in credentials.user :
        if theCurrentOAuthClient in credentials.user[theCurrentEndUser] :
            if hasattr(credentials.user[theCurrentEndUser][theCurrentOAuthClient], 'auth_method') :
                if credentials.user[theCurrentEndUser][theCurrentOAuthClient].auth_method == 'ToBeDropped' :
                    dropUserConnection()
                    return
                                
    if theCurrentOAuthClient in store :
        for key in ['redirect_uri', 'client_secret', 'client_email'] :
            if hasattr(credentials.gclient[theCurrentOAuthClient], key) :
                setattr(store[theCurrentOAuthClient], key, getattr(credentials.gclient[theCurrentOAuthClient], key))
            else:
                assert key in store[theCurrentOAuthClient]

        if theCurrentEndUser in store :
            if theCurrentOAuthClient in store[theCurrentEndUser] :
                if hasattr( store[theCurrentEndUser][theCurrentOAuthClient], 'refresh_token' ) :
                    if store[theCurrentEndUser][theCurrentOAuthClient].refresh_token is not None :
                        if len(store[theCurrentEndUser][theCurrentOAuthClient].refresh_token) > 0 :
                            assert len(store[theCurrentEndUser][theCurrentOAuthClient].refresh_token) == 45
                            return

    else :
        assert hasattr(credentials, 'gclient')
        assert theCurrentOAuthClient in credentials.gclient
        assert hasattr(credentials.gclient[theCurrentOAuthClient], 'client_secret')
    
                
    assert hasattr(credentials.gclient[theCurrentOAuthClient], 'redirect_uri')
    assert hasattr(credentials.gclient[theCurrentOAuthClient], 'client_secret')
    return


class NameSpace(object):
  def __init__(self, adict):
    self.__dict__.update(adict)

    
def request_approval(args) :

    client_id = args['client_id']
    client_email = args['client_email']
    client_secret = args['client_secret']
    
    if store[theCurrentOAuthClient].smtp_access_token is None :
        prep_smtp(args)

    # print "Temporary token using %s and %s ."   %  (client_email, store[theCurrentOAuthClient].smtp_access_token)
    auth_string = GenerateOAuth2String(client_email, store[theCurrentOAuthClient].smtp_access_token)
            
    message = 'From: %s\nTo: %s\nSubject: %s\n\n%s' % (client_email, args['user'], args['subject'], args['text'])
#    print message

    smtp_conn = smtplib.SMTP('smtp.gmail.com', 587)
    smtp_conn.set_debuglevel(False)
    smtp_conn.ehlo('test')
    smtp_conn.starttls()
    
    smtp_conn.docmd('AUTH', 'XOAUTH2 ' + auth_string)
    print 'Sending . . . '
    smtp_conn.sendmail(client_email, args['user'], message)
    print ' . . sent!'
    
    smtp_conn.close()


def pretty(dictionary, indent = 0):

    dctnry = dictionary

    if 'NameSpace' in '{}'.format(type(dctnry)) :
            dctnry = vars(dictionary)

    for key, value in dctnry.iteritems():
        txt = '.  ' * indent + str(key) + ' : '
        if isinstance(value, dict) or 'NameSpace' in '{}'.format(type(value)) :
            print txt
            pretty(value, indent + 1)
            if indent == 0 : print '\n'
        else:
            print txt + str(value)

def erase_access_token(credentials):

    logging.warn('Invalidate useless access token')

    sanity_check(credentials)
    
    logging.debug(
       'Killing record "{}" for "{}"'.format(
              theCurrentOAuthClient
            , theCurrentEndUser
            )
       )
       
       
    assert hasattr(store[theCurrentEndUser][theCurrentOAuthClient], 'access_token')
    
    del store[theCurrentEndUser][theCurrentOAuthClient].access_token
    
    
def get_auth_tokens(credentials):
    
    sanity_check(credentials)
    
    if theCurrentOAuthClient not in store :
        store[theCurrentOAuthClient] = credentials.gclient[theCurrentOAuthClient]
    else :
        if theCurrentEndUser in store:
            if hasattr(store[theCurrentEndUser][theCurrentOAuthClient], 'access_token' ) :
                logging.debug(store[theCurrentEndUser][theCurrentOAuthClient])
                if store[theCurrentEndUser][theCurrentOAuthClient].access_token :
                    if hasattr(credentials.now, 'debug') :
                        if credentials.now.debug :
                            store[theCurrentEndUser][theCurrentOAuthClient].access_token = 'deliberately corrupted to test token refresh'
                            print 'DEBUG: Testing refresh.'
                    return store[theCurrentEndUser][theCurrentOAuthClient]

            logging.warn('No access token available.')
            if hasattr(store[theCurrentEndUser][theCurrentOAuthClient], 'refresh_token'):
                refresh_token = store[theCurrentEndUser][theCurrentOAuthClient].refresh_token
                if refresh_token :
                    logging.debug('Trying to refresh the access token.')
                    return refreshToken()

#    if theCurrentEndUser not in store:
    store[theCurrentEndUser] = credentials.user[theCurrentEndUser]
            
    print 'Need to get a new access token.'
    
    if getGDataTokens() :
    
        logging.debug('We have token {}'.format(store[theCurrentEndUser][theCurrentOAuthClient].access_token))
        return store[theCurrentEndUser][theCurrentOAuthClient]
    
    return False
    
    
def dropUserConnection() :
    print 'Requesting to drop "%s"' % theCurrentOAuthClient
    if theCurrentEndUser in store :
        if theCurrentOAuthClient in store[theCurrentEndUser] :
            del store[theCurrentEndUser][theCurrentOAuthClient]
            print 'Dropped %s connection for %s.' % (theCurrentOAuthClient, theCurrentEndUser)

            if len(store[theCurrentEndUser]) < 1 :
                del store[theCurrentEndUser]
                
            print 'Dropped theCurrentEndUser %s' % (theCurrentEndUser)
            return
        
        print '%s connection for %s already dropped or never added.' % (theCurrentOAuthClient, theCurrentEndUser)
        
    print '%s already dropped or never added.' % (theCurrentEndUser)
    close_store()
    raise InvalidUserClientMapping("User %s no longer authorizes %s." % (theCurrentEndUser, theCurrentOAuthClient))
    

def prepareAsForDevices() :

    m = 'ForDevices'

    client_email = store[theCurrentOAuthClient].client_email
    client_secret = store[theCurrentOAuthClient].client_secret

    print 'Requesting as device for "%s"' % theCurrentOAuthClient

    data = {}
    data['client_id'] = theCurrentOAuthClient # 	the client_id obtained from the APIs Console 	Indicates the client that is making the request. The value passed in this parameter must exactly match the value shown in the APIs Console.
    
    data['scope'] = SCOPE  # Indicates the Google API access your application is requesting. The values passed in this parameter inform the consent page shown to the user. There is an inverse relationship between the number of permissions requested and the likelihood of obtaining user consent.
    
    url = 'https://accounts.google.com/o/oauth2/device/code'
    parms = urllib.urlencode(data)

    request = urllib2.Request (url, parms)

    theJSON = json.loads(urllib2.urlopen(request).read())
    logging.debug('Response as json : {}.'.format(theJSON))

    verification_url = theJSON['verification_url']
    user_code = theJSON['user_code']
    expiry = int(theJSON['expires_in'])
    device_code = theJSON['device_code']
    
    subject = '%s wants permission to access your Google Spreadheets with "gspread".' % client_email
    text = 'To give {} access to your spreadsheets, please copy this code [ {} ] to your clipboard, turn to {} and enter it in the field provided. You have {} minutes to do so.'.format(client_email, user_code, verification_url, expiry / 60)
    
    pckg = {}
    pckg['user'] = theCurrentEndUser
    pckg['text'] = text
    pckg['expiry'] = expiry
    pckg['subject'] = subject
    pckg['client_id'] = theCurrentOAuthClient
    pckg['user_code'] = user_code
    pckg['device_code'] = device_code
    pckg['client_email'] = store[theCurrentOAuthClient].client_email
    pckg['client_secret'] = store[theCurrentOAuthClient].client_secret
    pckg['verification_url'] = verification_url

    return pckg
    
    

def getAsForDevices(rq) :
    m = 'ForDevices'

    client = rq['client_id']

    # print 'Getting authorization for device for "%s"' % client

    subject = '%s wants permission to access your Google Spreadheets with "gspread".' % rq['client_email']
    
    print "\n\n* * * * *  You have to verify that you DO allow this software to open your Google document space."
    print     '* * * * *  Please check your email at %s.' % rq['user']
    print     '* * * * *  The message "%s" contains further instructions for you.' % subject

    data = {}

    data['client_id'] = client
    data['client_secret'] = rq['client_secret']
    data['code'] = rq['device_code']
    data['grant_type'] = 'http://oauth.net/grant_type/device/1.0'
    
    url = 'https://accounts.google.com/o/oauth2/token'
    
    parms = urllib.urlencode(data)

    request = urllib2.Request (url, parms)

    delay = 30
    triesLimit = rq['expiry'] / delay
    tries = triesLimit
    while tries > 0 :
    
        theJSON = json.loads(urllib2.urlopen(request).read())
        logging.debug('Response as json : {}.'.format(theJSON))

        if 'access_token' in theJSON :
            print ' * * * Authorized ! * * * '
            store[theCurrentEndUser][theCurrentOAuthClient].access_token = theJSON['access_token']
            store[theCurrentEndUser][theCurrentOAuthClient].refresh_token = theJSON['refresh_token']
            store[theCurrentEndUser][theCurrentOAuthClient].auth_method = m

            logging.debug(
                    '==>\nAccess token : {}\nRefresh token : {}'.format(
                        store[theCurrentEndUser][theCurrentOAuthClient].access_token
                      , store[theCurrentEndUser][theCurrentOAuthClient].refresh_token
                    )
            )
            
            return
            
        elif 'error' in theJSON :
            if tries < triesLimit :
                time.sleep(delay)
                print 'Trying again to get tokens.  {} tries remain.'.format(tries)
        else :
            print ' * * *  Uh oh ! * * * %s ' % theJSON
            
        tries -= 1
        
    print "Too late.  You'll have to repeat it all."
    exit(-1)    
    
def prepareAsInstalledApp() :
    m = 'InstalledApp'
    client_email = store[theCurrentOAuthClient].client_email
    client_secret = store[theCurrentOAuthClient].client_secret
    redirect_uri = store[theCurrentOAuthClient].redirect_uri
    
    print 'Requesting as "%s" for "%s"' % (m, theCurrentOAuthClient)
    
    data = {}
    data['response_type'] = 'code' # Determines if the Google OAuth 2.0 endpoint returns an authorization code. For installed applications, a value of code should be used.
    
    data['redirect_uri'] = redirect_uri # one of the redirect_uri values registered at the APIs Console 	Determines where the response is sent. The value of this parameter must exactly match one of the values registered in the APIs Console (including the http or https schemes, case, and trailing '/'). You may choose between urn:ietf:wg:oauth:2.0:oob or an http://localhost port. See choosing a redirect_uri for more details.

    data['client_id'] = theCurrentOAuthClient # 	the client_id obtained from the APIs Console 	Indicates the client that is making the request. The value passed in this parameter must exactly match the value shown in the APIs Console.
    
    data['scope'] = SCOPE  # Indicates the Google API access your application is requesting. The values passed in this parameter inform the consent page shown to the user. There is an inverse relationship between the number of permissions requested and the likelihood of obtaining user consent.
    

    data['state'] = "I'm in SUCH a state!" # Indicates any state which may be useful to your application upon receipt of the response. The Google Authorization Server roundtrips this parameter, so your application receives the same value it sent.
    
    data['login_hint'] = '** ' + theCurrentEndUser + ' **' # When your application knows which user it is trying to authenticate, it may provide this parameter as a hint to the Authentication Server. Passing this hint will either pre-fill the email box on the sign-in form or select the proper multi-login session, thereby simplifying the login flow. 

    
    url = 'https://accounts.google.com/o/oauth2/auth'   
    parms = urllib.urlencode(data)

    verification_url = '%s?%s' % (url, parms)

    subject = '%s wants permission to access your Google Spreadheets with "gspread".' % client_email
    text = 'To give {} programmatic access to your spreadsheets, please click on the lick below, agree to the access authorization, copy the presented validation code to your clipboard and then paste it into the waiting program you launched for the purpose a few moments ago.\n\n The authorization link :\n {}'.format(client_email, verification_url)
    
#    print 'Email text : %s' % text
    store[theCurrentOAuthClient].client_id = theCurrentOAuthClient
    
    pckg = {}
    pckg['user'] = theCurrentEndUser
    pckg['text'] = text
    pckg['subject'] = subject
    pckg['client_id'] = theCurrentOAuthClient
    pckg['redirect_uri'] = redirect_uri
    pckg['client_email'] = store[theCurrentOAuthClient].client_email
    pckg['client_secret'] = store[theCurrentOAuthClient].client_secret
    pckg['verification_url'] = verification_url

    return pckg
    

def getAsInstalledApp(rq) :
    m = 'InstalledApp'
    
    client = rq['client_id']
    
    print "\n\n* * * * *  You have to verify that you DO allow this software to open your Google document space."
    print     '* * * * *  Please check your email at %s.' % rq['user']
    print     '* * * * *  The message "%s" contains further instructions for you.' % rq['subject']

    print "\n\n* * * * *         Here's the URL at which you can pick up your 'one-time' verification code, which was sent to your email account.       * * * * * "
    print '\n\n%s\n\n' % rq['verification_url']
    code = raw_input('\nPaste that code here, now . . , then hit <Enter> ').strip()
    
    data = {}
    
    data['code'] = code  # The authorization code returned from the initial request
    data['redirect_uri'] = rq['redirect_uri']  # The URI registered with the application
    data['grant_type'] = 'authorization_code'
    data['client_secret'] = rq['client_secret']
    data['client_id'] = client

    url = 'https://accounts.google.com/o/oauth2/token'
    parms = urllib.urlencode(data)
    
    logging.debug('Obtaining token pair with : {}?{}'.format(url, parms))
    
    theJSON = json.loads(urllib2.urlopen(urllib2.Request (url, parms)).read())
    logging.debug('Response as json : {}.'.format(theJSON))

    store[theCurrentEndUser][theCurrentOAuthClient].access_token = theJSON['access_token']
    store[theCurrentEndUser][theCurrentOAuthClient].refresh_token = theJSON['refresh_token']
    store[theCurrentEndUser][theCurrentOAuthClient].auth_method = m

    
    logging.debug(
            '==>\nAccess token : {}\nRefresh token : {}'.format(
                  store[theCurrentEndUser][theCurrentOAuthClient].access_token 
                , store[theCurrentEndUser][theCurrentOAuthClient].refresh_token

            )
    )

    return
    

def getGDataTokens() :

    logging.debug(' - - - - - - - ')
    logging.debug(store[theCurrentOAuthClient])
    logging.debug(' - - - - - - - ')

    try :
        method = store[theCurrentEndUser][theCurrentOAuthClient].auth_method
        if method not in ['ForDevices', 'InstalledApp'] :
            close_store()
            raise InvalidUserClientMapping("User %s no longer authorizes %s." % (theCurrentEndUser, theCurrentOAuthClient))
            
    except KeyError as ke :
        print "Uh oh <<{%s}>>" % ke

    # calling either "prepareAsInstalledApp(user, theCurrentOAuthClient, store)"  
    #             or "prepareAsForDevices(user, theCurrentOAuthClient, store)"  
    #    as indicated by "auth_method"
    req = globals()['prepareAs%s' % method]()
#     pretty (req)
    
    sending = True
    while sending :
        try :
        
            request_approval(req)
            sending = False
            
        except smtplib.SMTPSenderRefused as sr :

            if sr[0] == 530 :
                client_secret = store[theCurrentOAuthClient].client_secret
                smtp_refresh_token = store[theCurrentOAuthClient].smtp_refresh_token
                if 'Authentication Required' in sr[1] :
#                    print "  *    *   Do we get an 'invalid grant' error now ?   *    *    * "
                    pass
                    
#                print 'Refresh required: %s ' % smtp_refresh_token
#                print 'Client ID: %s, Secret: %s ' % (theCurrentOAuthClient, client_secret)

                rslt = RefreshToken(
                      theCurrentOAuthClient
                    , client_secret
                    , smtp_refresh_token
                )
                if 'error' in rslt :
                    close_store()
                    raise Exception("Cannot refresh invalid SMTP token. '%s' " % rslt['error'])
                    
                store[theCurrentOAuthClient].smtp_access_token = rslt['access_token']
                req['smtp_access_token'] = store[theCurrentOAuthClient].smtp_access_token
                print 'New SMTP token : %s' % store[theCurrentOAuthClient].smtp_access_token

    # calling either "getAsInstalledApp(user, client, store)"  
    #             or "getAsForDevices(user, client, store)"  
    #    as indicated by "auth_method"
    globals()['getAs%s' % method](req)
    return True
    
def refreshToken():

    result = {}
    assert theCurrentEndUser in store
    assert theCurrentOAuthClient in store
    assert theCurrentOAuthClient in store[theCurrentEndUser]
    assert hasattr(store[theCurrentOAuthClient], 'client_secret')
    
    token = store[theCurrentEndUser][theCurrentOAuthClient].refresh_token
    secret = store[theCurrentOAuthClient].client_secret
    url = "https://accounts.google.com/o/oauth2/token"
    
    logging.debug('Refresh the authorization {} gave to {} with token : {}.'.format(
                                      theCurrentEndUser
                                    , theCurrentOAuthClient
                                    , token))
    
    data = {}
    data['grant_type'] = 'refresh_token'
    data['client_secret'] = secret
    data['refresh_token'] = token
    data['client_id'] = theCurrentOAuthClient

    parms = urllib.urlencode(data)
    logging.debug('Calling {} with : {}.'.format(url, parms))
    request = urllib2.Request (url, parms)
        
    store[theCurrentEndUser][theCurrentOAuthClient].access_token = json.loads(
                                                    urllib2.urlopen(request).read()
                                                )['access_token']
    logging.debug('Refreshed access token : {}.'.format(store[theCurrentEndUser][theCurrentOAuthClient].access_token))

    result['refresh_token'] = token
    result['access_token'] = store[theCurrentEndUser][theCurrentOAuthClient].access_token
    return NameSpace(result)

def prep_creds(
                  nickname
                , users
                , client_id
                , client_secret
                , redirect_uri
                , client_email
                , smtp_access_token
                , smtp_refresh_token
              ) :

    """Set up a credentials Value Object.

    This is a helper function which prepares a dictionary of the OAuth2
    credential values that will be needed to initiate a gspread Client 
    connection.
    
    'users' is a dict of dicts of user profiles selected by a nickname.
    
    See test_parms.py.example for an example
    
    The returned 'credentials' object contains a many to many mapping 
    between possible users and possible project "Clients" as defined in
    the "Google API Console".
    
    The 'now' element facilitates keeping track of which user and which
    client are to be used in the current execution.
    
    Thus, the current access_token can be obtained with 
    
    credentials.[credentials.now['user_id']][credentials.now['client_id']].access_token

    :returns: :class:`NameSpace` instance.

    """
            
    current_user = NameSpace(users[nickname])
    
    now =       NameSpace({
                      'debug': False
                    , 'user_id' : current_user.user_email
                    , 'client_id' : client_id
                })
                

    client = NameSpace({
                  'client_secret' : client_secret
                , 'redirect_uri' : redirect_uri
                , 'client_email' : client_email
                , 'smtp_access_token' : smtp_access_token
                , 'smtp_refresh_token' : smtp_refresh_token

            })
            
    gclient =   { client_id : client }

    client_user = {
                    client_id : NameSpace({
                                     'auth_method': current_user.auth_method
                                   , 'access_token': ''
                                   , 'refresh_token': ''
                                })
                  }

    user = {current_user.user_email : client_user }
    credentials = NameSpace({'gclient': gclient, 'user' : user, 'now' : now})

    
    return credentials

    
    
'''
Data structure
..............

The point of the datastructure is to allow you to keep track of multiple projects with multiple end-users.

Each project has a unique "Client ID for installed applications", as managed here : https://code.google.com/apis/console in the sub-section "API Access".  

Each end-user may allow access to multiple projects.  You will communicate with them by email, which will pass through your GMail account. 

You will use OAuth to allow this program to use your email without you needing to give it your password.

Storage is handled as a dictionary in a file by the micro-database manager "shelve".

Data for each distinct execution of this software is expected in a similar data structure

The structure is :

some.user@gmail.com : 
.  204618981389--Some_Client_ID_.apps.googleusercontent.com : 
.  .  access_token : ya29.AHES6ZxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxoILBCQA
.  .  auth_method : InstalledApp
.  .  refresh_token : 1/qz2th667xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxnpYLQ


some.other.user.com : 
.  204618981389--Some_Client_ID_.apps.googleusercontent.com : 
.  .  access_token : ya29.AHES6ZxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxTiR1DQAoLSZOZyn
.  .  auth_method : ForDevices
.  .  refresh_token : 1/rZpXLbxxxxxxxxxxxxxxxxxxxxxxxxxxmkpXz3se2lc


204618981389--Some_Client_ID_.apps.googleusercontent.com : 
.  smtp_refresh_token : 1/o1Yxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxolm8Po
.  smtp_access_token : ya29.AHES6Zxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx9xOQO3P8
.  redirect_uri : urn:ietf:wg:oauth:2.0:oob
.  client_email : your.account@gmail.com
.  client_id : 204618981389--Some_Client_ID_.apps.googleusercontent.com
.  client_secret : Zis38NZ_wyBII2Q9xfMRthW-


'''
