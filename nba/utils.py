# -*- coding: utf-8 -*-

import datetime
import time

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
            else datetime.date(year-1, month, int(day)))

class Timer:
    @classmethod
    def log_elapsed_time(cls, s, prev_time):
        curr_time = time.time()
        print '[Elapsed time] %s: %f' % (s, curr_time - prev_time)
        return curr_time

# Maps DK player full names to NBA.com full names
DK_NBA_PLAYER_NAME_MAP = {
    'Denis Schroder': 'Dennis Schroder',
    u'José Calderón': 'Jose Calderon'
}
