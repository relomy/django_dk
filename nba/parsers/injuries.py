from bs4 import BeautifulSoup
import csv
import datetime
import requests
from nba.models import Player, Injury

MONTHS = {
    'Jan': 1, 'Feb': 2, 'Mar': 3, 'Apr': 4, 'May': 5, 'Jun': 6, 'Jul': 7,
    'Aug': 8, 'Sep': 9, 'Oct': 10, 'Nov': 11, 'Dec': 12
}

TODAY = datetime.date.today()

URL = 'http://espn.go.com/nba/injuries'

def run():

    def get_date(datestr):
        """
        Return a date from a datestring. Make sure that it wraps around to the
        previous year if the datestring is greater than the current date (e.g.
        data for Dec 31 when 'today' is Jan 1).
        @param datestr [str]: [Month] [Date] (e.g. 'Nov 11')
        @return [datetime.date]
        """
        month, day = datestr.split(' ')
        month = MONTHS[month]
        year = TODAY.year
        date = datetime.date(year, month, int(day))
        return (date if date <= TODAY
                else datetime.date(year-1, month, int(day)))

    response = requests.get(URL)
    soup = BeautifulSoup(response.text, 'html5lib')
    rows = []
    player = date = status = comment = None
    for tr in soup.find_all('tbody')[0].children:
        row = [td for td in tr if hasattr(tr, 'children')]
        if player and date and status:
            if len(row) == 1 and 'Comment:' in row[0].contents[0].string:
                Injury.objects.update_or_create(
                    player=player,
                    date=date,
                    comment=unicode(row[0].contents[-1]),
                    defaults={ 'status': status }
                )
            else:
                Injury.objects.update_or_create(
                    player=player,
                    date=date,
                    defaults={ 'status': status }
                )
            player = date = status = comment = None
        if len(row) == 3:
            name, status, datestr = [r.string for r in row]
            if name != 'NAME' and status != 'STATUS' and datestr != 'DATE':
                date = get_date(datestr)
                try:
                    player = Player.get_by_name(name)
                except Player.DoesNotExist:
                    print 'Couldn\'t find player %s' % name

