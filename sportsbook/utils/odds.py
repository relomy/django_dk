from django.utils import timezone

from sportsbook.models import Odds

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
    ((t_a, o_a), (t_b, o_b)) = odds
    ((t1, o1), (t2, o2)) = sorted(((t_a, o_a), (t_b, o_b)),
                                  key=lambda x: x[0].id)
    gamestr = Odds.get_gamestr(t1, t2)
    o, _ = Odds.objects.update_or_create(
        site=site,
        type='MONEYLINE',
        timestamp=timezone.now(),
        game=gamestr,
        team1=t1,
        team2=t2,
        defaults={
            'odds1': o1,
            'odds2': o2
        }
    )
    print 'Updated %s' % o
