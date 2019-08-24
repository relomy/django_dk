"""
URL: https://www.draftkings.com/lobby/getcontests?sport=NBA
Response format: {
    'SelectedSport': 4,
    # To find the correct contests, see: find_new_contests()
    'Contests': [{
        'id': '16911618',                              # Contest id
        'n': 'NBA $375K Tipoff Special [$50K to 1st]', # Contest name
        'po': 375000,                                  # Total payout
        'm': 143750,                                   # Max entries
        'a': 3.0,                                      # Entry fee
        'sd': '/Date(1449619200000)/'                  # Start date
        'dg': 8014                                     # Draft group
        ... (the rest is unimportant)
    },
    ...
    ],
    # Draft groups are for querying salaries, see: run()
    'DraftGroups': [{
        'DraftGroupId': 8014,
        'ContestTypeId': 5,
        'StartDate': '2015-12-09T00:00:00.0000000Z',
        'StartDateEst': '2015-12-08T19:00:00.0000000',
        'Sport': 'NBA',
        'GameCount': 6,
        'ContestStartTimeSuffix': null,
        'ContestStartTimeType': 0,
        'Games': null
    },
    ...
    ],
    ... (the rest is unimportant)
}
"""

from csv import reader, writer
import datetime
import os
import re
from pytz import timezone
import requests
from nba.models import Player, DKContest, DKSalary

import browsercookie

CSVPATH = "nba/data/salaries"
COOKIES = browsercookie.chrome()


def find_new_contests():
    """
    Maybe this belongs in another module
    """

    def get_pst_from_timestamp(timestamp_str):
        timestamp = float(re.findall("[^\d]*(\d+)[^\d]*", timestamp_str)[0])
        return datetime.datetime.fromtimestamp(
            timestamp / 1000, timezone("America/Los_Angeles")
        )

    def get_largest_contest(contests, entry_fee):
        return sorted(
            [c for c in contests if c["a"] == entry_fee],
            key=lambda x: x["m"],
            reverse=True,
        )[0]

    def get_contests_by_entries(contests, entry_fee, limit):
        return sorted(
            [c for c in contests if c["a"] == entry_fee and c["m"] > limit],
            key=lambda x: x["m"],
            reverse=True,
        )

    URL = "https://www.draftkings.com/lobby/getcontests?sport=NBA"
    HEADERS = {
        "Accept": "*/*",
        "Accept-Encoding": "gzip, deflate, sdch",
        "Accept-Language": "en-US,en;q=0.8",
        "Cache-Control": "no-cache",
        "Connection": "keep-alive",
        # 'Cookie': os.environ['DK_AUTH_COOKIES'],
        "Host": "www.draftkings.com",
        "Pragma": "no-cache",
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
            "AppleWebKit/537.36 (KHTML, like Gecko)"
            "Chrome/76.0.3809.100 Safari/537.36"
        ),
        "X-Requested-With": "XMLHttpRequest",
    }

    response = requests.get(URL, headers=HEADERS, cookies=COOKIES).json()
    contests = [
        get_largest_contest(response["Contests"], 3),
        get_largest_contest(response["Contests"], 0.25),
        get_largest_contest(response["Contests"], 27),
    ] + get_contests_by_entries(response["Contests"], 3, 50000)
    for contest in contests:
        date_time = get_pst_from_timestamp(contest["sd"])
        DKContest.objects.update_or_create(
            dk_id=contest["id"],
            defaults={
                "date": date_time.date(),
                "datetime": date_time,
                "name": contest["n"],
                "total_prizes": contest["po"],
                "entries": contest["m"],
                "entry_fee": contest["a"],
            },
        )


def write_salaries_to_db(input_rows, date=datetime.date.today()):
    return_rows = []
    csvreader = reader(input_rows, delimiter=",", quotechar='"')
    try:
        for i, row in enumerate(csvreader):
            if i != 0 and len(row) == 9:  # Ignore possible empty rows
                pos, name_and_pid, name, pid, rpos, salary, gameinfo, team, ppg = row
                player = Player.get_by_name(name)
                dksalary, _ = DKSalary.objects.get_or_create(
                    player=player, date=date, defaults={"salary": int(salary)}
                )
                player.dk_position = pos
                player.save()
                if dksalary.salary != int(salary):
                    print(
                        "Warning: trying to overwrite salary for %s."
                        " Ignoring - did not overwrite" % player
                    )
                return_rows.append(row)
    except UnicodeEncodeError as e:
        print(e)
        return []
    return return_rows


