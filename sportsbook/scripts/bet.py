from sportsbook.models import *
from sportsbook.sites.bookmaker import bettor as bm_bettor
from sportsbook.sites.betonline import bettor as bo_bettor
from sportsbook.webhooks import post_bet_to_slack

def get_bettor(site):
    """
    Args:
        site [str]: Site identifier ('BOOKMAKER', 'BETONLINE', etc.).
    Returns:
        [module]: Corresponding bettor.py module.
    """
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

def bet_arb(arb, amount=1.00):
    def add_bets(b1, b2, arb, amount):
        (b1_bettor, b1_game_id, b1_prop_id, b1_pos, b1_team, b1_odds,
         b1_site) = b1
        (b2_bettor, b2_game_id, b2_prop_id, b2_pos, b2_team, b2_odds,
         b2_site) = b2
        result1 = b1_bettor.add_bet(b1_game_id, b1_prop_id, b1_pos,
                                    round_bet(amount * arb.percentage),
                                    odds=b1_odds)
        result2 = b2_bettor.add_bet(b2_game_id, b2_prop_id, b2_pos,
                                    round_bet(amount * (1-arb.percentage)),
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
        (b1_bettor, b1_game_id, b1_prop_id, b1_pos, b1_team, b1_odds,
         b1_site) = b1
        (b2_bettor, b2_game_id, b2_prop_id, b2_pos, b2_team, b2_odds,
         b2_site) = b2
        result1 = b1_bettor.place_bet(b1_game_id, b1_prop_id, b1_pos,
                                      round_bet(amount * arb.percentage),
                                      odds=b1_odds)
        result2 = b2_bettor.place_bet(b2_game_id, b2_prop_id, b2_pos,
                                      round_bet(amount * (1-arb.percentage)),
                                      odds=b2_odds)
        if result1['success']:
            post_bet_to_slack(
                bet_success_str(amount * arb.percentage, b1_team, b1_site,
                                b1_odds)
            )
        else:
            post_bet_to_slack('Could not post bet on %s: %s'
                              % (b1_site, result1['message']))
        if result2['success']:
            post_bet_to_slack(
                bet_success_str(amount * (1-arb.percentage), b2_team, b2_site,
                                b2_odds)
            )
        else:
            post_bet_to_slack('Could not post bet on %s: %s'
                              % (b2_site, result2['message']))
        return result1['success'] and result2['success']

    def remove_bets(b1, b2, arb, amount):
        (b1_bettor, b1_game_id, b1_prop_id, b1_pos, b1_team, b1_odds,
         b1_site) = b1
        (b2_bettor, b2_game_id, b2_prop_id, b2_pos, b2_team, b2_odds,
         b2_site) = b2
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

    bet_success = False
    odds1 = arb.odds1
    odds2 = arb.odds2
    post_bet_to_slack('Attempting to bet: %s' % arb)
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
                bet_success = place_bets(b1, b2, arb, amount)
            # Always remove bets from bet slip
            remove_bets(b1, b2, arb, amount)
            return bet_success
        elif arb.option == 2:
            b1 = (bettor1, odds1.game_id, odds1.prop_id, odds1.pos2,
                  odds1.team2, odds1.odds2, odds1.site)
            b2 = (bettor2, odds2.game_id, odds2.prop_id, odds2.pos1,
                  odds2.team1, odds2.odds1, odds2.site)
            if add_bets(b1, b2, arb, amount):
                bet_success = place_bets(b1, b2, arb, amount)
            # Always remove bets from bet slip
            remove_bets(b1, b2, arb, amount)
            return bet_success
    else:
        print ('[ERROR/signals.bet] Not enough arb metadata to place bet:'
               ' %s %s %s v %s %s %s\n%s'
               % (odds1.site, odds1.game_id, odds1.prop_id, odds2.site,
                  odds2.game_id, odds2.prop_id, arb))

def bet_odds(odds, amount=1.00, position=0):
    bet_success = False

    bettor = get_bettor(odds.site)
    if position == 1:
        team = odds.team1
        odds_value = odds.odds1
    elif position == 2:
        team = odds.team2
        odds_value = odds.odds2
    else:
        return False

    add_result = bettor.add_bet(odds.game_id, odds.prop_id, position, amount,
                                odds=odds_value)
    if add_result['success']:
        post_bet_to_slack('Added bet to bet slip on %s' % odds.site)
        place_result = bettor.place_bet(odds.game_id, odds.prop_id, position,
                                        amount, odds=odds_value)
        if place_result['success']:
            bet_success = True
            post_bet_to_slack(
                bet_success_str(amount, team, odds.site, odds_value)
            )
        else:
            post_bet_to_slack('Could not post bet on %s: %s'
                              % (odds.site, place_result['message']))
    else:
        post_bet_to_slack('Could not add bet to bet slip on %s: %s'
                          % (odds.site, add_result['message']))
    # Always remove bets from bet slip
    remove_result = bettor.remove_bet(odds.game_id, odds.prop_id, position)
    if remove_result['success']:
        post_bet_to_slack('Successfully removed %s bet from slip' % odds.site)
    else:
        post_bet_to_slack('Could not remove %s from bet slip: %s'
                          % (odds.site, remove_result['message']))
    return bet_success

def bet(instance, **kwargs):
    """
    Args:
        instance [Arb/Odds]: Instance to bet on. There are different procedures
                             defined for different instances (betting on an Arb
                             is different from betting on an Odds object).
    Returns:
        None
    """
    if isinstance(instance, Arb):
        return bet_arb(instance, amount=kwargs['amount'])
    elif isinstance(instance, Odds):
        return bet_odds(instance, amount=kwargs['amount'],
                        position=kwargs['position'])
    else:
        print '[WARNING/scripts.bet]: No bet procedure found for %s' % instance
