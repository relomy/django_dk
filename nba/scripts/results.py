import datetime
import logging
import numpy
from django.db import connection
from nba.models import Player, DKContest, DKResult


def print_contestant_results():
    """
    Used to see the average rank of contestants by number of contests entered.
    The hypothesis is people who enter more contests will rank better than
    people who enter fewer contests.

    Prints the following table:
    # Contests entered | Avg % Rank | # People
    """

    QUERY = (
        "SELECT r.name, r.rank, c.dk_id, c.entries"
        "FROM nba_dkcontest AS c JOIN nba_dkresult AS r ON c.id=r.contest_id"
        "ORDER BY c.dk_id, r.rank, r.id"
    )

    contests = set([])

    print("Executing SQL...")
    cursor = connection.cursor()
    cursor.execute(QUERY)
    rows = [row for row in cursor.fetchall()]

    print("Collecting data")
    results = {}
    for row in rows:
        name, rank, contest_id, num_entries = row
        percent = float(row[1]) / num_entries
        if name in results:
            results[name].append((percent, contest_id))
        else:
            results[name] = [(percent, contest_id)]

    print("Aggregating data")
    results_agg = {}
    for key, val in results.iteritems():
        contestant_contests = set([x[1] for x in val])
        avg = sum([x[0] for x in val]) / len(val)
        num_contests = len(contestant_contests)
        num_entries = len(val)
        results_agg[key] = (avg, num_contests, num_entries)
        contests = contests.union(contestant_contests)

    rows_agg = sorted(
        [(k, v[0], v[1], v[2]) for k, v in results_agg.iteritems()], key=lambda x: x[1]
    )

    print("Printing results")
    for i in range(1, len(contests) + 1):
        filtered = [row[1] for row in rows_agg if row[2] == i]
        print("{}\t{:.3f}\t{}".format(i, sum(filtered) / len(filtered), len(filtered)))


def find_top_contestants():
    """
    Used to see the most consistently high scoring contestants.

    Prints the following table:
    # Contests entered | Avg % Rank | # People
    """

    QUERY = (
        "SELECT r.name, r.rank, c.dk_id, c.entries"
        "FROM nba_dkcontest AS c JOIN nba_dkresult AS r ON c.id=r.contest_id"
        "ORDER BY c.dk_id, r.rank, r.id"
    )

    contests = set([])

    print("Executing SQL...")
    cursor = connection.cursor()
    cursor.execute(QUERY)
    rows = [row for row in cursor.fetchall()]

    print("Collecting data")
    results = {}
    for row in rows:
        name, rank, contest_id, num_entries = row
        percent = float(row[1]) / num_entries
        if name in results:
            results[name].append((percent, contest_id))
        else:
            results[name] = [(percent, contest_id)]

    print("Aggregating data")
    results_agg = {}
    for key, val in results.iteritems():
        contestant_contests = set([x[1] for x in val])
        avg = sum([x[0] for x in val]) / len(val)
        num_contests = len(contestant_contests)
        num_entries = len(val)
        results_agg[key] = (avg, num_contests, num_entries)
        contests = contests.union(contestant_contests)

    rows_agg = sorted(
        [(k, v[0], v[1], v[2]) for k, v in results_agg.iteritems()], key=lambda x: x[1]
    )

    print("Printing results")
    for i in range(1, len(contests) + 1):
        filtered = [row[1] for row in rows_agg if row[2] == i]
        print("{}\t{:.3f}\t{}").format(i, sum(filtered) / len(filtered), len(filtered))


