import urllib
import urllib2
import cookielib

FORM_PARAMS = {'userType':'REGISTERED_FAN',
               'returnUrl':'http://www.nhl.com/ice/gamecenterlive.htm?id=2011020240',
               'returnOnError':'true',
               'username':None,
               'password':None}
LOGIN_URL = 'https://account.nhl.com/app?service=login&siteId=34'
USER_AGENT = 'Mozilla/5.0 (X11; U; Linux i586; de; rv:5.0) Gecko/20100101 Firefox/5.0'


class Auth(object):
    """
    Class to deal with authenication with NHL GameCenter
    """
    
    def __init__(self):
        custom_policy = cookielib.DefaultCookiePolicy(rfc2965=True)
        self.cookiejar = cookielib.CookieJar(custom_policy)
        
    def construct_postData(self):
        """
        Construct the form data needed to login via a HTTP post
        """
        #TODO: use xbmc to get saved values
        FORM_PARAMS['username'] = 'test_user'
        FORM_PARAMS['password'] = 'test_pass'
        data = urllib.urlencode(FORM_PARAMS)
        return data
    
    def login(self):
        """
        Login to GameCentre to get the auth cookies needed for viewing
        """
        data = self.construct_postData()
        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(self.cookiejar))
        opener.addheaders = [('User-Agent', USER_AGENT)]
        opener.open(LOGIN_URL, data)
        return True
        
    #TODO: is this needed? Could construct flash url instead of parsing from page.
    def open_page(self, page_url, data=None):
        """
        Wrapper for urllib2.urlopen. Adds authorization information to the request.
        """
        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(self.cookiejar))
        opener.addheaders = [('User-Agent', USER_AGENT)]
        return opener.open(page_url, data)
