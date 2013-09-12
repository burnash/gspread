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
import time
import shelve
import urllib, urllib2

import logging
import inspect

import json

import base64
import smtplib
from oauth2 import GeneratePermissionUrl, AuthorizeTokens, RefreshToken, GenerateOAuth2String

SCOPE = 'https://spreadsheets.google.com/feeds/'


def sanity_check(credentials, store):

    print '\n\n  =    =    =    =    Credentials    =    =    =    =    =    =    =  '
    pretty(credentials)
    print '  .    .    .    .    .    .  Store  .    .    .    .    .    .    .    .  '
    pretty(store)
    print '  =    =    =    =    =    =    =    =    =    =    =    =    =    =  \n\n'

    logging.debug('\n\n  =    =    =    =    =    =    =    =    =    =    =    =    =    =  ')
    logging.debug('{}.{}()\n\nDump credentials :\n{} \n\nDump store : \n\n{}'
                                    .format(__name__, inspect.stack()[0][3], credentials, store))
    logging.debug('  =    =    =    =    =    =    =    =    =    =    =    =    =    =  \n\n')

    assert 'now' in credentials
    assert 'client_id' in credentials['now']
    assert 'user_id' in credentials['now']

    clientId = credentials['now']['client_id']
    userId = credentials['now']['user_id']
    
    if userId in credentials['user'] :
        if clientId in credentials['user'][userId] :
            if 'auth_method' in credentials['user'][userId][clientId] :
                if credentials['user'][userId][clientId]['auth_method'] == 'ToBeDropped' :
                    dropUserConnection(userId, clientId, store)
                    exit(0)
                                
    if clientId in store :
        assert 'redirect_uri' in store[clientId]
        assert 'client_secret' in store[clientId]
        assert 'client_email' in store[clientId]
        assert 'smtp_access_token' in store[clientId]
        assert 'smtp_refresh_token' in store[clientId]
        
        if userId in store :
            if clientId in store[userId] :
                assert 'auth_method' in store[userId][clientId]
                if 'refresh_token' in store[userId][clientId] :
                    if store[userId][clientId]['refresh_token'] is not None :
                        assert len(store[userId][clientId]['refresh_token']) == 45
                        return

    else :
        assert 'gclient' in credentials
        assert clientId in credentials['gclient']
        assert 'client_secret' in credentials['gclient'][clientId]
    
                
    assert 'redirect_uri' in credentials['gclient'][clientId]
    assert 'client_secret' in credentials['gclient'][clientId]
    return
    
# def request_approval(args, user, subject, text) :
def request_approval(args) :

    client_id = args['client_id']
    client_email = args['client_email']
    client_secret = args['client_secret']
    access_token = args['smtp_access_token']
    refresh_token = args['smtp_refresh_token']
    
    print "Temporary token.................."   
    auth_string = GenerateOAuth2String(client_email, access_token)
            
    print "That's that ....................."   
    message = 'From: %s\nTo: %s\nSubject: %s\n\n%s' % (client_email, args['user'], args['subject'], args['text'])
    print message

    smtp_conn = smtplib.SMTP('smtp.gmail.com', 587)
    smtp_conn.set_debuglevel(False)
    smtp_conn.ehlo('test')
    smtp_conn.starttls()
    
    smtp_conn.docmd('AUTH', 'XOAUTH2 ' + auth_string)
    print 'sending'
    smtp_conn.sendmail(client_email, args['user'], message)
    print 'sent'
    
    smtp_conn.close()

def pretty(dictionary, indent=0):
   for key, value in dictionary.iteritems():
      txt = '.  ' * indent + str(key) + ' : '
      if isinstance(value, dict):
         print txt
         pretty(value, indent+1)
         if indent == 0 : print '\n'
      else:
         print txt + str(value)


def erase_access_token(credentials, store):
    sanity_check(credentials, store)
    
    logging.debug(
       'Killing record "{}" for "{}"'.format(
              credentials['now']['user_id']
            , credentials['now']['client_id']
            )
       )
    assert credentials['now']['user_id'] in store
    assert credentials['now']['client_id'] in store[credentials['now']['user_id']]
    assert 'access_token' in store[credentials['now']['user_id']][credentials['now']['client_id']]
    
    del store[credentials['now']['user_id']][credentials['now']['client_id']]['access_token']
    
    
def get_auth_tokens(credentials, store):

    sanity_check(credentials, store)
    
    clientId = credentials['now']['client_id']
    userId = credentials['now']['user_id']

    if clientId not in store :
        store[clientId] = credentials['gclient'][clientId]
    else :
        if userId in store:
            if 'access_token' in store[userId][clientId]:
                logging.debug(store[userId][clientId])
                if store[userId][clientId]['access_token'] :
                    if 'debug' in credentials['now'] :
                        if credentials['now']['debug'] :
                            store[userId][clientId]['access_token'] = 'corrupted to test token refresh'
                            print 'DEBUG: Testing refresh.'
                    return store[userId][clientId]

            logging.warn('No access token available.')
            if 'refresh_token' in store[userId][clientId]:
                refresh_token = store[userId][clientId]['refresh_token']
                if refresh_token :
                    logging.debug('Trying to refresh the access token.')
                    return refreshToken(credentials, store)
    if userId not in store:
        store[userId] = credentials['user'][userId]
            
    print 'Need to get a new access token.'
    
