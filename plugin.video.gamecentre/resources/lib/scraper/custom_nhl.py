from BeautifulSoup import BeautifulSoup 

def parse_game_xml(game_xml):
    soup = BeautifulSoup(game_xml)
    g_id, home_program, away_program = None
    g_id = soup.find('id').getText()
    if soup.find('hasHomeProgram').getText() == 'true':
        home_program = soup.find('homeProgramId').getText()
    if soup.find('hasAwayProgram').getText() == 'true':
        away_program = soup.find('awayProgramId').getText()
        
    return g_id, home_program, away_program