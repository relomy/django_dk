import os
import datetime
import random
from pytz import timezone

from celery import shared_task

from nba.models import Team
from sportsbook.models import Odds

from sportsbook.sites.bookmaker.parser import write_moneylines as bm_write_moneylines
from sportsbook.sites.betonline.parser import write_moneylines as bo_write_moneylines

from sportsbook.sites.betonline.user import login_by_user_number as bo_login

@shared_task
def login(site=''):
    """
    Args:
        site [str]: Website to log into.
    """
    try:
        print '[INFO/tasks.login] Starting task.'
        if datetime.datetime.now(timezone('US/Pacific')).hour not in range(
            int(os.environ['SPORTSBOOK_SCRAPE_MIN_HOUR']),
            int(os.environ['SPORTSBOOK_SCRAPE_MAX_HOUR'])
        ):
            return

        if site == 'betonline':
            bo_login(0)
        else:
            print ('[WARNING/tasks.login]: No procedure defined for'
                   ' site %s.' % site)
    except Exception, e:
        print '[ERROR/tasks.login]: %s' % e
    finally:
        print '[INFO/tasks.login] Successfully exited task.'

@shared_task
def delayed_login(**kwargs):
    interval = random.randint(0, 5 * 60) # Random delay from 0 to 5 minutes
    login.apply_async(countdown=interval, kwargs=kwargs)

@shared_task
def write_moneylines(site='', parallel=False):
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
            bm_write_moneylines(parallel=parallel)
        elif site == 'betonline':
            bo_write_moneylines(parallel=parallel)
        else:
            print ('[WARNING/tasks.write_moneylines]: No procedure defined for'
                   ' site %s.' % site)
    except Exception, e:
        print '[ERROR/tasks.write_moneylines]: %s' % e
    finally:
        print '[INFO/tasks.write_moneylines] Successfully exited task.'
