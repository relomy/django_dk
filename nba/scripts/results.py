from django.db import connection
from nba.models import Player, DKContest

def contestant_results():
    """
    Used to see the average rank of contestants by number of contests entered.
    The hypothesis is people who enter more contests will rank better than
    people who enter fewer contests.

    Prints the following table:
    # Contests entered | Avg % Rank | # People
    """

    QUERY = '''
SELECT r.name, r.rank, c.dk_id, c.entries
FROM nba_dkcontest AS c JOIN nba_dkresult AS r ON c.id=r.contest_id
ORDER BY c.dk_id, r.rank, r.id
'''

    contests = set([])

    print 'Executing SQL...'
    cursor = connection.cursor()
    cursor.execute(QUERY)
    rows = [row for row in cursor.fetchall()]

    print 'Collecting data'
    results = {}
    for row in rows:
        name, rank, contest_id, num_entries = row
        percent = float(row[1]) / num_entries
        if name in results:
            results[name].append((percent, contest_id))
        else:
            results[name] = [(percent, contest_id)]

    print 'Aggregating data'
    results_agg = {}
    for key, val in results.iteritems():
        contestant_contests = set([x[1] for x in val])
        avg = sum([x[0] for x in val]) / len(val)
        num_contests = len(contestant_contests)
        num_entries = len(val)
        results_agg[key] = (avg, num_contests, num_entries)
        contests = contests.union(contestant_contests)

    rows_agg = sorted(
        [(k, v[0], v[1], v[2]) for k, v in results_agg.iteritems()],
        key=lambda x: x[1]
    )

    print 'Printing results'
    for i in range(1, len(contests)+1):
        filtered = [row[1] for row in rows_agg if row[2] == i]
        print '%d\t%.3f\t%d' % (i, sum(filtered) / len(filtered), len(filtered))


def player_ownerships(contest_id, percentile=20):
    """
    Used to see the difference between player ownerships in lineups in the top
    @percentile and all other lineups.

    Prints the following table sorted by diff (top own % - bot own %):
    Top Own % (#) | Bottom Own % (#) | Diff | Player | FPTS
    """

    QUERY = '''
SELECT c.dk_id, c.entries, rank, pg_id, sg_id, sf_id, pf_id, c_id, g_id, f_id,
    util_id
FROM nba_dkcontest AS c JOIN nba_dkresult AS r ON c.id=r.contest_id
WHERE c.dk_id='%s'
''' % contest_id

    print 'Executing SQL...'
    cursor = connection.cursor()
    cursor.execute(QUERY)
    rows = [row for row in cursor.fetchall()]
    if len(rows) == 0:
        print 'No entries found for contest %s' % contest_id
        return
    total_entries = rows[0][1]

    print 'Collecting data'
    results_toppercent = {}
    results_botpercent = {}
    for row in rows:
        contest_id, num_entries, rank = (row[0], row[1], row[2])
        player_ids = row[3:]
        dictptr = (results_toppercent
                   if float(rank) * 100 <= percentile * num_entries
                   else results_botpercent)
        for player_id in player_ids:
            if player_id in dictptr:
                dictptr[player_id] += 1
            else:
                dictptr[player_id] = 1

    print 'Aggregating data'
    results_diff = []
    print total_entries
    toptotal = sum(results_toppercent.values()) / 8
    bottotal = sum(results_botpercent.values()) / 8
    for player_id in results_toppercent:
        if player_id in results_botpercent:
            player = Player.objects.get(id=player_id)
            topct = results_toppercent[player_id]
            botct = results_botpercent[player_id]
            toppct = float(topct) / toptotal * 100
            botpct = float(botct) / bottotal * 100
            results_diff.append(
                (player, toppct, topct, botpct, botct, toppct - botpct)
            )
    results_diff = sorted(results_diff, key=lambda x: x[5], reverse=True)

    print 'Printing results (%d total)' % total_entries
    print ('Top %d%% (%s)\tBottom %d%% (%s)\tDiff\tPlayer\tFPTS'
           % (percentile, toptotal, 100-percentile, bottotal))
    for result in results_diff:
        fpts = result[0].get_stat(DKContest.objects.get(dk_id=contest_id).date,
                                  'dk_points')
        print ('%.2f%% (%d)\t%.2f%% (%d)\t\t%.2f%%\t%s\t%.2f'
               % (result[1], result[2], result[3], result[4], result[5],
                  result[0], fpts))

def player_ownerships_timeseries(player_name, percentile=20):
    """
    Used to see the difference between player ownerships in lineups in the top
    @percentile and all other lineups for a single player over time.

    Prints the following table:
    Date | # Entries | Top Own % (#) | Bottom Own % (#) | Total Own % | Diff
    FPTS | Minutes
    """

    def calculate_ownerships(contest):
        query = '''
SELECT c.dk_id, c.entries, rank, pg_id, sg_id, sf_id, pf_id, c_id, g_id, f_id,
    util_id
FROM nba_dkcontest AS c JOIN nba_dkresult AS r ON c.id=r.contest_id
WHERE c.dk_id='%s'
''' % contest.dk_id

        # Executing SQL
        cursor = connection.cursor()
        cursor.execute(query)
        rows = [row for row in cursor.fetchall()]
        if len(rows) == 0:
            print 'No entries found for contest %s' % contest.dk_id
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
        stats = player.get_stats(contest.date, 'min', 'dk_points')
        print ('%s\t%d\t%.2f%% (%d)\t%.2f%% (%d)\t%.2f%%\t%.2f%%\t%.2f\t%d'
               % (contest.date, toptotal + bottotal, toppct, topct, botpct,
                  botct, totalpct, toppct - botpct, stats['dk_points'],
                  stats['min']))

    player = Player.get_by_name(player_name)
    print ('Contest date\tEntries\tTop % (Entries)\tBot % (Entries)\tTotal %'
           '\tDiff %\tFPTS\tMIN')
    for date in sorted(set([d.date for d in DKContest.objects.all()])):
        contest = DKContest.objects.filter(date=date).order_by('entries').last()
        calculate_ownerships(contest)
