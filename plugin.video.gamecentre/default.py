import xbmcgui
import xbmcplugin
import sys
import calendar
from datetime import date
from resources import games, GCparser

# magic; id of this plugin's instance - cast to integer
thisPlugin = int(sys.argv [1])

def create_listings():
    """
    Creates a listing that XBMC can display as a directory listing
    @return list
    """

def modes():
    list_game('0374')


def list_months():
    today = date.today()
    month_list = calendar.month_name
    for x in month_list[today.month:]:
        listItem = xbmcgui.ListItem(x + str(today.year))
        uri = 'plugin://plugin.video.gamecentre?mode=list_month?month=' + x
        xbmcplugin.addDirectoryItem(thisPlugin, uri, listItem, isFolder='True')
    xbmcplugin.endOfDirectory(thisPlugin)

def list_month(month):
    
    pass

def list_day(date='12/05/2011'):
    game_list = games.create_games_for_date(date)
    for game in game_list:
        title = game.set_title()
        listItem = xbmcgui.ListItem(title)
        uri = 'plugin://plugin.video.gamecentre?mode=list_game?game_id=' + game.game_id
        xbmcplugin.addDirectoryItem(thisPlugin, uri, listItem, isFolder='True')
    xbmcplugin.endOfDirectory(thisPlugin)
    
def list_game(game_id):
    print game_id
    comm = games.authenticate('user', 'pass')
    game = games.NHLGame(game_id)
    game.comm = comm
    game.find_streams()
    game.generate_play_links()
    for name, url in game.links.iteritems():
        listItem = xbmcgui.ListItem(name)
        xbmcplugin.addDirectoryItem(thisPlugin, url, listItem)
    xbmcplugin.endOfDirectory(thisPlugin)


if  __name__ == "__main__" :
    modes ()
    
sys.modules.clear()
