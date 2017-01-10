"""
Gets games and lines from bookmaker.eu. As of 2017/01/04, does not require
authentication for either request (games or lines).
"""

import re
import requests
from multiprocessing import Pool
from celery import shared_task, group
from nba.models import Team
import sportsbook.utils.odds as sbo
from sportsbook.models import Odds

#############
# Constants #
#############

def construct_odds_request_data(game_id):
    return ('{"prms":"gv_gmid=%s,gv_pst=1483556785687,gv_msgst=1483552131167'
            ',gv_progst=1483556654687,gvmenu=1,gvmenu_stamp=1483556785860,'
            'bs=1"}' % game_id)

SITE = 'BOOKMAKER'

# Get all games
GAMES = {
    'url': 'https://livebetting.bookmaker.eu/ngwbet.aspx/gvFrameHtml',
    'headers': {
        'Pragma': 'no-cache',
        'Origin': 'https://livebetting.bookmaker.eu',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'en-US,en;q=0.8',
        'User-Agent': ('Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_5)'
                       ' AppleWebKit/537.36 (KHTML, like Gecko)'
                       ' Chrome/55.0.2883.95 Safari/537.36'),
        'Content-Type': 'application/json; charset=UTF-8',
        'Accept': '*/*',
        'Cache-Control': 'no-cache',
        'X-Requested-With': 'XMLHttpRequest',
        'Connection': 'keep-alive',
        'Referer': 'https://livebetting.bookmaker.eu/ngwbet.aspx',
    },
    # You need to pass a valid gameID, but it seem to need to be current.
    'data': '{"gameID":84040}'
}

# Get odds for a single game
ODDS = {
    'url': 'https://livebetting.bookmaker.eu/refresh.aspx/Refresh',
    'headers': {
        'Pragma': 'no-cache',
        'Origin': 'https://livebetting.bookmaker.eu',
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
        'Referer': 'https://livebetting.bookmaker.eu/ngwbet.aspx',
    },
    'data': construct_odds_request_data,
    'regex': {
        'title': u'<div class="propTitle"><span>(.+)</span>',
        'teams': u'<div class="propText">(.+)</div>',
        'odds': u'<div class="odds">(.+?)<img'
    }
}

# Maximum odds to consider - otherwise, betting might be frozen (when betting
# freezes, the odds explode to a very large number).
ODDS_LIMIT = 9000

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
        'games': [{
            'gameStat': 2,
            'sportName': 'Basketball',
            'gameID': 84039,
            'leagueOrder': 1,
            'title': 'Milwaukee Bucks at New York Knicks',
            'tv': True,
            'fav': False,
            'leagueName': 'NBA',
            'startTime': '4:30 PM',
            'leagueID': 2,
            'brMatchID': 9955431,
            'sportID': 2,
            'sportOrder': 2,
            'stamp': -62135596800000
        }, ...],
        'html': [str],
        ...
    }}

    Args:
        None
    Returns:
        [list]: List of game ids to monitor: ['90001', '90002', ...]
    """
    response = requests.post(GAMES['url'], headers=GAMES['headers'],
                             data=GAMES['data'])
    if response.status_code == 200:
        try:
            games = response.json()['d']['games']
            # Filter for NBA for now
            return [game['gameID'] for game in games
                    if game['leagueName'] == 'NBA']
        except KeyError:
            print ('[WARNING/bookmaker.get_games()]: Unable to parse response'
                   ' json.')
            return []
    else:
        print '[WARNING/bookmaker.get_games()]: Error calling endpoint.'
        return []

def get_moneyline(game_id):
    """
    Sample response:
    { 'd': {
        'gvProps': [{
            'gameID': 84040,
            'propID': 3570884,
            'nPropStatus': 1,
            'mainPropSlot': 0,
            'stamp': 1483556933237,
            'html': "\r\n\r\n\u003c!-- Begin ~/Skin/{0}/Content/gvGameProp.ascx
                     --\u003e\r\n\u003cdiv class=\"gvProp\"pid=\u00273570884
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
        [tuple]: Tuple of: ((Team1, Odds1), (Team2, Odds2)), where @Team is a
                 Team object (e.g. <Team: Houston Rockets>) and @Odds is an
                 int (e.g. -110).
    """
    def is_moneyline(html):
        # Take the first group, which is the value of propTitle
        if html:
            match = re.search(ODDS['regex']['title'], html)
            return match and match.group(1) == 'Winner Match'
        return False

    def get_odds(html):
        try:
            team1, team2 = re.findall(ODDS['regex']['teams'], html)
            odds1, odds2 = re.findall(ODDS['regex']['odds'], html,
                                      flags=re.DOTALL)
            team1, team2 = (normalize_team(team1), normalize_team(team2))
            odds1, odds2 = (normalize_odds(odds1), normalize_odds(odds2))
            # Sort by team id
            return sorted(
                ((team1, odds1), (team2, odds2))
                if abs(odds1) < ODDS_LIMIT and abs(odds2) < ODDS_LIMIT
                else None,
                key=lambda x: x[0].id
            )
        except ValueError:
            print '[WARNING/bookmaker.get_odds()]: Unable to parse odds HTML.'
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
                print ('[WARNING/bookmaker.get_moneyline()]: Found %d open'
                       ' moneyline bets for %s, expected 1.'
                       % (len(odds), game_id))
                return None
        except KeyError:
            print ('[WARNING/bookmaker.get_moneyline()]: Unable to parse'
                   ' response json.')
            return None
    else:
        print '[WARNING/bookmaker.get_moneyline()]: Error calling endpoint.'
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
    sbo.write_moneyline(get_moneyline(game_id), 'BOOKMAKER')

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
