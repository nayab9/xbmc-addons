import unittest
import os
from datetime import date
from resources import GCparser

def read_test_data_file(file_to_read):
    full_path = os.getcwd() + '/data/' + file_to_read
    with open(full_path, 'r') as f:
        result = f.read()
    return result
    
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
        self.assertEqual(('02','0091'), game.game_id)
        self.assertEqual('San Jose', game.away_team)
        self.assertEqual('New Jersey', game.home_team)
        self.assertEqual(('4','3'), game.score)
        self.assertEqual('http://www.nhl.com/ice/gamecenterlive.htm?id=2011020091', game.raw_url)
        self.assertEqual('FINAL SO', game.time)
    
class Test_Servlets(unittest.TestCase):
    def setUp(self):
        pass
    
    def test_parse_game_servlet_response(self):
        response_xml = read_test_data_file('game_servlet_response.xml')
        parsed_data = GCparser.parse_game_servlet_response(response_xml)
        _id = '7194'
        home = '34304'
        away = '35636'
        expected = (_id, home, away)
        self.assertEqual(expected, parsed_data)
        
    def test_parse_play_servlet_response(self):
        response_xml = read_test_data_file('encrypted_url_response.xml')
        actual = GCparser.parse_encrypted_url_response(response_xml)
        expected = 'nlds31.neulion.com:443/nlds/nhl/blackhawks/as/live/s_blackhawks_live_game_hd?eid=32714&pid=34305&gid=3000&pt=5&uid=376556'
        self.assertEqual(expected, actual)
        
    def test_parse_streams_response(self):
        response_xml = read_test_data_file('play_response.xml')
        actual = GCparser.parse_streams_response(response_xml)
        self.assertEqual('1321225900000', actual[0].currentTime)
        self.assertEqual('/nlds/nhl/panthers/as/live/panthers_hd_1', actual[0].url)
        self.assertEqual('2000', actual[0].blockDuration)
        self.assertEqual('8000', actual[0].liveBlockDelay)
        self.assertEqual('409600', actual[0].bitrate)
        self.assertEqual(['nlds36.cdnllnwnl.neulion.com', 'nlds36.cdnl3nl.neulion.com'], actual[0].httpservers)
        