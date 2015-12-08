from csv import reader, writer
import datetime
import os
import re
import requests
from nba.models import Player, DKSalary

CSVPATH = 'nba/data/salaries'

def get_next_contest():
    """
    Response format: {
        'SelectedSport': 4,
        # To find the correct contests
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
        # Draft groups are for querying salaries
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

    """
    TODO
    """
    URL = 'https://www.draftkings.com/lobby/getcontests?sport=NBA'
    HEADERS = { 'cookie': os.environ['DK_AUTH_COOKIES'] }

    response = requests.get(URL, headers=HEADERS).json()

def write_salaries_to_db(input_rows, date=datetime.date.today()):
    return_rows = []
    csvreader = reader(input_rows, delimiter=',', quotechar='"')
    for i, row in enumerate(csvreader):
        if i != 0 and len(row) == 6: # Ignore possible empty rows
            pos, player, salary, game, ppg, team = row
            dksalary, _ = DKSalary.objects.get_or_create(
                player=Player.get_by_name(player),
                date=date,
                defaults={ 'salary': int(salary) }
            )
            if dksalary.salary != int(salary):
                print ('Warning: trying to overwrite salary for %s.'
                       ' Ignoring - did not overwrite' % player)
            return_rows.append(row)
    return return_rows

def dump_csvs():
    """
    Writes all existing salary CSVs in the @CSVPATH directory to the database
    """

    FILE_DATETIME_REGEX = r'.*/dk_nba_salaries_([^\.]+).csv'

    files = [os.path.join(CSVPATH, f) for f in os.listdir(CSVPATH)
             if os.path.isfile(os.path.join(CSVPATH, f))]
    for filename in files:
        print 'Writing salaries for %s' % filename
        with open(filename, 'r') as f:
            datestr = re.findall(FILE_DATETIME_REGEX, filename)[0]
            date = datetime.datetime.strptime(datestr, '%Y_%m_%d').date()
            write_salaries_to_db(f, date)

def run(writecsv=True):
    """
    Downloads and unzips the CSV salaries and then populates the database
    """

    def get_salary_csv(draft_group_id, contest_type_id):
        """
        Assume the salaries for each player in different draft groups are the
        same for any given day.
        """
        URL = 'https://www.draftkings.com/lineup/getavailableplayerscsv'
        response = requests.get(URL, headers=HEADERS, params={
            'contestTypeId': contest_type_id,
            'draftGroupId': draft_group_id
        })
        return write_salaries_to_db(response.text.split('\n'),
                                    datetime.date.today())

    def write_csv(rows):
        HEADER_ROW = ['Position', 'Name', 'Salary', 'GameInfo',
                      'AvgPointsPerGame', 'teamAbbrev']
        TODAY = datetime.date.today()
        outfile = ('%s/dk_nba_salaries_%s.csv'
                   % (CSVPATH, TODAY.strftime('%Y_%m_%d')))
        # Remove duplicate rows and sort by salary, then name
        # Lists are unhashable so convert each element to a tuple
        rows = sorted(list(set([tuple(r) for r in rows])),
                      key=lambda x: (-int(x[2]), x[1]))
        print 'Writing salaries to csv %s' % outfile
        with open(outfile, 'w') as f:
            csvwriter = writer(f, delimiter=',', quotechar='"')
            csvwriter.writerow(HEADER_ROW)
            for row in rows:
                csvwriter.writerow(row)

    URL = 'https://www.draftkings.com/lobby/getcontests?sport=NBA'
    HEADERS = { 'cookie': os.environ['DK_AUTH_COOKIES'] }

    response = requests.get(URL, headers=HEADERS).json()
    rows = []
    for dg in response['DraftGroups']:
        print ('Updating salaries for draft group %d, contest type %d'
               % (dg['DraftGroupId'], dg['ContestTypeId']))
        rows += get_salary_csv(dg['DraftGroupId'], dg['ContestTypeId'])
    if writecsv:
        write_csv(rows)

