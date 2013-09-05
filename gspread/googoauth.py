#!/usr/bin/env python 
# -*- coding: utf-8 -*-
'''
'''
import shelve
import urllib, urllib2

import logging

import json

def sanity_check(credentials, store):

    assert 'now' in credentials
    assert 'client_id' in credentials['now']
    assert 'user_id' in credentials['now']

    appId = credentials['now']['client_id']
    userId = credentials['now']['user_id']
    
    if appId in store :
        assert 'redirect_uri' in store[appId]
        assert 'client_secret' in store[appId]
        
        if userId in store :
            if appId in store[userId] :
                assert 'refresh_token' in store[userId][appId]
                return
    else :
        assert 'app' in credentials
        assert appId in credentials['app']
        assert 'client_secret' in credentials['app'][appId]
    
                
    assert 'redirect_uri' in credentials['app'][appId]
    assert 'client_secret' in credentials['app'][appId]
    return
    
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
    
    appId = credentials['now']['client_id']
    userId = credentials['now']['user_id']

    if appId not in store :
        store[appId] = credentials['app'][appId]
    else :
        if userId in store:
            if 'access_token' in store[userId][appId]:
                logging.debug(store[userId][appId])
                if store[userId][appId]['access_token'] :
                    if 'debug' in credentials['now'] :
                        if credentials['now']['debug'] :
                            store[userId][appId]['access_token'] = 'corrupted to test token refresh'
                            print 'DEBUG: Testing refresh.'
                    return store[userId][appId]
                
        logging.warn('No access token available.')
        if 'refresh_token' in store[userId][appId]:
            refresh_token = store[userId][appId]['refresh_token']
            if refresh_token :
                logging.debug('Trying to refresh the access token.')
                return refreshToken(credentials, store)
                
    print 'Need to get a new access token.'
    
    store[appId]['client_id'] = appId
    store[userId] = getGDataTokens(store[appId])
    
    logging.debug('We have token {}'.format(store[userId][appId]['access_token']))
    return store[userId][appId]
    
    
def getGDataTokens(credentials) :

    logging.debug(' - - - - - - - ')
    logging.debug(credentials)
    logging.debug(' - - - - - - - ')
    
    client_id = credentials['client_id']
    Scope='https://spreadsheets.google.com/feeds/'
    User_agent='myself'
    
    data = {}
    data['scope'] = Scope
    
    data['response_type'] = 'code' # Determines if the Google OAuth 2.0 endpoint returns an authorization code. For installed applications, a value of code should be used.
    
    data['client_id'] = client_id # 	the client_id obtained from the APIs Console 	Indicates the client that is making the request. The value passed in this parameter must exactly match the value shown in the APIs Console.
    
    data['redirect_uri'] = credentials['redirect_uri'] # one of the redirect_uri values registered at the APIs Console 	Determines where the response is sent. The value of this parameter must exactly match one of the values registered in the APIs Console (including the http or https schemes, case, and trailing '/'). You may choose between urn:ietf:wg:oauth:2.0:oob or an http://localhost port. See choosing a redirect_uri for more details.
    
    data['scope'] = Scope  # Indicates the Google API access your application is requesting. The values passed in this parameter inform the consent page shown to the user. There is an inverse relationship between the number of permissions requested and the likelihood of obtaining user consent.
    
    url = 'https://accounts.google.com/o/oauth2/auth'
    parms = urllib.urlencode(data)
    
    print "\n\n* * * * *  You have to verify that you DO allow this software to open your Google document space.  * * * * * "
    print "* * * * *         Here's the URL at which you can pick up your 'one-time' verification code.       * * * * * "
    print '\n\n{}?{}\n\n'.format(url, parms)
    code = raw_input('\nPaste that code here, now . . , then hit <Enter> ').strip()
    
    data = {}
    
    data['code'] = code  # The authorization code returned from the initial request
    data['redirect_uri'] = credentials['redirect_uri']  # The URI registered with the application
    data['grant_type'] = 'authorization_code'
    data['client_secret'] = credentials['client_secret']
    data['client_id'] = client_id

    url = 'https://accounts.google.com/o/oauth2/token'
    parms = urllib.urlencode(data)
    
    logging.debug('Obtaining token pair with : {}?{}'.format(url, parms))
    
    request = urllib2.Request (url, parms)
        
    resp = urllib2.urlopen(request)
    logging.debug('Raw response : {}.'.format(resp))
    
    theResponse = resp.read()
    logging.debug('Response text : {}.'.format(theResponse))
    
    theJSON = json.loads(theResponse)
    logging.debug('Response as json : {}.'.format(theJSON))

    user = {}
    user[client_id] = {}
    user[client_id]['access_token'] = theJSON['access_token']
    user[client_id]['refresh_token'] = theJSON['refresh_token']
    
    logging.debug(
            '==>\nAccess token : {}\nRefresh token : {}'.format(
                user[client_id]['access_token']
              , user[client_id]['refresh_token']
            )
    )

    
    return user

def refreshToken(credentials, store):

    result = {}
    app = credentials['now']['client_id']
    assert app in store
    assert 'client_secret' in store[app]
    

    user = credentials['now']['user_id']
    assert user in store
    assert app in store[user]
    
    token = store[user][app]['refresh_token']
    secret = store[app]['client_secret']
    url = "https://accounts.google.com/o/oauth2/token"
    
    logging.debug('Refresh the authorization {} gave to {} with token : {}.'.format(user, app, token))
    
    data = {}
    data['grant_type'] = 'refresh_token'
    data['client_secret'] = secret
    data['refresh_token'] = token
    data['client_id'] = app

    parms = urllib.urlencode(data)
    logging.debug('Calling {} with : {}.'.format(url, parms))
    request = urllib2.Request (url, parms)
        
    store[user][app]['access_token'] = json.loads(urllib2.urlopen(request).read())['access_token']
    logging.debug('Refreshed access token : {}.'.format(store[user][app]['access_token']))

    result['refresh_token'] = token
    result['access_token'] = store[user][app]['access_token']
    return result


