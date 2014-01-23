#!/usr/bin/env python
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
import urllib

try :

    from oauth2 import GeneratePermissionUrl
    from oauth2 import AuthorizeTokens
    from oauth2 import GenerateOAuth2String
    from oauth2 import RefreshToken
    
except ImportError :

    # Get Google oauth2 helper file
    webFile = urllib.urlopen('http://google-mail-oauth2-tools.googlecode.com/svn/trunk/python/oauth2.py')
    localFile = open('oauth2.py', 'w')
    localFile.write(webFile.read())
    webFile.close()
    localFile.close()
    
    from oauth2 import GeneratePermissionUrl
    from oauth2 import AuthorizeTokens
    from oauth2 import GenerateOAuth2String
    from oauth2 import RefreshToken


import os, sys, argparse, json, datetime, smtplib, base64, urllib2, time
from pprint import pprint
from progressbar import *

try:
    from oauth2client.client import OAuth2WebServerFlow
    from oauth2client.tools import run_flow
    from oauth2client.file import Storage
    from oauth2client.util import 	POSITIONAL_WARNING, POSITIONAL_EXCEPTION, POSITIONAL_IGNORE
except ImportError:
    print "ImportError: Please execute the following command (with root privileges):\npip install oauth2client"
    exit(-1)

SCOPE = 'https://spreadsheets.google.com/feeds/'

class NameSpace(object):
  def __init__(self, adict):
    self.__dict__.update(adict)
    


def third_person_auth(credentials):
    smtp_credentials = prep_smtp(credentials, True)
    # print 'Got SMTP creds;\n\n{}'.format(smtp_credentials)
    
    credentials.smtp_access_token = smtp_credentials['access_token']
    credentials.smtp_refresh_token = smtp_credentials['refresh_token']

    data = {}
    data['client_id'] = credentials.google_project_client_id # 	the client_id obtained from the APIs Console 	Indicates the client that is making the request. The value passed in this parameter must exactly match the value shown in the APIs Console.
    data['scope'] = SCOPE  # Indicates the Google API access your application is requesting. The values passed in this parameter inform the consent page shown to the user. There is an inverse relationship between the number of permissions requested and the likelihood of obtaining user consent.
    
    url = 'https://accounts.google.com/o/oauth2/device/code'
    parms = urllib.urlencode(data)

    request = urllib2.Request (url, parms)

    theJSON = json.loads(urllib2.urlopen(request).read())
#    print 'Response as json : {}.'.format(theJSON)

    credentials.verification_url = theJSON['verification_url']
    credentials.user_code = theJSON['user_code']
    credentials.expiry = int(theJSON['expires_in'])
    credentials.device_code = theJSON['device_code']
    
    credentials.subject = 'Requesting permission for remote access your Google Spreadheets.'
    credentials.text = 'To give {} access to your spreadsheets, please copy this code [ {} ] to your clipboard, turn to {} and enter it in the field provided. You have {} minutes to do so.'.format(credentials.client_email, credentials.user_code, credentials.verification_url, credentials.expiry / 60)
    
    sending = True
    while sending :
        try :
        
            request_approval(credentials)
            sending = False
            
        except smtplib.SMTPSenderRefused as sr :

            if sr[0] == 530 :
                if 'Authentication Required' in sr[1] :
#                    print "  *    *   Do we get an 'invalid grant' error now ?   *    *    * "
                    pass
                    
                print 'Refresh required: %s ' % credentials.smtp_refresh_token
                print 'Client ID: %s, Secret: %s ' % (credentials.google_project_client_id, credentials.google_project_client_secret)

                rslt = RefreshToken(
                      credentials.google_project_client_id
                    , credentials.google_project_client_secret
                    , credentials.smtp_refresh_token
                )
                print 'Result = {}'.format(rslt)
                if 'error' in rslt :
                    raise Exception("Cannot refresh invalid SMTP token. '%s' " % rslt['error'])
                    
                credentials.smtp_access_token = rslt['access_token']
                print 'New SMTP token : %s' % credentials.smtp_access_token
    
    return getAsForDevices(credentials)

def getAsForDevices(credentials) :
    m = 'ForDevices'

    subject = '%s wants permission to access your Google Spreadheets with "gspread".' % credentials.client_email
    
    print "\n\n* * * * *  You have to verify that you DO allow this software to open your Google document space."
    print     '* * * * *  Please check your email at %s.' % credentials.end_user_email
    print     '* * * * *  The message "%s" contains further instructions for you.' % subject

    data = {}

    data['client_id'] = credentials.google_project_client_id
    data['client_secret'] = credentials.google_project_client_secret
    data['code'] = credentials.device_code
    data['grant_type'] = 'http://oauth.net/grant_type/device/1.0'
    
    url = 'https://accounts.google.com/o/oauth2/token'
    
    parms = urllib.urlencode(data)

    request = urllib2.Request (url, parms)

    delay = 30
    triesLimit = credentials.expiry
    print 'Trying to get tokens.'
    
    widgets = [Bar('>'), ' ', Timer(), ' ', ReverseBar('<')]
    with ProgressBar(widgets=widgets, maxval=triesLimit) as progress:
        for i in range(1, triesLimit, delay):


            theJSON = json.loads(urllib2.urlopen(request).read())

            if 'access_token' in theJSON :
                progress.finish()

