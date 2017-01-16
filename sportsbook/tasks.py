import os
import datetime
from pytz import timezone

from celery import shared_task

from nba.models import Team
from sportsbook.models import Odds

from sportsbook.sites.bookmaker.parser import write_moneylines as bm_write_moneylines
from sportsbook.sites.betonline.parser import write_moneylines as bo_write_moneylines

@shared_task
def write_moneylines(site=''):
    """
    Args:
        site [str]: Website to pull moneyline odds from.
    """
    try:
        print '[INFO/tasks.write_moneylines] Starting task.'
        if datetime.datetime.now(timezone('US/Pacific')).hour not in range(
            int(os.environ['SPORTSBOOK_SCRAPE_MIN_HOUR']),
            int(os.environ['SPORTSBOOK_SCRAPE_MAX_HOUR'])
        ):
            return

        if site == 'bookmaker':
            bm_write_moneylines(parallel=False)
        elif site == 'betonline':
            bo_write_moneylines(parallel=False)
        else:
            print ('[WARNING/tasks.write_moneylines]: No procedure defined for'
                   ' site %s.' % site)
    except Exception, e:
        print '[ERROR/tasks.write_moneylines]: %s' % e
    finally:
        print '[INFO/tasks.write_moneylines] Successfully exited task.'
