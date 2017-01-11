def calculate(site1, site2):
    """
    For an arbitrage opportunity to exist, there must be some pair (o1, o2)
    that are opposite positions such that for some fraction of a bet r:
        r * o1 > 1     => r > 1/o1
        (1-r) * o2 > 1 => (1-r) > 1/o2
    This implies:
        1 > 1/o1 + 1/o2
    Given a pair (o1, o2) that maximally satisfies this condition, compute
    r as:
        r * o1 = (1-r) * o2 => r = o2 / (o1+o2)

    NOTE: All odds tuples must be in decimal (European) odds format.

    Args:
        site1 [tuple]: ([int] site1_odds1, [int] site1_odds2)
        site2 [tuple]: ([int] site2_odds1, [int] site2_odds2)
    Returns:
        [tuple]: ([int] 0 if no arb opportunity exists
                        1 to back/back (s1o1/s2o2)
                        2 to back/back (s1o2/s2o1),
                  [float] percentage of the bet to allocate to site1,
                  [float] margin)
    """
    s1o1, s1o2 = site1
    s2o1, s2o2 = site2

    ratio1 = 1.0/s1o1 + 1.0/s2o2
    ratio2 = 1.0/s1o2 + 1.0/s2o1

    if ratio1 < 1.0 and ratio1 < ratio2:
        return (1, s2o2 / (s1o1 + s2o2), s1o1 * s2o2 / (s1o1 + s2o2) - 1)
    elif ratio2 < 1.0:
        return (2, s2o1 / (s1o2 + s2o1), s1o2 * s2o1 / (s1o2 + s2o1) - 1)
    else:
        return (0, 0.0, 0.0)

def calculate_odds(odds1, odds2):
    """
    Args:
        odds1 [Odds]: Odds object to compare.
        odds2 [Odds]: Odds object to compare.
    Returns:
        [tuple]: ([int] 0 if no arb opportunity exists
                        1 to back/back (s1o1/s2o2)
                        2 to back/back (s1o2/s2o1),
                  [float] percentage of the bet to allocate to odds1,
                  [float] margin)
    """
    if (odds1.bet_type != odds2.bet_type or odds1.game != odds2.game
        or odds1.team1 != odds2.team1 or odds1.team2 != odds2.team2):
        return (0, 0.0, 0.0)
    return calculate((odds1.odds1, odds1.odds2), (odds2.odds1, odds2.odds2))