#                print ' * * * Authorized ! * * * '
                credentials.oauth_access_token = theJSON['access_token']
                credentials.oauth_refresh_token = theJSON['refresh_token']

                return credentials
                
            elif 'error' in theJSON :
                time.sleep(delay)
                progress.update(i)
            else :
                progress.finish()
                print ' * * *  Uh oh ! * * * %s ' % theJSON

    print "Too late.  You'll have to repeat it all."
    exit(-1)    




    
    '''
    while tries > 0 :
    
        theJSON = json.loads(urllib2.urlopen(request).read())
        # print 'Response as json : {}.'.format(theJSON)

        if 'access_token' in theJSON :
            print ' * * * Authorized ! * * * '
            
            credentials.oauth_access_token = theJSON['access_token']
            credentials.oauth_refresh_token = theJSON['refresh_token']

            return credentials
            
        elif 'error' in theJSON :
            if tries < triesLimit :
                time.sleep(delay)
                print 'Trying again to get tokens.  {} tries remain. ({})'.format(tries, theJSON['error'])
        else :
            print ' * * *  Uh oh ! * * * %s ' % theJSON
            
        tries -= 1
        
    print "Too late.  You'll have to repeat it all."
    exit(-1)    
    '''

def first_person_auth(credentials, manual=True):

    flow = OAuth2WebServerFlow(client_id=credentials.google_project_client_id,
                               client_secret=credentials.google_project_client_secret,
                               scope='https://spreadsheets.google.com/feeds https://docs.google.com/feeds',
                               redirect_uri='http://example.com/auth_return')

    storage = Storage('creds.data')

    flags = NameSpace({'noauth_local_webserver': manual, 'auth_host_port' : [8080, 8090], 'auth_host_name' : 'localhost', 'logging_level' : POSITIONAL_WARNING})

    rslt = run_flow(flow, storage, flags)
    credentials.oauth_access_token = rslt.access_token
    credentials.oauth_refresh_token = rslt.refresh_token
    return credentials
    
def prepare_result(credentials):

    print "\n =    =    =    =    =    =    =    =    =    =    =    =    =    =   "
    print "\n\n Code fragment to use to configure the gspread 'nose' tests.  Paste into the file 'test.config' : "
    print " .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  . "
    print ""
    print "auth_type: OAuth"    
    print ";"
    print "; These three values are obligatory for OAuth access, not required for UID/pwd access"
    print "client_secret: {}".format(credentials.google_project_client_secret)
    print "client_id: {}".format(credentials.google_project_client_id)
    print "refresh_token: {}".format(credentials.oauth_refresh_token)
    print ""
    print "; This value is optional but will make the tests start sooner if the token is less than 60 minutes old."
    print "access_token: {}".format(credentials.oauth_access_token)
    print ""
    print " .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  . "


    creds_oa = open('creds_oa.py', 'w')
    creds_oa.write("\nrefresh_token = '{}'".format(credentials.oauth_refresh_token))
    creds_oa.write("\nclient_secret = '{}'".format(credentials.google_project_client_secret))
    creds_oa.write("\nclient_id = '{}'".format(credentials.google_project_client_id))
    creds_oa.write("\n#")
    creds_oa.write("\nkey_ring = {}")
    creds_oa.write("\nkey_ring['grant_type'] = 'refresh_token'")
    creds_oa.write("\nkey_ring['refresh_token'] = refresh_token")
    creds_oa.write("\nkey_ring['client_secret'] = client_secret")
    creds_oa.write("\nkey_ring['client_id'] = client_id")
    creds_oa.write("\n#")
    creds_oa.write("\naccess_token = '{}'".format(credentials.oauth_access_token))
    creds_oa.write("\n#\n#")
    creds_oa.write("\ncredentials = {")
    creds_oa.write("\n      'cred_type': 'oauth'")
    creds_oa.write("\n    , 'key_ring': key_ring")
    creds_oa.write("\n    , 'access_token': access_token")
    creds_oa.write("\n}")
    creds_oa.write("\n#")
    creds_oa.write("\nsmtp_access_token = '{}'".format(credentials.smtp_access_token))
    creds_oa.write("\nsmtp_refresh_token = '{}'".format(credentials.smtp_refresh_token))
    creds_oa.write("\n#")

    creds_oa.close()

    print 'Identify the Google spreadsheet you want to use; use the full URL ("http://" etc, etc) '
    spreadsheet_url  = raw_input('Paste the full URL here : ')
    #
    qiktest = open('qiktest.py', 'w')
    qiktest.write("#!/usr/bin/env python")
    qiktest.write("\n# -*- coding: utf-8 -*-")
    qiktest.write("\nimport gspread")
    qiktest.write("\nfrom creds_oa import access_token, key_ring")
    qiktest.write("\n#")
    qiktest.write("\naccess_token = '{}'".format(credentials.oauth_access_token))
    qiktest.write("\ngc = gspread.authorize(access_token, key_ring)")
    qiktest.write("\n#")
    qiktest.write("\nwkbk = gc.open_by_url('{}')".format(spreadsheet_url))
    qiktest.write("\ncnt = 1")
    qiktest.write("\nprint 'Found sheets:'")
    qiktest.write("\nfor sheet in wkbk.worksheets():")
    qiktest.write("\n    print ' - Sheet #{}: Id = {}  Title = {}'.format(cnt, sheet.id, sheet.title)")
    qiktest.write("\n    cnt += 1")
    qiktest.write("\n#\n")
    qiktest.close()
    os.chmod('qiktest.py', 0o770)
    #
    print "\n\n   A simple example file called qiktest.py was written to disk."
    print "   It lists the names of the sheets in the target spreadsheet."
    print "   Test it with:"
    print "      $  python qiktest.py  ## or possibly just  ./qiktest.py\n\n\n"


