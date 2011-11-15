from resources.lib.BeautifulSoup import BeautifulSoup, Tag 
from datetime import date
from collections import namedtuple
import urllib2

"""
Module to that contains all the logic to parse the data from GameCentre
"""

GameListing = namedtuple('GameListing', 'home_team away_team score raw_url time')

class Listings():
    BASE_URL = 'http://www.nhl.com/ice/scores.htm'
    
    def find_listings(self, date=None):
        self.games = []
        listing_date = self.pick_date(date)
        listing_url = self.construct_scrape_page_url(listing_date)
        raw_games = self.find_games(listing_url)
        for x in raw_games:
            self.games.append(self.parse_raw_game(x))
        
    def pick_date(self, listing_date=None):
        '''Picks the listing_date to use for getting the scores. MM/DD/YYYY Format.'''
        if listing_date is None:
            return date.today().strftime('%m/%d/%Y')
        else:
            #TODO: add logic to pick yesterday's listing_date if it's early in the day
            if type(listing_date) is str:
                return listing_date
            else:
                return listing_date.strftime('%m/%d/%Y')
    
    def construct_scrape_page_url(self, date, base=BASE_URL):
        '''Consturcts the URL to scrape. date is a string in MM/DD/YYYY format'''
        return base + '?date=' + date 
    
    def find_games(self,url):
        page = urllib2.urlopen(url)
        soup = BeautifulSoup(page)
        games = soup.findAll('div', {'class':'sbGame'})
        return games
    
    def find_raw_url(self,element):
        """Finds the Watch Live URL."""
        def tag_filter(tag):
            name = tag.name
            title = tag.get('title')
            href = tag.get('href')
            if name != 'a':
                return False
            if not title:
                return False
            if not href:
                return False
            if 'Watch' in title and 'register' not in href:
                return True                
            return False
    
        try:
            result = element.find(tag_filter).get('href')
        except:
            #Couldn't find a watch live link
            result = None
        return result
    
    def find_time_left(self, game_element):
        """Find how much time is left in the game"""
        matches = game_element.find('th')
        if matches:
            result = str( matches.getText() ).rstrip()
            if '(' in result:
                result = result[:result.index('(')]
            return result
        else:
            return None
    
    def parse_raw_game(self, game_element):
        teams = game_element.findAll('td', {'class':'team left'})
        away_team = teams[0].find('a').getText()
        home_team = teams[1].find('a').getText()
        scores = game_element.findAll('td', {'class':'total'})
        home_score = scores[1].text
        away_score = scores[0].text
        raw_url =  self.find_raw_url(game_element)
        time = self.find_time_left(game_element)
        
        return GameListing(home_team, away_team, (away_score,home_score), raw_url, time)    


#Mini parsers used for various querries to GameCentre servers
def parse_game_servlet_response(response_xml):
    soup = BeautifulSoup(response_xml)
    g_id = home_program = away_program = None
    
    g_id = soup.find('id').getText()
    if soup.find('hashomeprogram') and soup.find('hashomeprogram').getText() == 'true':
        home_program = soup.find('homeprogramid').getText()
    if soup.find('hasawayprogram') and soup.find('hasawayprogram').getText() == 'true':
        away_program = soup.find('awayprogramid').getText()
        
    return g_id, home_program, away_program

def parse_encrypted_url_response(response_xml):
    soup = BeautifulSoup(response_xml)
    result = soup.find('path').getText()
    result = result[11:] #Strip off 'adaptive://'
    return result

def parse_streams_response(response_xml):
    soup = BeautifulSoup(response_xml)
    streams = soup.findAll('streamdata')
    currentTime = soup.find('channel').get('currenttime')
    result = []
    for x in streams:
        new_stream = Stream(currentTime, x.get(u'url'))
        new_stream.blockDuration = x.get(u'blockduration')
        new_stream.liveBlockDelay = x.get(u'liveblockdelay')
        new_stream.bitrate = x.get(u'bitrate')
        new_stream.liveStartupTime = x.get(u'livestartuptime')
        httpservers = []
        for server in x.findAll('httpserver'):
            httpservers.append(server.get('name'))
        new_stream.httpservers = httpservers
        result.append(new_stream)
    return result
        
class Stream(object):
    def __init__(self, currentTime, url):
        self.currentTime = currentTime
        self.url = url
