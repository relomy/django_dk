"""
Gets games and lines from betonline.ag. As of 2017/01/04, does not require
authentication for either request (games or lines).
"""

import re
import requests
from multiprocessing import Pool
from celery import shared_task, group
from bs4 import BeautifulSoup
from nba.models import Team
import sportsbook.utils.odds as sbo
from sportsbook.models import Odds

#############
# Constants #
#############

def construct_odds_request_data(game_id):
    #epoch = datetime.datetime(1970, 1, 1)
    #dt = (datetime.datetime.utcnow() - epoch).total_seconds() * 1000
    return ('{"prms":"gv_gmid=%s,gv_pst=1483646359097,gv_msgst=1483646359097'
            ',gv_progst=1483646359097"}' % (game_id))

SITE = 'BETONLINE'

SPORT_ID = 2 # Basketball
LEAGUE_ID = 2 # NBA

# Get all games
GAMES = {
    'url': 'https://dgslivebetting.betonline.ag/ngwbet.aspx/ovFrameHtml',
    'headers': {
        'Pragma': 'no-cache',
        'Origin': 'https://dgslivebetting.betonline.ag',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'en-US,en;q=0.8',
        'User-Agent': ('Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_5)'
                       ' AppleWebKit/537.36 (KHTML, like Gecko)'
                       ' Chrome/55.0.2883.95 Safari/537.36'),
        'Content-Type': 'application/json; charset=utf-8',
        'Accept': '*/*',
        'Cache-Control': 'no-cache',
        'X-Requested-With': 'XMLHttpRequest',
        'Connection': 'keep-alive',
        'Referer': 'https://dgslivebetting.betonline.ag/ngwbet.aspx',
        'Content-Length': '0',
    },
    'regex': (r'class="game" gid="(.+)" sportid="%d" leagueid="%d"'
              % (SPORT_ID, LEAGUE_ID))
}

# Get odds for a single game
ODDS = {
    'url': 'https://dgslivebetting.betonline.ag/refresh.aspx/Refresh',
    'headers': {
        'Pragma': 'no-cache',
        'Origin': 'https://dgslivebetting.betonline.ag',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'en-US,en;q=0.8',
        'User-Agent': ('Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_5)'
                       ' AppleWebKit/537.36 (KHTML, like Gecko)'
                       ' Chrome/55.0.2883.95 Safari/537.36'),
        'Content-Type': 'application/json; charset=UTF-8',
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'Cache-Control': 'no-cache',
        'X-Requested-With': 'XMLHttpRequest',
        'Connection': 'keep-alive',
        'Referer': 'https://dgslivebetting.betonline.ag/ngwbet.aspx',
    },
    'data': construct_odds_request_data
}

###########
# Helpers #
###########

def normalize_team(team_name):
    return Team.get_by_name(team_name)

def normalize_odds(odds_str):
    return sbo.us_to_decimal(int(odds_str.strip().replace(u'\u2212', '-')))

##########
# Public #
##########

def get_games():
    """
    Sample response:
    { 'd': {
        'html': '"\r\n\r\n\u003cdiv id=\"ovFrame\"...',
        'maxGameStamp': 1483635396433,
        'maxPropStamp': 1483635668440,
        'maxScoreStamp': 1483635681210,
        ...
    }}

    Args:
        None
    Returns:
        [list]: List of game ids to monitor: ['90001', '90002', ...]
    """
    response = requests.post(GAMES['url'], headers=GAMES['headers'])
    if response.status_code == 200:
        try:
            games_html = response.json()['d']['html']
            return re.findall(GAMES['regex'], games_html)
        except KeyError:
            print ('[WARNING/betonline.get_games()]: Unable to parse response'
                   ' json.')
            return []
    else:
        print '[WARNING/betonline.get_games()]: Error calling endpoint.'
        return []

