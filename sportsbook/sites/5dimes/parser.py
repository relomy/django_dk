"""
Gets games and lines from 5dimes.eu. As of 2017/01/04, does not require
authentication for either request (games or lines).
"""

import re
import requests
from nba.models import Team
from sportsbook.models import Odds

#############
# Constants #
#############

# Get all games
GAMES = {
    'url': 'http://lbultra.5dimes.eu/sports2/static.php',
    'headers': {
        'Pragma': 'no-cache',
        'Accept-Encoding': 'gzip, deflate, sdch',
        'Accept-Language': 'en-US,en;q=0.8',
        'User-Agent': ('Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_5)'
                       ' AppleWebKit/537.36 (KHTML, like Gecko)'
                       ' Chrome/55.0.2883.95 Safari/537.36'),
        'Accept': 'application/json, text/plain, */*',
        'Referer': 'http://lbultra.5dimes.eu/ultra/new5/index.php',
        'Connection': 'keep-alive',
        'Cache-Control': 'no-cache',
    }
}

##########
# Public #
##########

def get_games():
    """
    Sample response:
    {
        'sports': {
            '6': {
                'providerid': 1,
                'show': 1,
                'externalid': 48242,
                'id': 6,
                'name': 'Basketball'
            },
            ...
        },
        ...
    }

    Args:
        None
    Returns:
        [list]: List of game ids to monitor: ['90001', '90002', ...]
    """
    response = requests.get(GAMES['url'], headers=GAMES['headers'])
    if response.status_code == 200:
        try:
            games = response.json()['sports']
            # Filter for NBA for now
            return [game['externalid'] for game in games
                    if game['name'] == 'Basketball']
        except KeyError:
            print ('[WARNING/5dimes.get_games()]: Unable to parse response'
                   ' json.')
            return []
    else:
        print '[WARNING/5dimes.get_games()]: Error calling endpoint.'
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
                 string (e.g. CLE) and @Odds is a float (e.g. -110).
    """
    return

def run_moneyline():
    """
    Args:
        None
    Returns:
        [list]: List of moneyline odds: [
            ((u'SACRAMENTO KINGS', -199), (u'MIAMI HEAT', 147)),
            ((u'LOS ANGELES CLIPPERS', -190), (u'MEMPHIS GRIZZLIES', 159)),
            ...
        ]
    """
    return filter(lambda x: x is not None,
                  [get_moneyline(game_id) for game_id in get_games()])

def dump_moneyline():
    """
    Args:
        None
    Returns:
        [list]: List of moneyline odds: [
            ((u'SACRAMENTO KINGS', -199), (u'MIAMI HEAT', 147)),
            ((u'LOS ANGELES CLIPPERS', -190), (u'MEMPHIS GRIZZLIES', 159)),
            ...
        ]
    """ 
    for line in run_moneyline():
        ((t_a, o_a), (t_b, o_b)) = line
        t_a, t_b = (Team.objects.get(name=t_a), Team.objects.get(name=t_b))
        ((t1, o1), (t2, o2)) = sorted(((t_a, o_a), (t_b, o_b)),
                                      key=lambda x: x[0].id)
        Odds.update_or_create(
            site='BOOKMAKER',
            type='MONEYLINE',
            timestamp=datetime.datetime.now(),
            team1=t1,
            team2=t2,
            defaults={
                'odds1': o1,
                'odds2': o2
            }
        )
