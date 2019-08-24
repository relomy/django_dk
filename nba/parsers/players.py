import datetime
import os
import requests
from time import sleep
from nba.models import Team, Player


def run(season="2018-19", player_name=None):
    def parse_players(player_name=None):
        """
        Format: {
            "resource": "commonallplayers",
            "parameters": {
                "LeagueID": "00",
                "Season": "2015-16",
                "IsOnlyCurrentSeason": 1
            },
            "resultSets": [{
                "name": "CommonAllPlayers",
                "headers": ["PERSON_ID", "DISPLAY_LAST_COMMA_FIRST", ...],
                "rowSet": [
                    [203112, "Acy, Quincy", ...],
                    [203919, "Adams, Jordan", ...],
                    ...
                ]
            }]
        }
        Row format:
            "PERSON_ID": 203112
            "DISPLAY_LAST_COMMA_FIRST": "Acy, Quincy"
            "ROSTERSTATUS": 1
            "FROM_YEAR": "2012"
            "TO_YEAR": "2015"
            "PLAYERCODE": "quincy_acy"
            "TEAM_ID": 1610612758
            "TEAM_CITY": "Sacramento"
            "TEAM_NAME": "Kings"
            "TEAM_ABBREVIATION": "SAC"
            "TEAM_CODE": "kings"
            "GAMES_PLAYED_FLAG": "y"
        Sample response:
        http://stats.nba.com/stats/commonallplayers
            ?IsOnlyCurrentSeason=1&LeagueID=00&Season=2015-16
        """

        def parse_player_name(display_name):
            """'[Last], [First]' -> '[First] [Last]'"""
            name_arr = [x.strip() for x in display_name.split(",")]
            last, first = name_arr[0], name_arr[1:]
            return "{} {}".format(" ".join(first), last)

        URL = "http://stats.nba.com/stats/commonallplayers"
        # 1/25/2016 - NBA.com now requires ordered params
        PARAMS = (("IsOnlyCurrentSeason", 1), ("LeagueID", "00"), ("Season", season))
        # HEADERS = { 'user-agent': os.environ['USER_AGENT'] }
        HEADERS = {"user-agent": os.getenv("USER_AGENT")}

        response = requests.get(URL, params=PARAMS, headers=HEADERS)
        player_ids = []
        json = response.json()["resultSets"][0]["rowSet"]
        for player_data in json:
            player_id, display_name, _, _, _, _, _, team_id, team_city, team_name, team_abbr, _, _, _ = (
                player_data
            )

            if player_name:
                if parse_player_name(display_name) == player_name:
                    player_ids.append(player_id)
            else:
                # only append player if team_id is not blank

                # update team
                if team_id and team_id != "":
                    Team.objects.update_or_create(
                        nba_id=str(team_id),
                        defaults={
                            "name": team_name,
                            "abbr": team_abbr,
                            "city": team_city,
                        },
                    )
                    player_ids.append(player_id)
                else:
                    print(
                        f"Player {display_name} [id: {player_id}] not found on a team (id: {team_id} name: {team_name})"
                    )

        return player_ids

    def parse_player(player_id):
        """
        Format: {
            "resource": "commonallplayers",
            "parameters": {
                "PlayerID": 201939,
                "LeagueID": "00"
            },
            "resultSets": [{
                "name": "CommonPlayerInfo",
                "headers": ["PERSON_ID", "FIRST_NAME", ...],
                "rowSet": [[201939, "Stephen", ...]], # Single row
            }, {
                "name": "PlayerHeadlineStats", # Aggregate PTS, AST, REB, PIE
                "headers": ["PLAYER_ID", "PLAYER_NAME", ...]
                "rowSet": [[201939, "Stephen", ...]], # Single row
            }]
        }
        Row format:
            "PERSON_ID": 201939,
            "FIRST_NAME": "Stephen",
            "LAST_NAME": "Curry",
            "DISPLAY_FIRST_LAST": "Stephen Curry",
            "DISPLAY_LAST_COMMA_FIRST": "Curry, Stephen",
            "DISPLAY_FI_LAST": "S. Curry",
            "BIRTHDATE": "1988-03-14T00:00:00",
            "SCHOOL": "Davidson",
            "COUNTRY": "USA",
            "LAST_AFFILIATION": "Davidson/USA",
            "HEIGHT": "6-3",
            "WEIGHT": "190",
            "SEASON_EXP": 6,
            "JERSEY": "30",
            "POSITION": "Guard",
            "ROSTERSTATUS": "Active",
            "TEAM_ID": 1610612744,
            "TEAM_NAME": "Warriors",
            "TEAM_ABBREVIATION": "GSW",
            "TEAM_CODE": "warriors",
            "TEAM_CITY": "Golden State",
            "PLAYERCODE": "stephen_curry",
            "FROM_YEAR": 2009,
            "TO_YEAR": 2015,
            "DLEAGUE_FLAG": "N",
            "GAMES_PLAYED_FLAG": "Y"
        Sample response:
        http://stats.nba.com/stats/commonplayerinfo?
            LeagueID=00&PlayerID=201939&SeasonType=Regular+Season
        """

        def weight_to_int(weightstr):
            return int(weight) if weightstr else None

        def height_to_int(heightstr):
            """
            @param heightstr [str]: FT-IN (e.g. 6-3)
            @return [int]: Height in inches
            """
            if heightstr:
                feet, inches = [int(x) for x in heightstr.split("-")]
                return feet * 12 + inches
            return None

        def datestr_to_date(d):
            """
            @param d [str]: "YYYY-MM-DDTHH:MM:SS" (e.g. 1988-03-14T00:00:00)
            @return [datetime.date]
            """
            return datetime.datetime.strptime(d, "%Y-%m-%dT%H:%M:%S").date()

        URL = "http://stats.nba.com/stats/commonplayerinfo"
        # 1/25/2016 - NBA.com now requires ordered params
        PARAMS = (
            ("LeagueID", "00"),
            ("PlayerID", player_id),
            ("SeasonType", "Regular Season"),
        )
        HEADERS = {"user-agent": os.environ["USER_AGENT"]}

        response = requests.get(URL, params=PARAMS, headers=HEADERS)
        player_data = response.json()["resultSets"][0]["rowSet"][0]
        player_id, first_name, last_name, _, _, _, birthdate, school, country, _, height, weight, seasons, number, position, _, team_id, _, _, _, _, _, from_year, to_year, _, _, _, _, _, _ = (
            player_data
        )
        print(f"Updating {player_id}")
        p, _ = Player.objects.update_or_create(
            nba_id=player_id,
            defaults={
                "first_name": first_name,
                "last_name": last_name,
                "team": Team.objects.get(nba_id=team_id),
                "position": position,
                "height": height_to_int(height),
                "weight": weight_to_int(weight),
                "birthdate": datestr_to_date(birthdate),
                "school": school,
                "country": country,
                "start_year": from_year,
                "end_year": to_year,
                "seasons": seasons,
            },
        )
        print(f"Updated {p}")

    # player_name=None by default, which gets all player ids
    player_ids = parse_players(player_name=player_name)
    for player_id in player_ids:
        parse_player(player_id)
        sleep(0.75)