def get_moneyline(game_id):
    """
    Sample response:
    { 'd': {
        'gvProps': [{
            'gameID': 70014,
            'propID': 2873560,
            'nPropStatus': 1,
            'mainPropSlot': 0,
            'stamp': 1483644838637,
            'html': "\r\n\r\n\u003c!-- Begin ~/Skin/{0}/Content/gvGameProp.ascx
                     --\u003e\r\n\u003cdiv class=\"gvProp\"pid=\u00272873560
                     \u0027 order=\u002710\u0027\u003e\r\n...""
        }, ...],
        'html': [str],
        ...
    }}
    Parse HTML string for each moneyline bet (called 'Winner Match'), and look
    for "odds=" for each team.

    Args:
        game_id [str]: Id of the game to get lines for.
    Returns:
        [tuple]: ((Team1, Odds1), (Team2, Odds2)), where @Team is a Team object
                 (e.g. <Team: Houston Rockets>) and @Odds is a European odds
                 float (e.g. 1.4).
    """
    def is_moneyline(html):
        # Take the first group, which is the value of propTitle
        if html:
            soup = BeautifulSoup(html, 'html5lib')
            title = soup.find_all(class_='propTitle')
            return title and title[0] and title[0].string == 'Moneyline'
        return False

    def get_odds(html):
        try:
            soup = BeautifulSoup(html, 'html5lib')
            team1, team2 = [node.string for node in soup.find_all(class_='name')]
            odds1, odds2 = [node.string for node in soup.find_all(class_='odds')]
            team1, team2 = (normalize_team(team1), normalize_team(team2))
            odds1, odds2 = (normalize_odds(odds1), normalize_odds(odds2))
            # Sort by team id
            return sorted(((team1, odds1), (team2, odds2)),
                          key=lambda x: x[0].id)
        except ValueError:
            print '[WARNING/betonline.get_odds()]: Unable to parse odds HTML.'
            return None

    if not game_id:
        return

    response = requests.post(ODDS['url'], headers=ODDS['headers'],
                             data=ODDS['data'](game_id))
    if response.status_code == 200:
        try:
            bets = response.json()['d']['gvProps']
            odds = [get_odds(bet['html']) for bet in bets
                    if is_moneyline(bet['html']) and get_odds(bet['html'])]
            if len(odds) == 1:
                return odds[0]
            else:
                print ('[WARNING/betonline.get_moneyline()]: Found %d open'
                       ' moneyline bets for %s, expected 1.'
                       % (len(odds), game_id))
                return None
        except KeyError:
            print ('[WARNING/betonline.get_moneyline()]: Unable to parse'
                   ' response json.')
            return None
    else:
        print '[WARNING/betonline.get_moneyline()]: Error calling endpoint.'
        return None

@shared_task
def write_moneyline(game_id):
    """
    Writes moneyline odds for a single game to the database.

    Args:
        game_id [str]: Id of the game to write to the database.
    Returns:
        None
    """
    Odds.write_moneyline(get_moneyline(game_id), 'BETONLINE')

def run_moneylines(parallel=False, max_processes=10):
    """
    Do not run this in parallel with Celery. Instead, use get_games() and
    get_moneyline() independently.

    Args:
        parallel [bool]: Whether to get moneylines in parallel.
        processes [int]: Maximum number of concurrent processes to run.
    Returns:
        [list]: List of moneyline odds: [
            ((<Team: Sacramento Kings>, 1.2), (<Team: Miami Heat>, 3.5)),
            ((<Team: Chicago Bulls>, 1.9), (<Team: Memphis Grizzlies>, 4.7)),
            ...
        ]
    """
    if parallel:
        game_ids = get_games()
        pool = Pool(processes=min(len(game_ids), max_processes))
        results = pool.map(get_moneyline, game_ids)
        results = [result for result in results if result is not None]
        return results
    else:
        return filter(lambda x: x is not None,
                      [get_moneyline(game_id) for game_id in get_games()])

def write_moneylines(parallel=False):
    """
    Writes moneyline odds for all active games to the database.

    Args:
        parallel [bool]: Whether to get moneylines in parallel.
    Returns:
        None
    """
    game_ids = get_games()
    if parallel:
        group(write_moneyline.s(game_id) for game_id in game_ids if game_id)()
    else:
        [write_moneyline(game_id) for game_id in game_ids if game_id]

