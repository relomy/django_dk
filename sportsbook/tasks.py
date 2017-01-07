from multiprocessing import Pool

from django.utils import timezone
from celery import shared_task

from nba.models import Team
from sportsbook.models import Odds
from sportsbook.sites.bookmaker.parser import run_moneyline as bm_run_moneyline
from sportsbook.sites.betonline.parser import run_moneyline as bo_run_moneyline

def active_games(
    """
    Checks whether the game is within 4:30-10PM PST.
    """

def dump_moneyline(site, f_moneyline, parallel=False):
    """
    Args:
        site [str]: Website the odds data is from.
        f_moneyline [function]: Moneyline function that returns a list of lines.
    Returns:
        None
    """
    lines = f_moneyline(parallel=parallel)
    for line in lines:
        ((t_a, o_a), (t_b, o_b)) = line
        ((t1, o1), (t2, o2)) = sorted(((t_a, o_a), (t_b, o_b)),
                                      key=lambda x: x[0].id)
        gamestr = Odds.get_gamestr(t1, t2)
        o, _ = Odds.objects.update_or_create(
            site=site,
            type='MONEYLINE',
            timestamp=timezone.now(),
            game=gamestr,
            team1=t1,
            team2=t2,
            defaults={
                'odds1': o1,
                'odds2': o2
            }
        )
        print 'Updated %s' % o

@shared_task
def pull_moneylines():
    try:
        dump_moneyline('BOOKMAKER', bm_run_moneyline, True)
        dump_moneyline('BETONLINE', bo_run_moneyline, True)
        # TODO: Figure out how to do nested pools
        """
        pool = Pool(processes=2)
        pool.apply_async(dump_moneyline, ('BOOKMAKER', bm_run_moneyline, True))
        pool.apply_async(dump_moneyline, ('BETONLINE', bo_run_moneyline, True))
        pool.close()
        pool.join()
        """
    except Exception, e:
        print '[ERROR/tasks.pull_moneylines]: %s' % e
