import urllib
import urllib2
import cookielib

USER_AGENT = 'Mozilla/5.0 (X11; U; Linux i586; de; rv:5.0) Gecko/20100101 Firefox/5.0'

#URL's
LOGIN_URL = 'https://account.nhl.com/app?service=login&siteId=34'
GAME_INFO_URL = 'http://gamecenter.nhl.com/nhlgc/servlets/game'

class Auth(object):
    """
    Class to deal with logging into NHL GameCentre and retreiving any data that requires a login
    """
    
    def __init__(self):
        custom_policy = cookielib.DefaultCookiePolicy(rfc2965=True)
        self.cookiejar = cookielib.CookieJar(custom_policy)
        

    def login(self):
        """
        Login to GameCentre to get the auth cookies needed for viewing
        """
        login_params = {
               'userType':'REGISTERED_FAN',
               'returnUrl':'http://www.nhl.com/ice/gamecenterlive.htm?id=2011020240',
               'returnOnError':'true',
               'username':None,
               'password':None }
        
        #TODO: use xbmc to get saved values
        login_params['username'] = 'cjsimpson'
        login_params['password'] = 'klinkdsa'
        
        data = urllib.urlencode(login_params)
        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(self.cookiejar))
        opener.addheaders = [('User-Agent', USER_AGENT)]
        response = opener.open(LOGIN_URL, data)
        
        #TODO: Determine if the login was successful
        return True
    
    def get_game_info(self, game_id):
        request_params = {
            'gid':None,
            'type':'2',
            'isFlex':'true',
            'season':'2011'}
        data = urllib.urlencode(request_params)
        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(self.cookiejar))
        opener.addheaders = [('User-Agent', USER_AGENT)]
        response = opener.open(GAME_INFO_URL, data)
        id, home_program_id, away_program_id = ''
        
        return response
    