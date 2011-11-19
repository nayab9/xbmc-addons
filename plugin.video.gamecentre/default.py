import xbmcgui
import xbmcplugin
import sys
from resources import GCparser
from datetime import date

# magic; id of this plugin's instance - cast to integer
thisPlugin = int(sys.argv [1])

def create_listings():
    """
    Creates a listing that XBMC can display as a directory listing
    @return list
    """
    listing = []
    games = GCparser.parse()
    if games:
        for x in games:
            title = date.today().strftime('%Y-%m-%d') + '   ' + x.away_team + ' @ ' + x.home_team + ' (' + x.score[0] + '-' +x.score[1] + ')' + '  ' + x.time
            listing.append(title)
    return listing

def send_to_xbmc(listing):
    global thisPlugin
    
    for item in listing:
        listItem = xbmcgui.ListItem(item)
        xbmcplugin.addDirectoryItem(thisPlugin, '', listItem)
        
    xbmcplugin.endOfDirectory(thisPlugin)

send_to_xbmc( create_listings() )


