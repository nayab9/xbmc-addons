import urllib
import urllib2
import cookielib
import time
from urlgrabber.keepalive import HTTPHandler

#USER_AGENT = 'Mozilla/5.0 (X11; U; Linux i586; de; rv:5.0) Gecko/20100101 Firefox/5.0'
USER_AGENT = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/535.2 (KHTML, like Gecko) Chrome/15.0.874.120 Safari/535.2'

#URL's
LOGIN_URL = 'https://account.nhl.com/app?service=login&siteId=34'
SOCIALIZE_URL = 'https://socialize.gigya.com/socialize.notifyLogin'
SIMPLE_CONSOLE_URL = 'http://gamecenter.nhl.com/nhlgc/servlets/simpleconsole'
GAME_INFO_URL = 'http://gamecenter.nhl.com/nhlgc/servlets/game'
ENCRYPTED_VIDEO_PATH_URL = 'http://gamecenter.nhl.com/nhlgc/servlets/encryptvideopath'
API_URL = 'http://gscounters.gigya.com/gs/api.ashx'
API_KEY = '2_pd9mRZHRYIukd6DpOMReSfqTpuF0K4eHN_cz3hYmMGx8zmPE3ObXwGQCSKZ4FS1O' #NHL/Gigya key

class Comm(object):
    """
    Handles all commuication with NHL GameCentre servers
    GCParser.py is responsible for dealing with the responses
    """
    
    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.cookiejar = cookielib.CookieJar(cookielib.DefaultCookiePolicy())
        self.default_headers = ('User-Agent', USER_AGENT)
        self.br.addheaders = [self.default_headers]
        self.br.set_handle_robots(False)
        self.cookies = []
        keepalive_handler = HTTPHandler()
        self.api_opener = urllib2.build_opener(keepalive_handler)
        urllib2.install_opener(self.api_opener)
    
    def setup_cookies(self):
        print self.login()
        print self._get_simple_console_cookies()
        print self._get_api_cookies()
        print self._get_socialize_cookies()
        
    def login(self):
        """
        Login to GameCentre to get the auth cookies needed for viewing
        """
        login_params = {
               'userType':'REGISTERED_FAN',
               'returnUrl':'http://www.nhl.com/index.html',
               'returnOnError':'true',
               'username':self.username,
               'password':self.password }
        data = urllib.urlencode(login_params)
        
        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(self.cookiejar))
        opener.addheaders = [('User-Agent', USER_AGENT)]
        response = opener.open(LOGIN_URL, data) #Don't care about return page, just want the cookies
        
        #Extrac the auth cookies from the response
        request = urllib2.Request(ENCRYPTED_VIDEO_PATH_URL)
        cookie_names = map(lambda x: x.name, self.cookiejar._cookies_for_request(request))
        cookie_values = map(lambda x: x.value, self.cookiejar._cookies_for_request(request))
        cookies = dict(zip(cookie_names, cookie_values))
        self.cookies=cookies
        
        #Verify it worked
        if cookies['rfclient_auth']:
            return cookies['rfclient_auth'] > 10    #If present then login worked
        return False
    
    def _get_api_cookies(self):
        now_value = str(time.time())
        now_value = now_value.replace('.', '') + '00'
        request_params = (
            ('sdk', 'js'),
            ('f', 're'),
            ('e', 'loadc'),
            ('ak', API_KEY),
            ('now', now_value), #Unix time
            ('sref', ''))
        data = urllib.urlencode(request_params)
        headers = [
            ('Accept', "*/*"),
            ('Accept-Charset', 'ISO-8859-1,utf-8;q=0.7,*;q=0.3'),
            #('Accept-Encoding', 'gzip, deflate'),
            ('Accept-Language', 'en-US,en;q=0.8'),
            ('Connection', 'Keep-Alive'),
            ('User-Agent', USER_AGENT),
            ('Referer', 'http://www.nhl.com/') ]
        self.api_opener.addheaders = headers
        response = self.api_opener.open(API_URL + '?' + data)
        self.extract_cookies(response.info())
        
        #Verify
        if 'ucid' in self.cookies:
            return True
        return False
        
    
    def _get_socialize_cookies(self):
        """
        Sets more auth related cookies. Used by login
        """
        code = None
        for k,v in self.cookies.iteritems():
            if 'gac' in k:
                code = v
        
        request_params = (
            ('format', 'jsonp'),
            ('sdk', 'js'),
            ('APIKey', API_KEY), 
            ('authCode', code), #cookie value received at login. cookie name starts with gac
            ('lang', 'en'),
            ('callback', 'gigya.global.JPCMD.prototype.hanldeJPResponse'),
            ('context', 'R1321673290079_0.9422900734934956'), #Where does this value come from?
            ('authMode', 'cookie') )
        data = urllib.urlencode(request_params)
        headers = [
            ('Accept', "*/*"),
            ('Accept-Charset', 'ISO-8859-1,utf-8;q=0.7,*;q=0.3'),
            #('Accept-Encoding', 'gzip, deflate'),
            ('Accept-Language', 'en-US,en;q=0.8'),
            ('Connection', 'Keep-Alive'),
            ('User-Agent', USER_AGENT),
            ('Cookie', self.generate_cookie_string(self.cookies) ),
            ('Referer', 'http://www.nhl.com/') ]
        self.api_opener.addheaders = headers
        response = self.api_opener.open(SOCIALIZE_URL + '?' + data)
        
        self.extract_cookies(response.info())
        
        #Remove gac cookie now
        for k,_ in self.cookies.iteritems():
            if 'gac' in k:
                to_del = k
        del self.cookies[to_del]
        del self.cookies['ucid']
        del self.cookies['gmid']
                
        #Create dictioinary out of response
        self.gigya_response = dict()
        for line in response.readlines():
            if ':' in line:
                line = line.strip().replace('"','')
                key = line[:line.find(':')]
                value = line[line.find(':')+1:].replace(',','')
                self.gigya_response[key] = value.strip()
        
        #Add glt cookie
        glt_name = 'glt_' + API_KEY 
        self.cookies[glt_name] = self.gigya_response['login_token'].replace('=',"%3D").replace('|', "%7C")

        if 'glt' in self.cookies:
            return True
        return False
    

    def _get_simple_console_cookies(self):
        """
        Used to set cookies needed for encrypted url request
        """
        request_params = {'isFlex':'true'}
        data = urllib.urlencode(request_params)
        headers = [('User-Agent', USER_AGENT)]
        self.api_opener.addheaders = headers
        request = urllib2.Request(SIMPLE_CONSOLE_URL)
        response = self.api_opener.open(request, data)
        self.extract_cookies( response.info() )
        
        #Verify it worked
        if 'JSESSIONID' in self.cookies:
            return True
        return False
            
        
    def retreive_listings(self, day):
        #Doesn't care about login info, but will use it if available
        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(self.cookiejar))
        opener.addheaders = [('User-Agent', USER_AGENT)]
        return opener.read()

    
    def send_game_servlet_request(self, game_id):
        request_params = {
            'gid':None,
            'type':'2',
            'isFlex':'true',
            'season':'2011'}
        request_params['gid'] = game_id
        data = urllib.urlencode(request_params)
        headers = [
            ('User-Agent', USER_AGENT),
            ('Cookie', self.generate_cookie_string(self.cookies)) ]
        
        self.api_opener.addheaders=headers
        response = self.api_opener.open(GAME_INFO_URL, data)
        self.extract_cookies(response.info())
        return response
    
    def send_encrypted_url_request(self, program_id):
        request_params = (
            ('isFlex', 'true'),
            ('type', 'gameaa'),
            ('path', program_id) #Home or Away programID from the game servlet response
            ) 
        data = urllib.urlencode(request_params)
        self.cookies['s_cc'] ='true'
        self.cookies['s_sq'] = '%5B%5BB%5D%5D'
        #s_sq
        #kick_sess_ronin
        headers = [
            ('Accept', "*/*"),
            ('Accept-Charset', 'ISO-8859-1,utf-8;q=0.7,*;q=0.3'),
            #('Accept-Encoding', 'gzip, deflate'),
            ('Accept-Language', 'en-US,en;q=0.8'),
            ('Connection', 'Keep-Alive'),
            ('User-Agent', USER_AGENT),
            ('Cookie', self.generate_cookie_string(self.cookies) ),
            ('Origin', 'http://nhl.cdn.neulion.net'),
            ('Referer', 'http://nhl.cdn.neulion.net/u/nhlgc/gclplayer.swf'), ]
        
        self.api_opener.addheaders=headers
        response = self.api_opener.open(ENCRYPTED_VIDEO_PATH_URL, data)
        return response
    
    def send_streams_request(self, encrypted_url):
        playNoCacheTick = None
        self.api_opener.addheaders = [('Referer', 'http://nhl.cdn.neulion.net/u/nhlgc/gclplayer.swf')]
        print 'http://'+encrypted_url
        response = self.api_opener.open('http://' + encrypted_url)
        return response

    def extract_cookies(self, info):
        raw_cookies = info.getallmatchingheaders('set-cookie')
        for raw_cookie in raw_cookies:
            raw_cookie = raw_cookie.replace('Set-Cookie: ','')
            cookie = (raw_cookie[:raw_cookie.find('=')], raw_cookie[raw_cookie.find('=') + 1:raw_cookie.find(';')])
            self.cookies[cookie[0]] = cookie[1]
        return

    def generate_cookie_string(self, cookies):
        result = ''
        for k, v in cookies.iteritems():
            result += k + '=' + v + ';'
        return result.rstrip(';')