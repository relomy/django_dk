import csv
from bs4 import BeautifulSoup
import requests
from nba.models import Player, Injury
from nba.utils import get_date_yearless

URL = "http://espn.go.com/nba/injuries"


def run():
    response = requests.get(URL)
    soup = BeautifulSoup(response.text, "html5lib")
    rows = []
    player = date = status = comment = None
    for tr in soup.find_all("tbody")[0].children:
        row = [td for td in tr if hasattr(tr, "children")]
        if player and date and status:
            if len(row) == 1 and "Comment:" in row[0].contents[0].string:
                Injury.objects.update_or_create(
                    player=player,
                    date=date,
                    comment=unicode(row[0].contents[-1]),
                    defaults={"status": status},
                )
            else:
                Injury.objects.update_or_create(
                    player=player, date=date, defaults={"status": status}
                )
            player = date = status = comment = None
        if len(row) == 3:
            name, status, datestr = [r.string for r in row]
            if name != "NAME" and status != "STATUS" and datestr != "DATE":
                date = get_date_yearless(datestr)
                try:
                    player = Player.get_by_name(name)
                except Player.DoesNotExist:
                    print(f"Couldn't find player {name}")
