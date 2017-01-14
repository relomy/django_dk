from django.core.management.base import BaseCommand, CommandError
from sportsbook.models import Odds
from sportsbook.sites.bookmaker import bettor as bm_bettor
from sportsbook.sites.betonline import bettor as bo_bettor

def get_bettor(site):
    """TODO: Refactor this"""
    site = site.upper()
    if site == 'BOOKMAKER':
        return bm_bettor
    elif site == 'BETONLINE':
        return bo_bettor
    else:
        return None

class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('--site', '-s',
            action='store',
            dest='site',
            default='betonline',
            help='Name of the site to bet on.'
        )
        parser.add_argument('--position', '-p',
            action='store',
            dest='position',
            default=1,
            help='Position to take.'
        )
        parser.add_argument('--amount', '-a',
            action='store',
            dest='amount',
            default=0.10,
            help='Amount to bet.'
        )

    def handle(self, *args, **options):
        odds = (Odds.objects.filter(site=options['site'].upper())
                         .order_by('bet_time')
                         .last())
        bettor = get_bettor(options['site'])
        odds_amount = odds.odds1 if options['position'] == 1 else odds.odds2
        bettor.bet(odds.game_id, odds.prop_id, options['position'],
                   options['amount'], odds=odds_amount)

