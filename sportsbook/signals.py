from django.db.models.signals import post_save
from django.dispatch import receiver
from sportsbook.models import Odds
from sportsbook.webhooks import post_to_slack
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

def bet(arb, amount=1.00):
    def round_bet(amount):
        return float('%.2f' % amount)
    def bet_success_str(amount, team, site, odds_dec):
        return ('Successfully bet %.2f on %s @ %s (%.2f|%s)'
                % (amount, team, site, odds_dec, decimal_to_us_str(odds_dec)))
    def bet_failure_str(amount, team, site, odds_dec):
        return ('Failed to bet %.2f on %s @ %s (%.2f|%s)'
                % (amount, team, site, odds_dec, decimal_to_us_str(odds_dec)))

    odds1 = arb.odds1
    odds2 = arb.odds2
    if (odds1.game_id and odds1.prop_id and odds2.game_id and odds2.prop_id
        and arb.option in (1, 2)):
        bettor1 = get_bettor(odds1.site)
        bettor2 = get_bettor(odds2.site)
        if arb.option == 1:
            pass1 = bettor1.bet(odds1.game_id, odds1.prop_id, odds1.pos1,
                                round_bet(amount * arb.percentage),
                                odds=odds1.odds1)
            if pass1:
                pass2 = bettor2.bet(odds2.game_id, odds2.prop_id, odds2.pos2,
                                    round_bet(amount * (1-arb.percentage)),
                                    odds=odds2.odds2)
                if pass2:
                    post_to_slack(bet_success_str(amount * arb.percentage,
                                                  odds1.team1, odds1.site,
                                                  odds1.odds1))
                    post_to_slack(bet_success_str(amount * 1-arb.percentage,
                                                  odds2.team2, odds2.site,
                                                  odds2.odds2))
                else:
                    post_to_slack(bet_failure_str(amount * 1-arb.percentage,
                                                  odds2.team2, odds2.site,
                                                  odds2.odds2))
            else:
                post_to_slack(bet_failure_str(amount * arb.percentage,
                                              odds1.team1, odds1.site,
                                              odds1.odds1))
        elif arb.option == 2:
            pass1 = bettor1.bet(odds1.game_id, odds1.prop_id, odds1.pos2,
                                round_bet(amount * arb.percentage),
                                odds=odds1.odds2)
            if pass1:
                pass2 = bettor2.bet(odds2.game_id, odds2.prop_id, odds2.pos1,
                                    round_bet(amount * (1-arb.percentage)),
                                    odds=odds2.odds1)
                if pass2:
                    post_to_slack(bet_success_str(amount * arb.percentage,
                                                  odds1.team2, odds1.site,
                                                  odds1.odds2))
                    post_to_slack(bet_success_str(amount * 1-arb.percentage,
                                                  odds2.team1, odds2.site,
                                                  odds2.odds1))
                else:
                    post_to_slack(bet_failure_str(amount * 1-arb.percentage,
                                                  odds2.team1, odds2.site,
                                                  odds2.odds1))
            else:
                post_to_slack(bet_failure_str(amount * arb.percentage,
                                              odds1.team2, odds1.site,
                                              odds1.odds2))
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
    post_to_slack(format_arb_list(results))

    for arb in results:
        bet(arb, amount=0.10)