def print_player_ownerships(contest_id, percentile=20):
    """
    Used to see the difference between player ownerships in lineups in the top
    @percentile and all other lineups.

    Prints the following table sorted by diff (top own % - bot own %):
    Top Own % (#) | Bottom Own % (#) | Diff | Player | FPTS
    """

    QUERY = (
        "SELECT c.dk_id, c.entries, rank, pg_id, sg_id, sf_id, pf_id, c_id, g_id, f_id, util_id"
        "FROM nba_dkcontest AS c JOIN nba_dkresult AS r ON c.id=r.contest_id"
        "WHERE c.dk_id='{contest_id}'"
    )

    print("Executing SQL...")
    cursor = connection.cursor()
    cursor.execute(QUERY)
    rows = [row for row in cursor.fetchall()]
    if len(rows) == 0:
        print(f"No entries found for contest {contest_id}")
        return
    total_entries = rows[0][1]

    print("Collecting data")
    results_toppercent = {}
    results_botpercent = {}
    for row in rows:
        contest_id, num_entries, rank = (row[0], row[1], row[2])
        player_ids = row[3:]
        dictptr = (
            results_toppercent
            if float(rank) * 100 <= percentile * num_entries
            else results_botpercent
        )
        for player_id in player_ids:
            if player_id in dictptr:
                dictptr[player_id] += 1
            else:
                dictptr[player_id] = 1

    print("Aggregating data")
    results_diff = []
    print(total_entries)
    toptotal = sum(results_toppercent.values()) / 8
    bottotal = sum(results_botpercent.values()) / 8
    for player_id in results_toppercent:
        if player_id in results_botpercent:
            player = Player.objects.get(id=player_id)
            topct = results_toppercent[player_id]
            botct = results_botpercent[player_id]
            toppct = float(topct) / toptotal * 100
            botpct = float(botct) / bottotal * 100
            results_diff.append((player, toppct, topct, botpct, botct, toppct - botpct))
    results_diff = sorted(results_diff, key=lambda x: x[5], reverse=True)

    print(f"Printing results ({total_entries} total)")
    print(
        f"Top {percentile}%% ({toptotal})\tBottom {100-percentile}%% ({bottotal})\tDiff\tPlayer\tFPTS"
    )
    for result in results_diff:
        fpts = result[0].get_stat(
            DKContest.objects.get(dk_id=contest_id).date, "dk_points"
        )
        print(
            "%.2f%% (%d)\t%.2f%% (%d)\t\t%.2f%%\t%s\t%.2f"
            % (result[1], result[2], result[3], result[4], result[5], result[0], fpts)
        )


def print_player_ownerships_timeseries(player_name, percentile=20):
    """
    Used to see the difference between player ownerships in lineups in the top
    @percentile and all other lineups for a single player over time.

    Prints the following table:
    Date | # Entries | Top Own % (#) | Bottom Own % (#) | Total Own % | Diff
    FPTS | Minutes
    """

    def calculate_ownerships(contest):
        query = (
            f"SELECT c.dk_id, c.entries, rank, pg_id, sg_id, sf_id, pf_id, c_id, g_id, f_id, util_id"
            "FROM nba_dkcontest AS c JOIN nba_dkresult AS r ON c.id=r.contest_id"
            "WHERE c.dk_id='{contest.dk_id}'"
        )

        # Executing SQL
        cursor = connection.cursor()
        cursor.execute(query)
        rows = [row for row in cursor.fetchall()]
        if len(rows) == 0:
            print("No entries found for contest {contest.dk_id}")
            return
        total_entries = rows[0][1]

        # Collecting data
        topct = botct = toptotal = bottotal = 0
        for row in rows:
            contest_id, num_entries, rank = (row[0], row[1], row[2])
            player_ids = row[3:]
            is_top = float(rank) * 100 <= percentile * num_entries
            if is_top:
                toptotal += 1
            else:
                bottotal += 1
            for player_id in player_ids:
                if player_id == player.id:
                    if is_top:
                        topct += 1
                    else:
                        botct += 1
        toppct = float(topct) / toptotal * 100
        botpct = float(botct) / bottotal * 100
        totalpct = float(topct + botct) / (toptotal + bottotal) * 100

        # The player didn't play
        if topct == botct and topct == 0:
            return

        # Printing results
        stats = player.get_stats(contest.date, "min", "dk_points")
        print(
            "{}\t{}\t{:.2f}%% ({})\t{:.2f}%% ({})\t{:.2f}%%\t{:.2f}%%\t{:.2f}\t{}".format(
                contest.date,
                toptotal + bottotal,
                toppct,
                topct,
                botpct,
                botct,
                totalpct,
                toppct - botpct,
                stats["dk_points"],
                stats["min"],
            )
        )

    player = Player.get_by_name(player_name)
    print(
        "Contest date\tEntries\tTop % (Entries)\tBot % (Entries)\tTotal %"
        "\tDiff %\tFPTS\tMIN"
    )
    for date in sorted(set([d.date for d in DKContest.objects.all()])):
        contest = DKContest.objects.filter(date=date).order_by("entries").last()
        calculate_ownerships(contest)