def dump_csvs():
    """
    Writes all existing salary CSVs in the @CSVPATH directory to the database
    """

    FILE_DATETIME_REGEX = r".*/dk_nba_salaries_([^\.]+).csv"

    files = [
        os.path.join(CSVPATH, f)
        for f in os.listdir(CSVPATH)
        if os.path.isfile(os.path.join(CSVPATH, f))
    ]
    for filename in files:
        print(f"Writing salaries for {filename}")
        with open(filename, "r") as f:
            datestr = re.findall(FILE_DATETIME_REGEX, filename)[0]
            date = datetime.datetime.strptime(datestr, "%Y_%m_%d").date()
            write_salaries_to_db(f, date)


def run(writecsv=True):
    """
    Downloads and unzips the CSV salaries and then populates the database
    """

    def get_salary_date(draft_groups):
        dates = [
            datetime.datetime.strptime(
                dg["StartDateEst"].split("T")[0], "%Y-%m-%d"
            ).date()
            for dg in response["DraftGroups"]
        ]
        date_counts = [(d, dates.count(d)) for d in set(dates)]
        # Get the date from the (date, count) tuple with the most counts
        return sorted(date_counts, key=lambda x: x[1])[-1][0]

    def get_salary_csv(draft_group_id, contest_type_id, date):
        """
        Assume the salaries for each player in different draft groups are the
        same for any given day.
        """
        URL = "https://www.draftkings.com/lineup/getavailableplayerscsv"
        response = requests.get(
            URL,
            headers=HEADERS,
            cookies=COOKIES,
            params={"contestTypeId": contest_type_id, "draftGroupId": draft_group_id},
        )
        # return write_salaries_to_db(response.text.split("\n"), date)
        return write_salaries_to_db(response.text.splitlines(), date)

    def write_csv(rows, date):
        HEADER_ROW = [
            "Position",
            "NameId",
            "Name",
            "Id",
            "RosterPosition",
            "Salary",
            "GameInfo",
            "teamAbbrev",
            "AvgPointsPerGame",
        ]
        outfile = f"{CSVPATH}/dk_nba_salaries_{date:%Y_%m_%d}.csv"
        # Remove duplicate rows and sort by salary, then name
        # Lists are unhashable so convert each element to a tuple
        rows = sorted(
            list(set([tuple(r) for r in rows])), key=lambda x: (-int(x[2]), x[1])
        )
        print(f"Writing salaries to csv {outfile}")
        with open(outfile, "w") as f:
            csvwriter = writer(f, delimiter=",", quotechar='"')
            csvwriter.writerow(HEADER_ROW)
            for row in rows:
                csvwriter.writerow(row)

    URL = "https://www.draftkings.com/lobby/getcontests?sport=NBA"
    HEADERS = {
        "Accept": "*/*",
        "Accept-Encoding": "gzip, deflate, sdch",
        "Accept-Language": "en-US,en;q=0.8",
        "Cache-Control": "no-cache",
        "Connection": "keep-alive",
        # "Cookie": os.environ["DK_AUTH_COOKIES"],
        "Host": "www.draftkings.com",
        "Pragma": "no-cache",
        "User-Agent": (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_5) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/48.0.2564.97 Safari/537.36"
        ),
        "X-Requested-With": "XMLHttpRequest",
    }

    response = requests.get(URL, headers=HEADERS, cookies=COOKIES).json()
    rows_by_date = {}
    for dg in response["DraftGroups"]:
        # dg['StartDateEst'] should be mostly the same for draft groups, (might
        # not be the same for the rare long-running contest) and should be the
        # date we're looking for (game date in US time).
        date = get_salary_date(response["DraftGroups"])
        print(
            "Updating salaries for draft group {}, contest type {}, date {}".format(
                dg["DraftGroupId"], dg["ContestTypeId"], date
            )
        )
        row = get_salary_csv(dg["DraftGroupId"], dg["ContestTypeId"], date)
        if date not in rows_by_date:
            rows_by_date[date] = []
        rows_by_date[date] += row
    if writecsv:
        for date, rows in rows_by_date.iteritems():
            write_csv(rows, date)

