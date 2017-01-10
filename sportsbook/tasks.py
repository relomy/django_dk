import os

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
        print '[INFO/tasks.pull_moneylines] Starting task.'
        if site == 'bookmaker':
            bm_write_moneylines(parallel=True)
        elif site == 'betonline':
            bo_write_moneylines(parallel=True)
        else:
            print ('[WARNING/tasks.pull_moneylines]: No procedure defined for'
                   ' site %s.' % site)
    except Exception, e:
        print '[ERROR/tasks.pull_moneylines]: %s' % e
    finally:
        print '[INFO/tasks.pull_moneylines] Successfully exited task.'
