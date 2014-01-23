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
    


def third_person_auth(google_project_client_id, google_project_client_secret, client_email, end_user_email):
    #smtp_credentials = prep_smtp(client_email, google_project_client_id, google_project_client_secret, True)
    smtp_credentials = {'access_token': u'ya29.1.AADtN_UrB-lg5DHI6AcHM0A2YX--fEyfOi_xz4GiC-3qnY5i9UF9ps0k76nkbSi3xhHm1w', 'refresh_token': u'1/eUFgFZSSr3EvVpH2K46u33zMLHy2rauIhMeUbJCk-0k', 'expiry': '2014-01-22 14:15'}
    print 'Got SMTP creds;\n\n{}'.format(smtp_credentials)
    
    data = {}
    data['client_id'] = google_project_client_id # 	the client_id obtained from the APIs Console 	Indicates the client that is making the request. The value passed in this parameter must exactly match the value shown in the APIs Console.
    data['scope'] = SCOPE  # Indicates the Google API access your application is requesting. The values passed in this parameter inform the consent page shown to the user. There is an inverse relationship between the number of permissions requested and the likelihood of obtaining user consent.
    
    url = 'https://accounts.google.com/o/oauth2/device/code'
    parms = urllib.urlencode(data)

    request = urllib2.Request (url, parms)

    theJSON = json.loads(urllib2.urlopen(request).read())
#    print 'Response as json : {}.'.format(theJSON)
#    logging.debug('Response as json : {}.'.format(theJSON))

    verification_url = theJSON['verification_url']
    user_code = theJSON['user_code']
    expiry = int(theJSON['expires_in'])
    device_code = theJSON['device_code']
    
    subject = '%s wants permission to access your Google Spreadheets with "gspread".' % client_email
    text = 'To give {} access to your spreadsheets, please copy this code [ {} ] to your clipboard, turn to {} and enter it in the field provided. You have {} minutes to do so.'.format(client_email, user_code, verification_url, expiry / 60)
    
    req = {}
    req['sat'] = smtp_credentials['access_token']
    req['srt'] = smtp_credentials['refresh_token']
    req['user'] = end_user_email
    req['text'] = text
    req['expiry'] = expiry
    req['subject'] = subject
    req['client_id'] = google_project_client_id
    req['user_code'] = user_code
    req['device_code'] = device_code
    req['client_email'] = client_email
    req['client_secret'] = google_project_client_secret
    req['verification_url'] = verification_url

    print ' ..     ..     ..     ..     ..     ..     ..     ..     ..     ..     ..     ..    '
    pretty (req)
    print ' ..     ..     ..     ..     ..     ..     ..     ..     ..     ..     ..     ..    '

    sending = True
    while sending :
        try :
        
            request_approval(req)
            sending = False
            
        except smtplib.SMTPSenderRefused as sr :

            if sr[0] == 530 :
                client_secret = req['client_secret']
                smtp_refresh_token = req['srt']
                if 'Authentication Required' in sr[1] :
#                    print "  *    *   Do we get an 'invalid grant' error now ?   *    *    * "
                    pass
                    
#                print 'Refresh required: %s ' % smtp_refresh_token
#                print 'Client ID: %s, Secret: %s ' % (theCurrentOAuthClient, client_secret)

                rslt = RefreshToken(
                      req['client_id']
                    , client_secret
                    , smtp_refresh_token
                )
                if 'error' in rslt :
#                    close_store()
                    raise Exception("Cannot refresh invalid SMTP token. '%s' " % rslt['error'])
                    
                req['sat'] = rslt['access_token']
                print 'New SMTP token : %s' % req['sat']
    
    return NameSpace(getAsForDevices(req))

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
        print 'Response as json : {}.'.format(theJSON)

        if 'access_token' in theJSON :
            print ' * * * Authorized ! * * * '
            '''
            store[theCurrentEndUser][theCurrentOAuthClient].access_token = theJSON['access_token']
            store[theCurrentEndUser][theCurrentOAuthClient].refresh_token = theJSON['refresh_token']
            store[theCurrentEndUser][theCurrentOAuthClient].auth_method = m

            reopen_store()

            logging.debug(
                    '==>\nAccess token : {}\nRefresh token : {}'.format(
                        store[theCurrentEndUser][theCurrentOAuthClient].access_token
                      , store[theCurrentEndUser][theCurrentOAuthClient].refresh_token
                    )
            )
            '''
            
            return theJSON
            
        elif 'error' in theJSON :
            if tries < triesLimit :
                time.sleep(delay)
                print 'Trying again to get tokens.  {} tries remain.'.format(tries)
        else :
            print ' * * *  Uh oh ! * * * %s ' % theJSON
            
        tries -= 1
        
    print "Too late.  You'll have to repeat it all."
    exit(-1)    
    

