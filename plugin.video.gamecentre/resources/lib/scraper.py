from lxml import etree
from datetime import date
from collections import namedtuple

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
    game_parser = etree.HTMLParser()
    tree = etree.parse(url, parser=game_parser)
    root = tree.getroot()
    games = [ x for x in root.findall(".//div[@class]") if x.attrib['class']=='sbGame']
    return games

def find_raw_url(element):
    """Finds the Watch Live URL."""
    for x in element.iterfind(".//a[@title]"):
        if 'Watch' in x.attrib['title']:
            result = x.attrib['href']
    if 'register' in result:
        result = None
    return result

def find_time(game_element):
    """Find how much time is left in the game"""
    matches = game_element.iterfind(".//th")
    if matches:
        return matches.next().text.rstrip()
    else:
        return None
    
def parse_game(game_element):
    teams = [ x for x in game_element.findall(".//td[@class]") if x.attrib['class']=='team left']
    home_team = teams[1].find("./a").text
    away_team = teams[0].find("./a").text
    scores = [ x for x in game_element.findall(".//td[@class]") if x.attrib['class']=='total']
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

