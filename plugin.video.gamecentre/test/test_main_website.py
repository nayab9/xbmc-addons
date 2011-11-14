import unittest
import os
from datetime import date
from resources.lib.scraper import main_website

class TestGameCenter(unittest.TestCase):
    
    def setUp(self):
        unittest.TestCase.setUp(self)
        self.TEST_URL = 'file://' + os.getcwd() + '/testPage.htm'
        
    def testPickDate(self):
        d = date(2011, 12, 31)
        expected = '12/31/2011'
        result = main_website.pick_date(currentDate=d)
        self.assertEqual(expected, result)
        
        expected = date.today().strftime('%m/%d/%Y')
        result = main_website.pick_date()
        self.assertEqual(expected, result)
    
    
    def testConstructURL(self):
        expected = 'http://www.nhl.com/ice/scores.htm?date=04/21/2011'
        result = main_website.construct_scrape_page_url('04/21/2011')
        
        self.assertEqual(expected, result)
    
    def testFindGames(self):
        games = main_website.find_games(self.TEST_URL)
        
        self.assertEqual(4, len(games))

    def testParseGame(self):
        games = main_website.find_games(self.TEST_URL)
        game = main_website.parse_game(games[0])
        self.assertEqual('San Jose', game.away_team)
        self.assertEqual('New Jersey', game.home_team)
        self.assertEqual(('4','3'), game.score)
        self.assertEqual('http://www.nhl.com/ice/gamecenterlive.htm?id=2011020091', game.raw_url)
        self.assertEqual('FINAL SO', game.time)
    