def prep_smtp(credentials, test_mail = False) :

    expiry = ''    
    scope = 'https://mail.google.com/'

    print "\n    Acting as : {}".format(credentials.google_project_client_id)
    print "\n    To be able to request authorization from your users by email, you need to authorize this program to use Google's email resender via {}.".format(credentials.client_email)
    print "    Visit this url and follow the directions:\n"
    print '  %s' % GeneratePermissionUrl(
                                              credentials.google_project_client_id
                                            , scope
                                        )
    authorization_code = raw_input('\n\n    * * * Enter verification code: ')

    response = AuthorizeTokens  (
                                      credentials.google_project_client_id
                                    , credentials.google_project_client_secret
                                    , authorization_code
                                )
    access_token = ''
    refresh_token = ''
        
    try :
        access_token = response['access_token']
        refresh_token = response['refresh_token']
    except :
        print '\n\nServer reported   %s' % response
        print ' - Did you get the *latest* verification code?'
        print ' - Did you get all of it?'
        print ' - Did you use exactly the right ID and Secret for "Client for Installed Applications" from the Google API Console?\n(https://www.google.ca/url?sa=t&rct=j&q=&esrc=s&source=web&cd=1&cad=rja&ved=0CC4QFjAA&url=http%3A%2F%2Fcode.google.com%2Fapis%2Fconsole&ei=RgdEUvu-GM754AOeh4GgAQ&usg=AFQjCNFikY2jzXn9SOuZu0UcyS-59LlsTw&sig2=hpYvu7CrTb8royXO9f3nyQ&bvm=bv.53217764,d.dmg)'
        exit(-1)
    
    expiry = (datetime.datetime.now() + datetime.timedelta(0,response['expires_in'])).strftime('%Y-%m-%d %H:%M')
    '''
    print '\nSuccess :'
    print ' - Access Token: = %s' % access_token
    print ' - Refresh Token: %s'% refresh_token
    print ' - Access Token expires at : %s' % expiry
    '''
        
    smtp_conn = smtplib.SMTP('smtp.gmail.com', 587)
    smtp_conn.set_debuglevel(False)
    smtp_conn.ehlo('test')
    smtp_conn.starttls()
            
    # Temporary token...
    auth_string = GenerateOAuth2String  (
                                              credentials.client_email
                                            , access_token
                                            , base64_encode = False
                                        )
    '''
    print ">>>>"
    print auth_string
    print ">>>>"
    '''
    
    # Preparing test email envelope . . 
    title = 'Trash this email'
    body = 'Congratulations. You have fully enabled mail transfer through Google SMTP.'
    envelope = 'From: %s\nTo: %s\nSubject: %s\n\n%s' % (
                  credentials.client_email
                , credentials.client_email
                , title
                , body)
 
    if test_mail :
        print ' ~~~~~~~~~~~~~~~~~  START TEST EMAIL  ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~'
        print envelope
        print ' ~~~~~~~~~~~~~~~~~   END TEST EMAIL   ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~'
            
        try :
        
            smtp_conn.docmd('AUTH', 'XOAUTH2 ' + base64.b64encode(auth_string))
            print 'Sending TEST . . . '
            smtp_conn.sendmail(credentials.client_email, credentials.client_email, envelope)
            print '. . . TEST sent!\n'
            
        except smtplib.SMTPSenderRefused as sr :
            if sr[0] == 530 :
                print 'Refresh required: Using %s' % refresh_token
                access_token = RefreshToken(credentials.google_project_client_id, google_project_client_secret, refresh_token)
                print 'New token : %s' % access_token
                smtp_conn.docmd('AUTH', 'XOAUTH2 ' + base64.b64encode(auth_string))
                
                try :
                        smtp_conn.sendmail(credentials.client_email, credentials.client_email, envelope)
                except smtplib.SMTPSenderRefused as sr :
                    print sr
                    if sr[0] == 535 :
                        print 'The access token is correct. Maybe the user id is wrong?'
                        print '¿¿ Are you sure that <[{0}]> authorized <[{0}]> ??'.format(credentials.client_email)
                        exit(-1)


    
    else :
        print 'No test mail sent.'
    
    '''
    print 'Appending latest tokens to the bottom of the file "test_parms.py". . . '
    update_parms_file(access_token, refresh_token, expiry)
    print ' . . done.\n'
    '''
    
    return {'access_token':access_token, 'refresh_token':refresh_token, 'expiry': expiry}
    
    