#    store[clientId]['client_id'] = clientId
#    store[userId] = getGDataTokens(store[clientId])

    store[userId] = getGDataTokens(userId, clientId, store)
    
    logging.debug('We have token {}'.format(store[userId][clientId]['access_token']))
    return store[userId][clientId]
    
    
def dropUserConnection(user, client, store) :
    print 'Requesting to drop "%s"' % client
    if user not in store :
        print '%s already dropped or never added.' % (user)
        exit(0)
    else :    
        if client not in store[user] :
            print '%s connection for %s already dropped or never added.' % (client, user)
        else :
            del store[user][client]
            print 'Dropped %s connection for %s.' % (client, user)
            
    if len(store[user]) < 1 :
        del store[user]

    print 'Dropped user %s' % (user)
    exit(0)
    

def prepareAsForDevices(user, client, user_args) :
    m = 'ForDevices'
    client_email = user_args['client_email']
    client_secret = user_args['client_secret']

    print 'Requesting as device for "%s"' % client

    data = {}
    data['client_id'] = client # 	the client_id obtained from the APIs Console 	Indicates the client that is making the request. The value passed in this parameter must exactly match the value shown in the APIs Console.
    
    data['scope'] = SCOPE  # Indicates the Google API access your application is requesting. The values passed in this parameter inform the consent page shown to the user. There is an inverse relationship between the number of permissions requested and the likelihood of obtaining user consent.
    
    url = 'https://accounts.google.com/o/oauth2/device/code'
    parms = urllib.urlencode(data)

    request = urllib2.Request (url, parms)
    print 'Obtaining request code and URL with %s.' % request

    theJSON = json.loads(urllib2.urlopen(request).read())
    logging.debug('Response as json : {}.'.format(theJSON))

    verification_url = theJSON['verification_url']
    user_code = theJSON['user_code']
    expiry = int(theJSON['expires_in'])
    device_code = theJSON['device_code']
    
    subject = '%s wants permission to access your Google Spreadheets with "gspread".' % client_email
    text = 'To give {} access to your spreadsheets, please copy this code [ {} ] to your clipboard, turn to {} and enter it in the field provided. You have {} minutes to do so.'.format(client_email, user_code, verification_url, expiry / 60)
    
    pckg = {}
    pckg['user'] = user
    pckg['text'] = text
    pckg['expiry'] = expiry
    pckg['subject'] = subject
    pckg['client_id'] = client
    pckg['user_code'] = user_code
    pckg['device_code'] = device_code
    pckg['client_email'] = user_args['client_email']
    pckg['client_secret'] = user_args['client_secret']
    pckg['verification_url'] = verification_url
    pckg['smtp_access_token'] = user_args['smtp_access_token']
    pckg['smtp_refresh_token'] = user_args['smtp_refresh_token']

    return pckg
        
    exit(-1)    
    
    

def getAsForDevices(rq, store) :
    m = 'ForDevices'
    print '   getAs%s(rq, store) ' % m

    client = rq['client_id']

    print 'Requesting as device for "%s"' % client

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
    print url
    
    parms = urllib.urlencode(data)
    print parms

    request = urllib2.Request (url, parms)

    delay = 30
    triesLimit = rq['expiry'] / delay
    tries = triesLimit
    while tries > 0 :
    
        theJSON = json.loads(urllib2.urlopen(request).read())
        logging.debug('Response as json : {}.'.format(theJSON))

        if 'access_token' in theJSON :
            print ' * * *  Yayyyy ! * * * '
            user = {}
            user[client] = {}
            user[client]['access_token'] = theJSON['access_token']
            user[client]['refresh_token'] = theJSON['refresh_token']
            user[client]['auth_method'] = m
            
            logging.debug(
                    '==>\nAccess token : {}\nRefresh token : {}'.format(
                        user[client]['access_token']
                      , user[client]['refresh_token']
                    )
            )
            return user
            
        elif 'error' in theJSON :
            if tries < triesLimit :
                time.sleep(delay)
                print 'Trying again to get tokens.  {} tries remain.'.format(tries)
        else :
            print ' * * *  Uh oh ! * * * %s ' % theJSON
            
        tries -= 1
        
    exit(-1)    
    