def first_person_auth(idClient, secret, manual=True):

    flow = OAuth2WebServerFlow(client_id=idClient,
                               client_secret=secret,
                               scope='https://spreadsheets.google.com/feeds https://docs.google.com/feeds',
                               redirect_uri='http://example.com/auth_return')

    storage = Storage('creds.data')

    flags = NameSpace({'noauth_local_webserver': manual, 'auth_host_port' : [8080, 8090], 'auth_host_name' : 'localhost', 'logging_level' : POSITIONAL_WARNING})

    return run_flow(flow, storage, flags)
    
def prepare_result(idClient, secret, credentials):

    print "\n =    =    =    =    =    =    =    =    =    =    =    =    =    =   "
    print "\n\n Data for use in gspread 'nose' tests, in file test.config : "
    print " .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  . "
    print ""
    print "auth_type: OAuth"    
    print ";"
    print "; These three values are obligatory for OAuth access, optional for UID/pwd access"
    print '; The "wizard" get_google_oauth2_creds.py will you guide through the necessary steps and provide the values to paste here.'
    print "client_secret: {}".format(secret)
    print "client_id: {}".format(idClient)
    print "refresh_token: {}".format(credentials.refresh_token)
    print ""
    print "; This value is optional but will make the tests start sooner if the token is less than 60 minutes old."
    print "access_token: {}".format(credentials.access_token)
    print ""
    print " .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  . "


    creds_oa = open('creds_oa.py', 'w')
    creds_oa.write("\nrefresh_token = '{}'".format(credentials.refresh_token))
    creds_oa.write("\nclient_secret = '{}'".format(secret))
    creds_oa.write("\nclient_id = '{}'".format(idClient))
    creds_oa.write("\n#")
    creds_oa.write("\nkey_ring = {}")
    creds_oa.write("\nkey_ring['grant_type'] = 'refresh_token'")
    creds_oa.write("\nkey_ring['refresh_token'] = refresh_token")
    creds_oa.write("\nkey_ring['client_secret'] = client_secret")
    creds_oa.write("\nkey_ring['client_id'] = client_id")
    creds_oa.write("\n#")
    creds_oa.write("\naccess_token = '{}'".format(credentials.access_token))
    creds_oa.write("\n#\n#")
    creds_oa.write("\ncredentials = {")
    creds_oa.write("\n      'cred_type': 'oauth'")
    creds_oa.write("\n    , 'key_ring': key_ring")
    creds_oa.write("\n    , 'access_token': access_token")
    creds_oa.write("\n}")
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
    qiktest.write("\naccess_token = '{}'".format(credentials.access_token))
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


