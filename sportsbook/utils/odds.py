from django.utils import timezone

from sportsbook.models import Odds, Arb
from sportsbook.algs import arb

def us_to_decimal(odds):
    """
    Convert from US format odds (+110, -200, etc.) to decimal odds - the
    multiplier when a bet is won.
    E.g.: +100 -> 2.0, +110 -> 2.10, -200 -> 1.50
    US format odds are the amount won on a 100 stake when positive and the
    stake needed to win 100 when negative. US odds of 100 are an even bet
    (so you double your money).
    Reference: https://en.wikipedia.org/wiki/Sports_betting#Odds

    Args:
        odds [int]: US odds.
    Returns:
        [float]: European (decimal) odds.
    """
    if odds >= 100:
        return odds / 100.0 + 1
    elif odds <= -100:
        return 100.0 / -odds + 1
    else:
        return None

def decimal_to_us(odds):
    """
    Convert from European format odds (1.2, 3.4, etc.) to US odds (+110, -220,
    etc.)
    E.g.: 2.0 -> +100, 2.10 -> +110, 1.50 -> -200
    US format odds are the amount won on a 100 stake when positive and the
    stake needed to win 100 when negative. US odds of 100 are an even bet
    (so you double your money).
    Reference: https://en.wikipedia.org/wiki/Sports_betting#Odds

    Args:
        odds [float]: European (decimal) odds.
    Returns:
        [int]: US odds.
    """
    if odds >= 2.0:
        return int(round((odds - 1) * 100))
    elif odds >= 1.0:
        return int(round(-100.0 / (odds - 1)))
    else:
        return None

def write_moneyline(odds, site):
    """
    Write a pair of odds from a site to the database.

    Args:
        odds [tuple]: ((Team1, Odds1), (Team2, Odds2)), where @Team is a Team
                      object (e.g. <Team: Houston Rockets>) and @Odds is a
                      European odds float (e.g. 1.4).
        site [str]: Website key (e.g. BOOKMAKER).
    Returns:
        None
    """
    if odds:
        ((t_a, o_a), (t_b, o_b)) = odds
        ((t1, o1), (t2, o2)) = sorted(((t_a, o_a), (t_b, o_b)),
                                      key=lambda x: x[0].id)
        gamestr = Odds.get_gamestr(t1, t2)
        o, _ = Odds.objects.update_or_create(
            site=site,
            bet_type='MONEYLINE',
            bet_time=timezone.now(),
            game=gamestr,
            team1=t1,
            team2=t2,
            defaults={
                'odds1': o1,
                'odds2': o2
            }
        )
        print 'Updated %s' % o

def write_arb(odds1, odds2):
    """
    Takes two unordered Odds objects, orders them by timestamp, calculates if
    there is an arb opportunity. If so, writes it to the database.

    Args:
        odds1 [Odds]: Odds object.
        odds2 [Odds]: Odds object.
    Returns:
        None
    """
    (odds1, odds2) = Arb.order_odds((odds1, odds2))
    option, percentage, margin = arb.calculate_odds(odds1, odds2)
    if option in Arb.OPTIONS.values() and margin > 0:
        a, _ = Arb.objects.update_or_create(
            option=option,
            odds1=odds1,
            odds2=odds2,
            defaults={
                'percentage': percentage,
                'margin': margin,
                'delta': odds2.bet_time - odds1.bet_time
            }
        )
        print 'Updated %s' % a
