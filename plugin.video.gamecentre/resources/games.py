from datetime import date
import GCparser
import communicator
'''
Glue it all together
'''

class Streams(object):
    def __init__(self):
        pass
    

class NHLGame(object):
    game_id = ''
    title = ''
    home_team = ''
    home_score = ''
    away_team = ''
    away_score = ''
    
    def __init__(self, game_id):
        self.game_id=game_id
    
    def set_title(self):
        self.title = date.today().strftime('%Y-%m-%d') + '   ' + self.away_team + ' @ ' + self.home_team + ' (' + self.away_score + '-' +self.home_score + ')' + '  ' + self.time 

    def find_streams(self):
        response = self.comm.send_game_servlet_request(self.game_id)
        streams = GCparser.parse_game_servlet_response(response.read())
        self.streams = streams
    
    def generate_play_links(self):
        self.links = dict()
        for name, path in self.streams.paths.iteritems():
            if path is None:
                break
            encrypted_response = self.comm.send_encrypted_url_request(path)
            if self.streams.stream_type == GCparser.StreamTypes.RTMP:
                link = GCparser.parse_encrypted_url_response(self.streams.stream_type, encrypted_response)
                link = link[:link.find('?')] + '_hd' + link[link.find('?'):]
                self.links[name] = link
            elif self.streams.stream_type == GCparser.StreamTypes.LIVE:
                #TODO: Generate a m3u8 playlist
                pass
        return

def create_games_for_date(date=None):
    parser = GCparser.Listings()
    d = parser.pick_date(date)
    url = parser.construct_scrape_page_url(d)
    listings = parser.find_games(url)
    games = []
    for x in listings:
        gid = parser.find_game_id(x)
        game = NHLGame(gid)
        game.away_team, game.home_team = parser.find_teams(x)
        game.away_score, game.home_score = parser.find_score(x)
        game.time = parser.find_time_left(x)
        game.set_title()
        games.append(game)
    return games

def authenticate(username, password):
    comm = communicator.Comm(username, password)
    comm.setup_cookies()
    return comm

