import datetime
from nba.models import DKContest
from nba.scripts.lineups import set_lineup

def score_lineup(lineup, date):
    return sum([player.get_stat(date, 'dk_points') for player in lineup])

def get_contest_rank(contest, score):
    for result in contest.results.order_by('rank'):
        if score >= result.points:
            return result.rank
    return contest.results.count()

def get_payout(contest, index):
    def get_prize_map(prizes):
        prize_map = {}
        for prize in prizes:
            prize_map[prize.lower_rank] = prize.payout
        return prize_map

    entry_fee = contest.entry_fee
    prize_map = get_prize_map(contest.payouts.all())
    target_rank = index + 1
    for rank in sorted(prize_map.keys()):
        if target_rank <= rank:
            return prize_map[rank] - entry_fee
    return -entry_fee

def run():
    today = datetime.date.today()
    dates = [today - datetime.timedelta(days=i) for i in range(20, -1, -1)]
    results = { 'score': [], 'rank': [], 'payout': [] }
    for date in dates:
        try:
            contest = DKContest.objects.get(date=date, entry_fee=3)
            lineup = set_lineup(date, entry_fee=3)
            score = score_lineup(lineup, date)
            rank = get_contest_rank(contest, score)
            entries = contest.entries
            payout = get_payout(contest, rank)
            if lineup and score: # Also check score because it might try to
                                 # print the results for games that haven't
                                 # happened yet
                print 'VALIDATION RESULTS:'
                print '\tDate:    %s' % date.strftime('%m/%d/%Y')
                print '\tScore:   %.2f' % score
                print '\tRank:    %d' % rank
                print '\tEntries: %d' % entries
                print '\tPayout:  %.2f' % payout
                print ('\tLineup: %s' %
                       '\n\t\t'.join(['%s (%s %s): %.2f'
                                      % (player.full_name,
                                         player.dk_position,
                                         player.get_salary(date),
                                         player.get_stat(date, 'dk_points'))
                                     for player in lineup]))
                results['score'].append(score)
                results['rank'].append(float(rank) / entries)
                results['payout'].append(payout)
        except DKContest.DoesNotExist:
            print 'No contests for %s' % date.strftime('%m/%d/%Y')

    num_contests = len(results['score'])
    avg_score = sum(results['score']) / float(num_contests)
    avg_rank = sum(results['rank']) / float(num_contests)
    total_payout = sum(results['payout'])
    avg_payout = total_payout / num_contests
    print 'SUMMARY:'
    print '\tNumber contests: %d' % num_contests
    print '\tAverage score:   %.2f' % avg_score
    print '\tAverage rank:    %d/100' % round(avg_rank * 100)
    print '\tTotal payout:    %.2f' % total_payout
    print '\tAverage payout:  %.2f' % avg_payout
