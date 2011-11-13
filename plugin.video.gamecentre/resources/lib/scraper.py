from BeautifulSoup import BeautifulSoup 
from datetime import date
from collections import namedtuple
import urllib2

BASE_URL = 'http://www.nhl.com/ice/scores.htm'
Game = namedtuple('Game', 'home_team away_team score raw_url time')

def pick_date(currentDate=None):
    '''Picks the date to use for getting the scores. MM/DD/YYYY Format.'''
    #TODO: add logic to pick yesterday's date if it's early in the day
    if currentDate is None:
        currentDate = date.today()
    return currentDate.strftime('%m/%d/%Y')

def construct_url(date, base=BASE_URL):
    '''Consturcts the URL to scrape. date is a string in MM/DD/YYYY format'''
    return base + '?date=' + date 

def find_games(url):
    page = urllib2.urlopen(url)
    soup = BeautifulSoup(page)
    games = soup.findAll('div', {'class':'sbGame'})
    return games

def find_raw_url(element):
    """Finds the Watch Live URL."""
    def tag_filter(tag):
        if tag.name == 'a' \
        and 'Watch' in tag.get('title') \
        and 'register' not in tag.get('href'):
            return True
        else:
            return False
    result = element.find(tag_filter).get('href')
    return result

def find_time(game_element):
    """Find how much time is left in the game"""
    matches = game_element.find('th')
    if matches:
        result = str( matches.getText() ).rstrip()
        if '(' in result:
            result = result[:result.index('(')]
        return result
    else:
        return None
    
def parse_game(game_element):
    teams = game_element.findAll('td', {'class':'team left'})
    away_team = teams[0].find('a').getText()
    home_team = teams[1].find('a').getText()
    scores = game_element.findAll('td', {'class':'total'})
    home_score = scores[1].text
    away_score = scores[0].text
    raw_url =  find_raw_url(game_element)
    time = find_time(game_element)
    
    return Game(home_team, away_team, (away_score,home_score), raw_url, time)    

def parse(date=None):
    result = []
    if date is None:
        date = pick_date()
    game_elements = find_games( construct_url( date ) )
    for e in game_elements:
        result.append(parse_game(e))
    return tuple(result)

