import datetime
import os
import requests
from nba.models import Team, Player, Game, GameStats

def run(season='2015-16'):

    def parse_games(player_id, season):
        """
        Format: {
            "resource": "playergamelog",
            "parameters": {
                "PlayerID": 201939,
                "LeagueID": "00",
                "Season": "2015-16",
                "SeasonType": "Regular Season"
            },
            "resultSets": [{
                "name": "PlayerGameLog",
                "headers": ["SEASON_ID", "Player_ID", "Game_ID", ...],
                "rowSet": [
                    [22015, "201939", "0021500236", ...],
                    [22015, "201939", "0021500214", ...],
                    ...
                ]
            }]
        }
,
        Row format:
            "SEASON_ID": "22015"
            "Player_ID": 201939
            "Game_ID": "0021500236"
            "GAME_DATE": "NOV 27, 2015"
            "MATCHUP": "GSW @ PHX"
            "WL": "W"
            "MIN": 31
            "FGM": 11
            "FGA": 20
            "FG_PCT": 0.55
            "FG3M": 9
            "FG3A": 16
            "FG3_PCT": 0.563
            "FTM": 10
            "FTA": 11
            "FT_PCT": 0.909
            "OREB": 1
            "DREB": 5
            "REB": 6
            "AST": 8
            "STL": 2
            "BLK": 0
            "TOV": 6
            "PF": 2
            "PTS": 41
            "PLUS_MINUS": 27
            "VIDEO_AVAILABLE": 1
        Sample response:
            http://stats.nba.com/stats/playergamelog?LeagueID=00
                &PlayerID=201939&Season=2015-16&SeasonType=Regular+Season
        """

        def teamstr_to_teams(teamstr):
            """
            @param heightstr [str]: AWAY @ HOME (e.g. GSW @ PHX)
            @return [tuple]: Height in inches
            """
            if teamstr and '@' in teamstr:
                away, home = [Team.objects.get(abbr=team.strip())
                              for team in teamstr.split('@')]
                return (home, away)
            elif teamstr and 'vs.' in teamstr:
                home, away = [Team.objects.get(abbr=team.strip())
                              for team in teamstr.split('vs.')]
                return (home, away)
            return (None, None)

        def datestr_to_date(d):
            """
            @param d [str]: "MON D, YYYY" (e.g. JAN 1, 2016)
            @return [datetime.date]
            """
            return datetime.datetime.strptime(d, '%b %d, %Y').date()

        URL = 'http://stats.nba.com/stats/playergamelog'
        PARAMS = {
            'PlayerID': player_id,
            'LeagueID': '00',
            'Season': season,
            'SeasonType': 'Regular Season'
        }
        HEADERS = { 'user-agent': os.environ['USER_AGENT'] }

        response = requests.get(URL, params=PARAMS, headers=HEADERS)
        for game_data in response.json()['resultSets'][0]['rowSet']:
            season_id, player_id, game_id, date, matchup, _, minutes, fgm, \
                fga, _, fg3m, fg3a, _, ftm, fta, _, oreb, dreb, reb, ast, \
                stl, blk, tov, pf, pts, plus_minus, _ = game_data
            print 'Updating %s %s' % (player_id, game_id)
            home, away = teamstr_to_teams(matchup)
            if home and away:
                g, _ = Game.objects.update_or_create(nba_id=game_id, defaults={
                    'home_team': home,
                    'away_team': away,
                    'date': datestr_to_date(date),
                    'season_id': season_id,
                })

                gs, _ = GameStats.objects.update_or_create(
                    game=g,
                    player=Player.objects.get(nba_id=player_id),
                    defaults={
                        'min': minutes, 'fgm': fgm, 'fga': fga, 'fg3m': fg3m,
                        'fg3a': fg3a, 'ftm': ftm, 'fta': fta, 'oreb': oreb,
                        'dreb': dreb, 'reb': reb, 'ast': ast, 'stl': stl,
                        'blk': blk, 'tov': tov, 'pf': pf, 'pts': pts,
                        'plus_minus': plus_minus
                    }
                )
                print 'Updated %s, %s' % (g, gs)
            else:
                print 'Couldn\'t parse game %s' % matchup

    # TODO: Filter for active players
    player_ids = [p.nba_id for p in Player.objects.all()]
    for player_id in player_ids:
        parse_games(player_id, season)
