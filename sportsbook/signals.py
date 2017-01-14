from django.db.models.signals import post_save
from django.dispatch import receiver
from sportsbook.models import Odds
from sportsbook.webhooks import post_opp_to_slack, post_bet_to_slack
from sportsbook.utils.odds import decimal_to_us_str
from sportsbook.sites.bookmaker import bettor as bm_bettor
from sportsbook.sites.betonline import bettor as bo_bettor

ARB_DELTA = 5 # In seconds
MIN_MARGIN, MAX_MARGIN = (0.00, 1.00)

def format_arb_list(arbs):
    arbs = [arb for arb in arbs
            if arb.margin > MIN_MARGIN and arb.margin < MAX_MARGIN]
    return '\n'.join([arb.__unicode__() for arb in arbs])

def get_bettor(site):
    """TODO: Refactor this"""
    if site == 'BOOKMAKER':
        return bm_bettor
    elif site == 'BETONLINE':
        return bo_bettor
    else:
        return None

def round_bet(amount):
    return float('%.2f' % amount)

def bet_success_str(amount, team, site, odds_dec):
    return ('Successfully bet %.2f on %s @ %s (%.2f|%s)'
            % (amount, team, site, odds_dec, decimal_to_us_str(odds_dec)))

def bet_failure_str(amount, team, site, odds_dec):
    return ('Failed to bet %.2f on %s @ %s (%.2f|%s)'
            % (amount, team, site, odds_dec, decimal_to_us_str(odds_dec)))


def add_bets(b1, b2, arb, amount):
    (b1_bettor, b1_game_id, b1_prop_id, b1_pos, b1_team, b1_odds, b1_site) = b1
    (b2_bettor, b2_game_id, b2_prop_id, b2_pos, b2_team, b2_odds, b2_site) = b2
    result1 = b1_bettor.add_bet(b1_game_id, b1_prop_id, b1_pos,
                                round_bet(amount * arb.percentage),
                                odds=b1_odds)
    result2 = b2_bettor.add_bet(b2_game_id, b2_prop_id, b2_pos,
                                round_bet(amount * arb.percentage),
                                odds=b2_odds)
    if result1['success']:
        post_bet_to_slack('Added bet to bet slip on %s' % b1_site)
    else:
        post_bet_to_slack('Could not add bet to bet slip on %s: %s'
                          % (b1_site, result1['message']))
    if result2['success']:
        post_bet_to_slack('Added bet to bet slip on %s' % b2_site)
    else:
        post_bet_to_slack('Could not add bet to bet slip on %s: %s'
                          % (b2_site, result2['message']))
    return result1['success'] and result2['success']

def place_bets(b1, b2, arb, amount):
    (b1_bettor, b1_game_id, b1_prop_id, b1_pos, b1_team, b1_odds, b1_site) = b1
    (b2_bettor, b2_game_id, b2_prop_id, b2_pos, b2_team, b2_odds, b2_site) = b2
    result1 = b1_bettor.add_bet(b1_game_id, b1_prop_id, b1_pos,
                                round_bet(amount * arb.percentage),
                                odds=b1_odds)
    result2 = b2_bettor.add_bet(b2_game_id, b2_prop_id, b2_pos,
                                round_bet(amount * arb.percentage),
                                odds=b2_odds)
    if result1['success']:
        post_bet_to_slack(
            bet_success_str(amount * arb.percentage, b1_team, b1_site, b1_odds)
        )
    else:
        post_bet_to_slack('Could not post bet on %s: %s'
                          % (b1_site, result1['message']))
    if result2['success']:
        post_bet_to_slack(
            bet_success_str(amount * arb.percentage, b2_team, b2_site, b2_odds)
        )
    else:
        post_bet_to_slack('Could not post bet on %s: %s'
                          % (b2_site, result2['message']))
    return result1['success'] and result2['success']

def remove_bets(b1, b2, arb, amount):
    (b1_bettor, b1_game_id, b1_prop_id, b1_pos, b1_team, b1_odds, b1_site) = b1
    (b2_bettor, b2_game_id, b2_prop_id, b2_pos, b2_team, b2_odds, b2_site) = b2
    result1 = b1_bettor.remove_bet(b1_game_id, b1_prop_id, b1_pos)
    result2 = b2_bettor.remove_bet(b2_game_id, b2_prop_id, b2_pos)
    if result1['success']:
        post_bet_to_slack('Successfully removed %s bet from slip' % b1_site)
    else:
        post_bet_to_slack('Could not remove %s from bet slip: %s'
                          % (b1_site, result1['message']))
    if result2['success']:
        post_bet_to_slack('Successfully removed %s bet from slip' % b2_site)
    else:
        post_bet_to_slack('Could not remove %s from bet slip: %s'
                          % (b2_site, result2['message']))
    return result1['success'] and result2['success']

def bet(arb, amount=1.00):
    odds1 = arb.odds1
    odds2 = arb.odds2
    if (odds1.game_id and odds1.prop_id and odds2.game_id and odds2.prop_id
        and arb.option in (1, 2)):
        bettor1 = get_bettor(odds1.site)
        bettor2 = get_bettor(odds2.site)
        if arb.option == 1:
            b1 = (bettor1, odds1.game_id, odds1.prop_id, odds1.pos1,
                  odds1.team1, odds1.odds1, odds1.site)
            b2 = (bettor2, odds2.game_id, odds2.prop_id, odds2.pos2,
                  odds2.team2, odds2.odds2, odds2.site)
            if add_bets(b1, b2, arb, amount):
                if place_bets(b1, b2, arb, amount):
                    return True # Bet successfully placed
            # Fall through all failures and remove posted
            remove_bets(b1, b2, arb, amount)
            return False
        elif arb.option == 2:
            b1 = (bettor1, odds1.game_id, odds1.prop_id, odds1.pos2,
                  odds1.team2, odds1.odds2, odds1.site)
            b2 = (bettor2, odds2.game_id, odds2.prop_id, odds2.pos1,
                  odds2.team1, odds2.odds1, odds2.site)
            if add_bets(b1, b2, arb, amount):
                if place_bets(b1, b2, arb, amount):
                    return True # Bet successfully placed
            # Fall through all failures and remove posted
            remove_bets(b1, b2, arb, amount)
            return False
    else:
        print ('[ERROR/signals.bet] Not enough arb metadata to place bet:'
               ' %s %s %s v %s %s %s\n%s'
               % (odds1.site, odds1.game_id, odds1.prop_id, odds2.site,
                  odds2.game_id, odds2.prop_id, arb))

@receiver(post_save, sender=Odds, dispatch_uid='sportsbook_calculate_arb')
def calculate_arb(sender, instance, **kwargs):
    """
    Args:
        sender [Odds]: Class of the signal being received.
        instance [Odds]: Model instance of the signal being received.
        kwargs [dict]: Example: {
            'update_fields': None,
            'raw': False,
            'signal': <django.db.models.signals.ModelSignal>,
            'using': 'default',
            'created': False
        }
    Returns:
        None
    """
    results = instance.write_arbs(delta=5)
    post_opp_to_slack(format_arb_list(results))

    for arb in results:
        bet(arb, amount=0.10)