def get_weighted_scores(date=datetime.date.today(), days=7, entry_fee=3.0):
    """
    Used to calculate weighted scores for each player using contest data over
    the last @days days. The score is the median dollars made or lost per
    player.
    """
    logger = logging.getLogger()

    def get_contests(days):
        target_date = date - datetime.timedelta(days=days)
        if entry_fee:
            # Be sure not to include the results for the current date in the
            # date query
            contests = DKContest.objects.filter(
                date__gte=target_date, date__lt=date, entry_fee=entry_fee
            )
        else:
            contests = DKContest.objects.filter(date__gte=target_date, date__lt=date)
        return contests.order_by("date", "entry_fee")

    def analyze_results(results, prize_map, entry_fee):
        """
        @param results [list]: List of (rank, pg_id, sg_id, ..., util_id) tups
        @param prize_map [dict]: Mapping of {rank: payout}
        @param entry_fee [float]: Cost to enter the contest
        @return [dict]: {
            [player_id]: [score list]
        }
        """
        scores = {}
        scores_aggregate = {}
        id_fields = [
            "pg_id",
            "sg_id",
            "sf_id",
            "pf_id",
            "c_id",
            "g_id",
            "f_id",
            "util_id",
        ]
        for result in results:
            rank = result[0]
            for player_id in result[1:]:
                if player_id in scores:
                    scores[player_id].append(rank)
                else:
                    scores[player_id] = [rank]
        sorted_keys = sorted(prize_map.keys())
        for player_id, scorelist in scores.iteritems():
            if len(scorelist) * 5000 > float(len(results)):  # > 0.5%
                scores_aggregate[player_id] = sum(
                    [
                        get_weighted_score(x, prize_map, sorted_keys, entry_fee)
                        for x in scorelist
                    ]
                ) / float(len(scorelist))
        return scores_aggregate

    def get_prize_map(prizes):
        prize_map = {}
        for prize in prizes:
            prize_map[prize.lower_rank] = float(prize.payout)
        return prize_map

    def get_weighted_score(index, prize_map, sorted_keys, entry_fee):
        target_rank = index + 1
        for rank in sorted_keys:
            if target_rank <= rank:
                return prize_map[rank] - entry_fee
        return -entry_fee

    def get_results(contest_id):
        query = (
            f"SELECT rank, pg_id, sg_id, sf_id, pf_id, c_id, g_id, f_id, util_id"
            "FROM nba_dkcontest AS c JOIN nba_dkresult AS r ON c.id=r.contest_id"
            "WHERE c.dk_id='{contest_id}'"
        )
        cursor = connection.cursor()
        cursor.execute(query)
        rows = [row for row in cursor.fetchall()]
        return rows

    logger.info("Calculating weighted scores...")
    scores_weighted_all = {}
    for contest in get_contests(days):
        logger.info(contest)
        prize_map = get_prize_map(contest.payouts.all())
        scores_weighted = analyze_results(
            get_results(contest.dk_id), prize_map, float(contest.entry_fee)
        )
        for player_id, score in scores_weighted.iteritems():
            player = Player.objects.get(id=player_id)
            if player in scores_weighted_all:
                scores_weighted_all[player].append(score)
            else:
                scores_weighted_all[player] = [score]
    for player, scores in scores_weighted_all.iteritems():
        scores_weighted_all[player] = numpy.median(scores)
    # Return { player: (score, num data) }
    return scores_weighted_all


def print_weighted_scores(days=7):
    scores = get_weighted_scores(days=days)
    sorted_scores = sorted(
        [(k, v) for k, v in scores.iteritems()], key=lambda x: x[1], reverse=True
    )
    for player, score in sorted_scores:
        print(f"{player}, {score}")
