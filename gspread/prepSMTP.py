import datetime
import base64
import smtplib

try :

    from goauth2_helper import GeneratePermissionUrl
    from goauth2_helper import AuthorizeTokens
    from goauth2_helper import GenerateOAuth2String
    from goauth2_helper import RefreshToken
    
except ImportError :

    # Get Google oauth2 helper file
    webFile = urllib.urlopen('http://google-mail-oauth2-tools.googlecode.com/svn/trunk/python/oauth2.py')
    localFile = open('goauth2_helper.py', 'w')
    localFile.write(webFile.read())
    webFile.close()
    localFile.close()
    
    from goauth2_helper import GeneratePermissionUrl
    from goauth2_helper import AuthorizeTokens
    from goauth2_helper import GenerateOAuth2String
    from goauth2_helper import RefreshToken

def prep_smtp(args, test_mail = False) :

    google_project_client_id = args['client_id']
    google_project_client_email = args['client_email']
    google_project_client_secret = args['client_secret']
    
    expiry = ''
    '''
    if configure_email :
    '''
    scope = 'https://mail.google.com/'

    print "\n    To be able to request authorization from your users by email, you need to authorize this program to use Google's email resender in your name."
    print "    Visit this url and follow the directions:\n"
    print '  %s' % GeneratePermissionUrl(
                                              google_project_client_id
                                            , scope
                                        )
    authorization_code = raw_input('\n\n    * * * Enter verification code: ')

    response = AuthorizeTokens  (
                                      google_project_client_id
                                    , google_project_client_secret
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

            
    '''
    else :
    
        print 'An SMTP access token pair is already registered in "test_parms.py"'
        access_token = google_project_client_smtp_access_token
        refresh_token = google_project_client_smtp_refresh_token    
    '''

    smtp_conn = smtplib.SMTP('smtp.gmail.com', 587)
    smtp_conn.set_debuglevel(False)
    smtp_conn.ehlo('test')
    smtp_conn.starttls()
            
    # Temporary token...
    auth_string = GenerateOAuth2String  (
                                              google_project_client_email
                                            , access_token
                                            , base64_encode = False
                                        )
                                        
    # Preparing test email envelope . . 
    title = 'Trash this email'
    body = 'Congratulations. You have fully enabled mail transfer through Google SMTP.'
    envelope = 'From: %s\nTo: %s\nSubject: %s\n\n%s' % (
                  google_project_client_email
                , google_project_client_email
                , title
                , body)
 
    if test_mail :
        print ' ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~'
        print envelope
        print ' ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~'
            
        try :
        
            smtp_conn.docmd('AUTH', 'XOAUTH2 ' + base64.b64encode(auth_string))
            print 'Sending . . . '
            smtp_conn.sendmail(google_project_client_email, google_project_client_email, envelope)
            print '. . . sent!\n'
            
        except smtplib.SMTPSenderRefused as sr :
            if sr[0] == 530 :
                print 'Refresh required: Using %s' % refresh_token
                access_token = RefreshToken(google_project_client_id, google_project_client_secret, refresh_token)
                print 'New token : %s' % access_token
                smtp_conn.docmd('AUTH', 'XOAUTH2 ' + base64.b64encode(auth_string))
                smtp_conn.sendmail(google_project_client_email, google_project_client_email, envelope)

    
    else :
        print 'No test mail sent.'
    
    '''
    print 'Appending latest tokens to the bottom of the file "test_parms.py". . . '
    update_parms_file(access_token, refresh_token, expiry)
    print ' . . done.\n'
    '''
    args['srt'] = refresh_token
    args['sat'] = access_token
    
    return args

    

