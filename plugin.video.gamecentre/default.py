import xbmcgui
import xbmcplugin
import sys

# magic; id of this plugin's instance - cast to integer
thisPlugin = int(sys.argv [1])

def create_listings():
    """
    Creates a listing that XBMC can display as a directory listing
    @return list
    """
    listing = []
    #TODO: Pull the data from the scraper
    listing.append('Test 1')
    return listing

def send_to_xbmc(listing):
    global thisPlugin
    
    for item in listing:
        listItem = xbmcgui.ListItem(item)
        xbmcplugin.addDirectoryItem(thisPlugin, '', listItem)
    
    xbmcplugin.endOfDirectory(thisPlugin)

send_to_xbmc( create_listings() )


