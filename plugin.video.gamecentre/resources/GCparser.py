from resources.lib.BeautifulSoup import BeautifulSoup, Tag 
from datetime import date
from collections import namedtuple
import urllib2

"""
Module to that contains all the logic to parse the data from GameCentre
"""

GameListing = namedtuple('GameListing', 'game_id home_team away_team score time')

class StreamTypes(object):
    RTMP = 'rtmp'
    LIVE = 'live'

class Streams(object):
    def __init__(self):
        self.stream_type = None
        self.paths = dict()

    
class Listings():
    BASE_URL = 'http://www.nhl.com/ice/scores.htm'
    
    def pick_date(self, listing_date=None):
        """
        Picks the listing_date to use for getting the scores. MM/DD/YYYY Format.
        """
        if listing_date is None:
            return date.today().strftime('%m/%d/%Y')
        else:
            #TODO: add logic to pick yesterday's listing_date if it's early in the day
            if type(listing_date) is str:
                return listing_date
            else:
                return listing_date.strftime('%m/%d/%Y')
    
    def construct_scrape_page_url(self, date, base=BASE_URL):
        """
        Consturcts the URL to scrape. date is a string in MM/DD/YYYY format
        """
        return base + '?date=' + date 
    
    def find_games(self,url):
        page = urllib2.urlopen(url)
        soup = BeautifulSoup(page)
        games = soup.findAll('div', {'class':'sbGame'})
        return games
    
    def find_time_left(self, game_element):
        """
        Find how much time is left in the game
        """
        matches = game_element.find('th')
        if matches:
            result = str( matches.getText() ).rstrip()
            if '(' in result:
                result = result[:result.index('(')]
            return result
        else:
            return None
    
    def find_teams(self, game_element):
        teams = game_element.findAll('td', {'class':'team left'})
        away_team = teams[0].find('a').getText()
        home_team = teams[1].find('a').getText()
        return away_team, home_team
        
    def find_score(self, game_element):
        scores = game_element.findAll('td', {'class':'total'})
        away_score = scores[0].text
        home_score = scores[1].text
        return away_score, home_score
    
    def find_game_id(self, game_element): 
        tmp = game_element.findAll('a')
        game_id = None
        for x in tmp:
            if x.has_key('title') and 'Watch' in x.get('title'):
                watch_link = x.get('href')
                game_id = watch_link[-4:]
        return game_id


#Mini parsers used for various querries to GameCentre servers
def parse_game_servlet_response(response_xml):
    soup = BeautifulSoup(response_xml)
    streams = Streams()
    home_path = away_path = home_condensed_path = away_condensed_path = None
    
    #Figure out stream type
    if soup.find('isarchived') and soup.find('isarchived').getText()=='true':
        streams.stream_type = StreamTypes.RTMP
    else:
        streams.tream_type = StreamTypes.LIVE
        
    #Home Streams
    if soup.find('hashomeprogram') and soup.find('hashomeprogram').getText() == 'true':
        if streams.stream_type == StreamTypes.RTMP:
            home_path = soup.find('homeprogram').find('publishpoint').getText()[:-2]
            if soup.find('homecondensed'):
                home_condensed_path = soup.find('homecondensed').find('publishpoint').getText()[:-2]
    
        else:
            home_path = soup.find('homeprogramid').getText()
    
    #Away Streams
    if soup.find('hasawayprogram') and soup.find('hasawayprogram').getText() == 'true':
        if streams.stream_type == StreamTypes.RTMP:
            away_path = soup.find('awayprogram').find('publishpoint').getText()[:-2]
            if soup.find('awaycondensed'):
                home_condensed_path = soup.find('awaycondensed').find('publishpoint').getText()[:-2]
        else:
            away_path = soup.find('awayprogramid').getText()
    
    streams.paths = {
            'home'              :   home_path,
            'home_condensed'    :   home_condensed_path,
            'away'              :   away_path,
            'away_condensed'    :   away_condensed_path }
    return streams

def parse_encrypted_url_response(stream_type, response_xml):
    soup = BeautifulSoup(response_xml)
    raw = soup.find('path')
    if stream_type == StreamTypes.RTMP:
        result = raw.getText()
    elif stream_type == StreamTypes.LIVE:
        processed = raw.getText()[11:] #Strip 'addaptive://' from the start
        host = processed[:processed.find('/')]
        url = processed[processed.find('/'):]
        result = 'http://' + host + '/play?url=' + url
    
    return result

#def parse_streams_response(stream_type, response_xml):
#    if stream_type == StreamTypes.RTMP:
#        result = response_xml
#    
#    if stream_type == StreamTypes.LIVE:
#        soup = BeautifulSoup(response_xml)
#        streams = soup.findAll('streamdata')
#        currentTime = soup.find('channel').get('currenttime')
#        result = []
#        for x in streams:
#            new_stream = Stream(currentTime, x.get(u'url'))
#            new_stream.blockDuration = x.get(u'blockduration')
#            new_stream.liveBlockDelay = x.get(u'liveblockdelay')
#            new_stream.bitrate = x.get(u'bitrate')
#            new_stream.liveStartupTime = x.get(u'livestartuptime')
#            httpservers = []
#            for server in x.findAll('httpserver'):
#                httpservers.append(server.get('name'))
#            new_stream.httpservers = httpservers
#            result.append(new_stream)
#        return result