def prep_smtp(google_client_email, google_client_id, google_client_secret, test_mail = False) :

    expiry = ''    
    scope = 'https://mail.google.com/'

    print "\n    Acting as : {}".format(google_client_id)
    print "\n    To be able to request authorization from your users by email, you need to authorize this program to use Google's email resender via {}.".format(google_client_email)
    print "    Visit this url and follow the directions:\n"
    print '  %s' % GeneratePermissionUrl(
                                              google_client_id
                                            , scope
                                        )
    authorization_code = raw_input('\n\n    * * * Enter verification code: ')

    response = AuthorizeTokens  (
                                      google_client_id
                                    , google_client_secret
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
    print '\nSuccess :'
    print ' - Access Token: = %s' % access_token
    print ' - Refresh Token: %s'% refresh_token
    print ' - Access Token expires at : %s' % expiry
        
    smtp_conn = smtplib.SMTP('smtp.gmail.com', 587)
    smtp_conn.set_debuglevel(False)
    smtp_conn.ehlo('test')
    smtp_conn.starttls()
            
    # Temporary token...
    auth_string = GenerateOAuth2String  (
                                              google_client_email
                                            , access_token
                                            , base64_encode = False
                                        )
    print ">>>>"
    print auth_string
    print ">>>>"
    
    # Preparing test email envelope . . 
    title = 'Trash this email'
    body = 'Congratulations. You have fully enabled mail transfer through Google SMTP.'
    envelope = 'From: %s\nTo: %s\nSubject: %s\n\n%s' % (
                  google_client_email
                , google_client_email
                , title
                , body)
 
    if test_mail :
        print ' ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~'
        print envelope
        print ' ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~'
            
        try :
        
            smtp_conn.docmd('AUTH', 'XOAUTH2 ' + base64.b64encode(auth_string))
            print 'Sending . . . '
            smtp_conn.sendmail(google_client_email, google_client_email, envelope)
            print '. . . sent!\n'
            
        except smtplib.SMTPSenderRefused as sr :
            if sr[0] == 530 :
                print 'Refresh required: Using %s' % refresh_token
                access_token = RefreshToken(google_client_id, google_project_client_secret, refresh_token)
                print 'New token : %s' % access_token
                smtp_conn.docmd('AUTH', 'XOAUTH2 ' + base64.b64encode(auth_string))
                
                try :
                        smtp_conn.sendmail(google_client_email, google_client_email, envelope)
                except smtplib.SMTPSenderRefused as sr :
                    print sr
                    if sr[0] == 535 :
                        print 'The access token is correct. Maybe the user id is wrong?'
                        print '¿¿ Are you sure that <[{0}]> authorized <[{0}]> ??'.format(google_client_email)
                        exit(-1)


    
    else :
        print 'No test mail sent.'
    
    '''
    print 'Appending latest tokens to the bottom of the file "test_parms.py". . . '
    update_parms_file(access_token, refresh_token, expiry)
    print ' . . done.\n'
    '''
    
    return {'access_token':access_token, 'refresh_token':refresh_token, 'expiry': expiry}
    
def request_approval(args) :

    client_id = args['client_id']
    client_email = args['client_email']
    client_secret = args['client_secret']
    
#    if store[theCurrentOAuthClient].smtp_access_token is None :
#        args = prep_smtp(args, test_mail = True)
#        store[theCurrentOAuthClient].smtp_access_token = args['sat']
#        store[theCurrentOAuthClient].smtp_refresh_token = args['srt']
        
        

    # print "Temporary token using %s and %s ."   %  (client_email, store[theCurrentOAuthClient].smtp_access_token)
    auth_string = GenerateOAuth2String(client_email, args['sat'])
            
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


if __name__ == '__main__':

    json_files = []
    files = [f for f in os.listdir('.') if os.path.isfile(f)]
    cnt = 0;
    for f in files:
        if f.endswith('.json'):
            cnt += 1;
            json_files.append(f)
            
    theFile = None
    google_project_client_id = None
    google_project_client_secret = None
    if cnt < 1:
        print '\n\nCould not find exactly one (1) expected json file (named like "client_secret_*.json" for example).'
        print 'You get such a file from https://cloud.google.com/console in the sub-section :'
        print '   - APIs & auth '
        print '      - Credentials '
        print '          - Client ID for native application'
        print '             - [Download JSON]'
        google_project_client_id = raw_input('\nPaste your Google "Client ID" : ')
        google_project_client_secret = raw_input('\nPaste your Google "Client Secret" : ')
        
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
        google_project_client_id = oauth_creds['client_id']
        google_project_client_secret = oauth_creds['client_secret']
        json_data.close()
        print '\n The file "{}" contains :\n'.format(theFile)
        print '               Client id : {}'.format(google_project_client_id)
        print '               Client secret : {}\n'.format(google_project_client_secret)

    personal = False
    personal = raw_input("\n\nDo you want to:\n\n (1) authorize just yourself in a browser or, \n (2) email an authorization request code to a user and ask them to tell Google to let you in?\n\n        (1 or 2)  : ") in ("1")
    
    if personal:
        manual = raw_input("\n\nShall we try to open a page in your browser?  (Y/y)  : ") not in "Yy"
        credentials = first_person_auth(google_project_client_id, google_project_client_secret, manual)
    else:
######        your_email = raw_input("\n\nEnter a GMail address to be used as an SMTP server : ")
######        end_user_email = raw_input("\n\nEnter the GMail address of the person who requested spreadsheet work : ")

        end_user_email = "mhb.warehouseman@gmail.com"
        your_email = "alicia.factorepo@gmail.com"
        credentials = third_person_auth(google_project_client_id, google_project_client_secret, your_email, end_user_email)
        
    print '\n Credentials are :\n{}'.format(credentials)
    prepare_result(google_project_client_id, google_project_client_secret, credentials)
    
    
