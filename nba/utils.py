import datetime
import re
import time
from nba.models import DKContest

def get_date_yearless(datestr):
    """
    Return a date from a datestring. Make sure that it wraps around to the
    previous year if the datestring is greater than the current date (e.g.
    data for Dec 31 when 'today' is Jan 1).
    @param datestr [str]: [Month] [Date] (e.g. 'Nov 11')
    @return [datetime.date]
    """
    date = datetime.datetime.strptime(datestr, '%b %d').date()
    year = datetime.date.today().year
    date = date.replace(year=year)
    return (date if date <= datetime.date.today()
            else datetime.date(year-1, date.month, date.day))

def get_contest_ids_from_readme(limit=0, until=None, filter_sharpshooter=False):
    """
    DEPRECATED
    @param limit [int]: Number of results to return, from the most recent
    @param until [str]: Most recent date to consider in the format 'm/d/YYYY'
    @param filter_sharpshooter [bool]: True to filter for Sharpshooter contests
    @return [list]: List of contest ids
    """

    # Defaults to today
    until = until or datetime.date.today().strftime('%m/%d/%Y').lstrip('0')

    # Get the first contest id after each date (the Daily Sharpshooter ids)
    if filter_sharpshooter:
        regex = \
            r'\d{1,2}\/\d{1,2}\/\d{4}\nhttps://www.draftkings.com/[^ ]*/(\d*)'
    else:
        regex = r'https://www.draftkings.com/[^ ]*/(\d*)'

    def strip_text(text):
        left_bound = 'Contest Result URLs'
        right_bound = until
        return text.split(left_bound)[1].split(right_bound)[0]

    with open('README.md') as f:
        text = strip_text(''.join([line for line in f]))
    ids = re.findall(regex, text)
    return ids[-limit:] # Default of 0 returns the entire list

def get_empty_contest_ids():
    """
    Returns a list of contest ids for contests that are missing results data
    """
    contest_ids = []
    today = datetime.date.today()
    last = today - datetime.timedelta(days=7)
    contests = DKContest.objects.filter(date__gte=last)
    for contest in contests:
        num_results = contest.results.count()
        print("{} entries expected for {}, {} found".format(contest.entries, contest.name, num_results))
        if num_results == 0:
            contest_ids.append(contest.dk_id)
    print("Contest ids: {}".format(', '.join(contest_ids)))
    return contest_ids

def get_contest_ids(limit=1, entry_fee=None):
    """
    Returns a list of contest ids for the last @limit days with an optional
    additional @entry_fee filter
    """
    contest_ids = []
    today = datetime.date.today()
    last = today - datetime.timedelta(days=limit)
    contests = (DKContest.objects.filter(date__gte=last, entry_fee=entry_fee)
                if entry_fee else DKContest.objects.filter(date__gte=last))
    contest_ids = [contest.dk_id for contest in contests]
    print("Contest ids: {}".format(', '.join(contest_ids)))
    return contest_ids

class Timer:
    @classmethod
    def log_elapsed_time(cls, s, prev_time):
        curr_time = time.time()
        print("[Elapsed time] {}: {}".format(s, curr_time - prev_time))
        return curr_time


