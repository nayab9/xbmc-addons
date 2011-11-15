import unittest
import os
from datetime import date
from resources import GCparser

class Test_Listings(unittest.TestCase):
    
    def setUp(self):
        unittest.TestCase.setUp(self)
        self.TEST_URL = 'file://' + os.getcwd() + '/data/testPage.htm'
        self.listings = GCparser.Listings()
        
    def testPickDate(self):
        d = date(2011, 12, 31)
        expected = '12/31/2011'
        result = self.listings.pick_date(listing_date=d)
        self.assertEqual(expected, result)
        
        expected = date.today().strftime('%m/%d/%Y')
        result = self.listings.pick_date()
        self.assertEqual(expected, result)
    
    
    def testConstructURL(self):
        expected = 'http://www.nhl.com/ice/scores.htm?date=04/21/2011'
        result = self.listings.construct_scrape_page_url('04/21/2011')
        
        self.assertEqual(expected, result)
    
    def testFindGames(self):
        games = self.listings.find_games(self.TEST_URL)
        
        self.assertEqual(4, len(games))

    def testParseGame(self):
        games = self.listings.find_games(self.TEST_URL)
        game = self.listings.parse_raw_game(games[0])
        self.assertEqual('San Jose', game.away_team)
        self.assertEqual('New Jersey', game.home_team)
        self.assertEqual(('4','3'), game.score)
        self.assertEqual('http://www.nhl.com/ice/gamecenterlive.htm?id=2011020091', game.raw_url)
        self.assertEqual('FINAL SO', game.time)
    
class Test_Servlets(unittest.TestCase):
    def setUp(self):
        pass

    def test_parse_game_servlet_response(self):
        response_file = os.getcwd() + '/data/game_servlet_response.xml'
        with open(response_file, 'r') as f:
            response = f.read()
        parsed_data = GCparser.parse_game_servlet_response(response)
        _id = u'7194'
        home = u'34304'
        away = u'35636'
        expected = (_id, home, away)
        self.assertEqual(expected, parsed_data)