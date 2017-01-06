from django.core.management.base import BaseCommand, CommandError
from sportsbook.algs import arb
from sportsbook.sites.bookmaker import parser as bookmaker_parser
from sportsbook.sites.betonline import parser as betonline_parser

def match_odds(list1, list2):
    """
    Teams should be ordered.

    Args:
        list1 [list]: List of moneyline odds from site 1: [
            ((<Team: Sacramento Kings>, 1.2), (<Team: Miami Heat>, 3.5)),
            ((<Team: Chicago Bulls>, 1.9), (<Team: Memphis Grizzlies>, 4.7)),
            ...
        ]
        list2 [list]: List of moneyline odds from site 2: [
            ((<Team: Sacramento Kings>, 1.1), (<Team: Miami Heat>, 4.6)),
            ((<Team: Chicago Bulls>, 2.1), (<Team: Memphis Grizzlies>, 4.2)),
            ...
        ]
    Returns:
        [list]: List of matched odds: [
            ((<Team: Sacramento Kings>, 1.2, 1.1),
             (<Team: Miami Heat>, 3.5, 4.6)),
            ((<Team: Chicago Bulls>, 1.9, 2.1),
             (<Team: Memphis Grizzlies>, 4.7, 4.2)),
            ...
        ]
    """
    results = []
    for game1 in list1:
        for game2 in list2:
            if game1[0][0] == game2[0][0] and game1[1][0] == game2[1][0]:
                results.append((
                    (game1[0][0], game1[0][1], game2[0][1]),
                    (game1[1][0], game1[1][1], game2[1][1])
                ))
    return results

def dump_moneyline(site):
    """
    Args:
        site [str]: Website the odds data is from
    Returns:
        None
    """
    for line in run_moneyline():
        ((t_a, o_a), (t_b, o_b)) = line
        ((t1, o1), (t2, o2)) = sorted(((t_a, o_a), (t_b, o_b)),
                                      key=lambda x: x[0].id)
        gamestr = Team.get_gamestr(t1, t2)
        Odds.update_or_create(
            site=site,
            type='MONEYLINE',
            timestamp=datetime.datetime.now(),
            game=gamestr,
            team1=t1,
            team2=t2,
            defaults={
                'odds1': o1,
                'odds2': o2
            }
        )

class Command(BaseCommand):

    def handle(self, *args, **options):
        bookmaker_odds = bookmaker_parser.run_moneyline()
        betonline_odds = betonline_parser.run_moneyline()
        odds_list = match_odds(bookmaker_odds, betonline_odds)
        for odds in odds_list:
            team1, t1s1, t1s2 = odds[0]
            team2, t2s1, t2s2 = odds[1]
            opt, percentage, margin = arb.calculate((t1s1, t2s1), (t1s2, t2s2))
            if opt == 1:
                print 'Site 1, %s: %.2f @ %.2f' % (team1, percentage, t1s1)
                print 'Site 2, %s: %.2f @ %.2f' % (team2, 1-percentage, t2s2)
                print 'Margin: %2f' % margin
            elif opt == 2:
                print 'Site 1, %s: %.2f @ %.2f' % (team2, percentage, t2s1)
                print 'Site 2, %s: %.2f @ %.2f' % (team1, 1-percentage, t1s2)
                print 'Margin: %2f' % margin

