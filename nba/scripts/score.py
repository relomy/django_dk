"""
Scoring models
"""

import datetime
import numpy
from nba.models import Player, DKContest

def get_contests(from_date, days_back):
    target_date = from_date - datetime.timedelta(days=days_back)
    contests = DKContest.objects.filter(
        date__gte=target_date, date__lt=from_date, entry_fee=3.0
    )
    return contests.order_by('date')

def median_points_per_salary(date=datetime.date.today()):
    min_games_played = 3
    contests = get_contests(date, 10)
    scores = {} # { [player]: [score list] }
    for player in Player.objects.all():
        scores[player] = []
        for contest in contests:
            date = contest.date
            salary = player.get_salary(date)
            points = player.get_dkpoints(date)
            if salary and points != None:
                scores[player].append(points / salary)
    return {
        player: numpy.median(scorelist)
        for player, scorelist in scores.iteritems()
        if len(scorelist) >= min_games_played
    }