def prepareAsInstalledApp(user, client, user_args) :
    m = 'InstalledApp'
    client_email = user_args['client_email']
    client_secret = user_args['client_secret']
    redirect_uri = user_args['redirect_uri']
    
    print 'Requesting as "%s" for "%s"' % (m, client)
    
    data = {}
    data['response_type'] = 'code' # Determines if the Google OAuth 2.0 endpoint returns an authorization code. For installed applications, a value of code should be used.
    
    data['redirect_uri'] = redirect_uri # one of the redirect_uri values registered at the APIs Console 	Determines where the response is sent. The value of this parameter must exactly match one of the values registered in the APIs Console (including the http or https schemes, case, and trailing '/'). You may choose between urn:ietf:wg:oauth:2.0:oob or an http://localhost port. See choosing a redirect_uri for more details.

    data['client_id'] = client # 	the client_id obtained from the APIs Console 	Indicates the client that is making the request. The value passed in this parameter must exactly match the value shown in the APIs Console.
    
    data['scope'] = SCOPE  # Indicates the Google API access your application is requesting. The values passed in this parameter inform the consent page shown to the user. There is an inverse relationship between the number of permissions requested and the likelihood of obtaining user consent.
    

    data['state'] = "I'm in SUCH a state!" # Indicates any state which may be useful to your application upon receipt of the response. The Google Authorization Server roundtrips this parameter, so your application receives the same value it sent.
    
    data['login_hint'] = '** ' + user + ' **' # When your application knows which user it is trying to authenticate, it may provide this parameter as a hint to the Authentication Server. Passing this hint will either pre-fill the email box on the sign-in form or select the proper multi-login session, thereby simplifying the login flow. 

    
    url = 'https://accounts.google.com/o/oauth2/auth'   
    print url
    parms = urllib.urlencode(data)
    print parms

    verification_url = '%s?%s' % (url, parms)

    subject = '%s wants permission to access your Google Spreadheets with "gspread".' % client_email
    text = 'To give {} programmatic access to your spreadsheets, please click on the lick below, agree to the access authorization, copy the presented validation code to your clipboard and then paste it into the waiting program you launched for the purpose a few moments ago.\n\n The authorization link :\n {}'.format(client_email, verification_url)
    
#    print 'Email text : %s' % text
    user_args['client_id'] = client
    
    pckg = {}
    pckg['user'] = user
    pckg['text'] = text
    pckg['subject'] = subject
    pckg['client_id'] = client
    pckg['redirect_uri'] = redirect_uri
    pckg['client_email'] = user_args['client_email']
    pckg['client_secret'] = user_args['client_secret']
    pckg['verification_url'] = verification_url
    pckg['smtp_access_token'] = user_args['smtp_access_token']
    pckg['smtp_refresh_token'] = user_args['smtp_refresh_token']

    return pckg
    

def getAsInstalledApp(rq, store) :
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

    user = {}
    user[client] = {}
    user[client]['access_token'] = theJSON['access_token']
    user[client]['refresh_token'] = theJSON['refresh_token']
    user[client]['auth_method'] = m
    
    logging.debug(
            '==>\nAccess token : {}\nRefresh token : {}'.format(
                user[client]['access_token']
              , user[client]['refresh_token']
            )
    )

    return user
    

def getGDataTokens(user, client, store) :

    logging.debug(' - - - - - - - ')
    logging.debug(store[client])
    logging.debug(' - - - - - - - ')

    try :
        method = store[user][client]['auth_method']
    except KeyError as ke :
        print "Uh oh <<{%s}>>" % ke

    # calling either "prepareAsInstalledApp(user, client, store)"  
    #             or "prepareAsForDevices(user, client, store)"  
    #    as indicated by "auth_method"
    req = globals()['prepareAs%s' % method](user, client, store[client])
    pretty (req)
    sending = True
    while sending :
        try :
        
            request_approval(req)
            sending = False
            
        except smtplib.SMTPSenderRefused as sr :
        
            if sr[0] == 530 :
                print 'Refresh required: %s ' % req['smtp_refresh_token']
                print 'Client ID: %s, Secret: %s ' % (req['client_email'], req['client_secret'])
                store[client]['smtp_access_token'] = RefreshToken(
                      req['client_id']
                    , req['client_secret']
                    , req['smtp_refresh_token']
                )['access_token']
                req['smtp_access_token'] = store[client]['smtp_access_token']
                print 'New token : %s' % store[client]['smtp_access_token']

    # calling either "getAsInstalledApp(user, client, store)"  
    #             or "getAsForDevices(user, client, store)"  
    #    as indicated by "auth_method"
    result = globals()['getAs%s' % method](req, store)
    pretty (result)
    
    return result
    
def refreshToken(credentials, store):

    result = {}
    gclient = credentials['now']['client_id']
    assert gclient in store
    assert 'client_secret' in store[gclient]
    

    user = credentials['now']['user_id']
    assert user in store
    assert gclient in store[user]
    
    token = store[user][gclient]['refresh_token']
    secret = store[gclient]['client_secret']
    url = "https://accounts.google.com/o/oauth2/token"
    
    logging.debug('Refresh the authorization {} gave to {} with token : {}.'.format(user, gclient, token))
    
    data = {}
    data['grant_type'] = 'refresh_token'
    data['client_secret'] = secret
    data['refresh_token'] = token
    data['client_id'] = gclient

    parms = urllib.urlencode(data)
    logging.debug('Calling {} with : {}.'.format(url, parms))
    request = urllib2.Request (url, parms)
        
    store[user][gclient]['access_token'] = json.loads(urllib2.urlopen(request).read())['access_token']
    logging.debug('Refreshed access token : {}.'.format(store[user][gclient]['access_token']))

    result['refresh_token'] = token
    result['access_token'] = store[user][gclient]['access_token']
    return result

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

provided['now'] - Contains the data 


'''
