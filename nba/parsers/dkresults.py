from csv import reader
import decimal
import os
import re
import zipfile
import requests
from bs4 import BeautifulSoup
from nba.models import Player, DKContest, DKContestPayout, DKResult
from nba.utils import get_date_yearless

STOP_WORDS = set(['PG', 'SG', 'SF', 'PF', 'C', 'F', 'G', 'UTIL'])

def run(contest_ids=[], contest=True, resultscsv=True, resultsparse=True):
    """
    Downloads and unzips the CSV results and then populates the database
    """
    CSVPATH = 'nba/data/results'

    def dollars_to_decimal(dollarstr):
        return decimal.Decimal(dollarstr.replace('$', '').replace(',', ''))

    def get_contest_data(contest_id):

        def datestr_to_date(datestr):
            """
            @param datestr [str]: "MON DD, H:MM PM EST"
                                  (e.g. "NOV 29, 6:00 PM EST")
            @return [datetime.date]
            """
            return get_date_yearless(datestr.split(',')[0])

        URL = 'https://www.draftkings.com/contest/gamecenter/%s' % contest_id
        HEADERS = { 'cookie': os.environ['DK_AUTH_COOKIES'] }

        response = requests.get(URL, headers=HEADERS)
        soup = BeautifulSoup(response.text, 'html5lib')

        try:
            header = soup.find_all(class_='top')[0].find_all('h4')
            info_header = (soup.find_all(class_='top')[0]
                               .find_all(class_='info-header')[0]
                               .find_all('span'))
            DKContest.objects.update_or_create(dk_id=contest_id, defaults={
                'name': header[0].string,
                'total_prizes': dollars_to_decimal(header[1].string),
                'date': datestr_to_date(info_header[0].string),
                'entries': int(info_header[2].string),
                'positions_paid': int(info_header[4].string)
            })
        except IndexError:
            # This error occurs for old contests whose pages no longer are
            # being served.
            # Traceback:
            # header = soup.find_all(class_='top')[0].find_all('h4')
            # IndexError: list index out of range
            print 'Couldn\'t find DK contest with id %s' % contest_id

    def get_contest_prize_data(contest_id):
        def place_to_number(s):
            return int(re.findall(r'\d+', s)[0])

        URL = 'https://www.draftkings.com/contest/detailspop'
        HEADERS = { 'cookie': os.environ['DK_AUTH_COOKIES'] }
        PARAMS = {
            'contestId': contest_id,
            'showDraftButton': False,
            'defaultToDetails': True,
            'layoutType': 'legacy'
        }
        response = requests.get(URL, headers=HEADERS, params=PARAMS)
        soup = BeautifulSoup(response.text, 'html5lib')

        try:
            payouts = soup.find_all(id='payouts-table')[0].find_all('tr')
            entry_fee = soup.find_all('h2')[0].text.split('|')[2].strip()
            dkcontest = DKContest.objects.get(dk_id=contest_id)
            dkcontest.entry_fee = dollars_to_decimal(entry_fee)
            dkcontest.save()
            for payout in payouts:
                places, payout = [x.string for x in payout.find_all('td')]
                places = [place_to_number(x.strip()) for x in places.split('-')]
                top, bot = ((places[0], places[0]) if len(places) == 1
                            else places)
                DKContestPayout.objects.update_or_create(
                    contest=dkcontest,
                    upper_rank=top,
                    lower_rank=bot,
                    defaults={ 'payout': dollars_to_decimal(payout) }
                )
        except IndexError:
            # See comment in get_contest_data()
            print 'Couldn\'t find DK contest with id %s' % contest_id

    def get_contest_result_data(contest_id):
        url = 'https://www.draftkings.com/contest/gamecenter/%s' % contest_id
        HEADERS = {
            'referer': url,
            'cookie': os.environ['DK_AUTH_COOKIES']
        }

        OUTFILE = 'out.zip'

        def read_response(response):
            print 'Downloading and unzipping file from %s' % response.url
            with open(OUTFILE, 'wb') as f:
                for chunk in response.iter_content(chunk_size=1024):
                    if chunk:
                        f.write(chunk)

        def unzip_data():
            with open(OUTFILE, 'rb') as f:
                z = zipfile.ZipFile(f)
                for name in z.namelist():
                    z.extract(name, CSVPATH)

        try:
            export_url = url.replace('gamecenter', 'exportfullstandingscsv')
            read_response(requests.get(export_url, headers=HEADERS))
            unzip_data()
        except zipfile.BadZipfile:
            print 'Couldn\'t download/extract CSV zip for %s' % contest_id

    def parse_contest_result_csv(contest_id):
        def parse_entry_name(entry_name):
            return entry_name.split()[0]

        def get_player_cached(name, player_cache):
            if name in player_cache:
                result = player_cache[name]
                return result
            else:
                return Player.get_by_name(name)

        player_cache = { p.full_name: p for p in Player.objects.all()
                         if p.full_name }

        contest, _ = DKContest.objects.get_or_create(dk_id=contest_id)
        filename = '%s/contest-standings-%s.csv' % (CSVPATH, contest_id)
        try:
            with open(filename, 'r') as f:
                csvreader = reader(f, delimiter=',', quotechar='"')
                for i, row in enumerate(csvreader):
                    # Rank, EntryId, EntryName, TimeRemaining, Points, Lineup
                    if i != 0:
                        rank, entry_id, entry_name, _, points, lineup = row
                        lineup = lineup.split()
                        for wordidx, word in enumerate(lineup[:]):
                            if word in STOP_WORDS:
                                lineup[wordidx] = '\t'
                        word_list = ' '.join(lineup).split('\t')
                        players = [get_player_cached(word.strip(), player_cache)
                                   for word in ' '.join(lineup).split('\t')
                                   if word.strip()]
                        if players:
                            DKResult.objects.update_or_create(
                                dk_id=entry_id,
                                defaults={
                                    'contest': contest,
                                    'name': parse_entry_name(entry_name),
                                    'rank': rank,
                                    'points': points,
                                    'pg': players[0],
                                    'sg': players[1],
                                    'sf': players[2],
                                    'pf': players[3],
                                    'c': players[4],
                                    'g': players[5],
                                    'f': players[6],
                                    'util': players[7]
                                }
                            )
                    if i % 5000 == 0:
                        print '%d DKResult records created' % i
        except IOError:
            print 'Couldn\'t find CSV results file %s' % filename

    for contest_id in contest_ids:
        if contest:
            get_contest_data(contest_id)
            get_contest_prize_data(contest_id)
        if resultscsv:
            get_contest_result_data(contest_id)
        if resultsparse:
            parse_contest_result_csv(contest_id)