def request_approval(credentials) :

    # print "Temporary token using %s and %s ."   %  (client_email, store[theCurrentOAuthClient].smtp_access_token)
    auth_string = GenerateOAuth2String(credentials.client_email, credentials.smtp_access_token)
            
    message = 'From: %s\nTo: %s\nSubject: %s\n\n%s' % (
           credentials.client_email, credentials.end_user_email, credentials.subject, credentials.text)
           
#    print message

    smtp_conn = smtplib.SMTP('smtp.gmail.com', 587)
    smtp_conn.set_debuglevel(False)
    smtp_conn.ehlo('test')
    smtp_conn.starttls()
    
    smtp_conn.docmd('AUTH', 'XOAUTH2 ' + auth_string)
    print 'Sending permission request . . . '
    smtp_conn.sendmail(credentials.client_email, credentials.end_user_email, message)
    print ' . . permission request sent!'
    
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


if __name__ == '__main__':

    json_files = []
    files = [f for f in os.listdir('.') if os.path.isfile(f)]
    cnt = 0;
    for f in files:
        if f.endswith('.json'):
            cnt += 1;
            json_files.append(f)
        
    theFile = None
    
    credentials = NameSpace(
            {
                  'text': ''
                , 'expiry': ''
                , 'subject': ''
                , 'user_code': ''
                , 'device_code': ''
                , 'client_email': ''
                , 'end_user_email': ''
                , 'verification_url': ''
                , 'smtp_access_token': ''
                , 'smtp_refresh_token': ''
                , 'oauth_access_token': ''
                , 'oauth_refresh_token': ''
                , 'google_project_client_id': ''
                , 'google_project_client_secret': ''
            })
    print credentials.text
    
    
    
    if cnt < 1:
        print '\n\nCould not find exactly one (1) expected json file (named like "client_secret_*.json" for example).'
        print 'You get such a file from https://cloud.google.com/console in the sub-section :'
        print '   - APIs & auth '
        print '      - Credentials '
        print '          - Client ID for native application'
        print '             - [Download JSON]'
        credentials.google_project_client_id = raw_input('\nPaste your Google "Client ID" : ')
        credentials.google_project_client_secret = raw_input('\nPaste your Google "Client Secret" : ')
        
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
        credentials.google_project_client_id = oauth_creds['client_id']
        credentials.google_project_client_secret = oauth_creds['client_secret']
        json_data.close()
        
        print '\n The file "{}" contains :\n'.format(theFile)
        print '               Client id : {}'.format(credentials.google_project_client_id)
        print '               Client secret : {}\n'.format(credentials.google_project_client_secret)

    personal = False
    # personal = raw_input("\n\nDo you want to:\n\n (1) authorize just yourself in a browser or, \n (2) email an authorization request code to a user and ask them to tell Google to let you in?\n\n        (1 or 2)  : ") in ("1")
    
    if personal:
        manual = raw_input("\n\nShall we try to open a page in your browser?  (Y/y)  : ") not in "Yy"
        credentials = first_person_auth(credentials, manual)
    else:
    
        credentials.end_user_email = "martinhbramwell@gmail.com"
        credentials.client_email = "mhb.warehouseman@gmail.com"

        # credentials.client_email = raw_input("\n\nEnter a GMail address to be used as an SMTP server : ")
        # credentials.end_user_email = raw_input("\n\nEnter the GMail address of the person who requested spreadsheet work : ")

        credentials = third_person_auth(credentials)
        
#    print '\n Credentials are :\n{}'.format(credentials)
    prepare_result(credentials)
    
    
