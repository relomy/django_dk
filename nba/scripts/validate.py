import datetime
from nba.models import DKContest


def score_lineup(lineup, date):
    return sum([player.get_dkpoints(date) for player in lineup])


def get_contest_rank(contest, score):
    for result in contest.results.order_by("rank"):
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


def run(score_model, lineup_alg):
    """
    @score_model [function]: Scoring model
    @lineup_alg [function]: Lineup generation algorithm
    """
    today = datetime.date.today()
    dates = [today - datetime.timedelta(days=i) for i in range(20, -1, -1)]
    results = {"score": [], "rank": [], "payout": []}
    for date in dates:
        try:
            print("Getting contest data")
            contest = DKContest.objects.get(date=date, entry_fee=3)
            print("Scoring model")
            model_scores = score_model(date)
            print("Setting lineup")
            lineup = lineup_alg(model_scores, date=date)
            print("Scoring lineup")
            score = score_lineup(lineup, date)
            rank = get_contest_rank(contest, score)
            entries = contest.entries
            payout = get_payout(contest, rank)
            if lineup and score:  # Also check score because it might try to
                # print the results for games that haven't
                # happened yet
                print("VALIDATION RESULTS:")
                print("\tDate:    {}".format(date.strftime("%m/%d/%Y")))
                print("\tScore:   {:.2f}".format(score))
                print("\tRank:    {}".format(rank))
                print("\tEntries: {}".format(entries))
                print("\tPayout:  {:.2f}".format(payout))
                # lol what is this
                print(
                    "\tLineup: {}".format(
                        "\n\t\t".join(
                            [
                                "{} ({} {}): {:.2f}".format(
                                    (
                                        player.full_name,
                                        player.dk_position,
                                        player.get_salary(date),
                                        player.get_dkpoints(date),
                                    )
                                )
                                for player in lineup
                            ]
                        )
                    )
                )
                results["score"].append(score)
                results["rank"].append(float(rank) / entries)
                results["payout"].append(payout)
        except DKContest.DoesNotExist:
            print("No contests for {}".format(date.strftime("%m/%d/%Y")))

    num_contests = len(results["score"])
    avg_score = sum(results["score"]) / float(num_contests)
    avg_rank = sum(results["rank"]) / float(num_contests)
    total_payout = sum(results["payout"])
    avg_payout = total_payout / num_contests
    print("SUMMARY:")
    print("\tNumber contests: {}".format(num_contests))
    print("\tAverage score:   {:.2f}".format(avg_score))
    print("\tAverage rank:    {}/100".format(round(avg_rank * 100)))
    print("\tTotal payout:    {:.2f}".format(total_payout))
    print("\tAverage payout:  {:.2f}".format(avg_payout))
