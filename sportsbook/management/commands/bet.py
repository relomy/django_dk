from django.core.management.base import BaseCommand, CommandError
from sportsbook.models import Odds
from sportsbook.scripts.bet import bet

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
            type=int,
            default=1,
            help='Position to take.'
        )
        parser.add_argument('--amount', '-a',
            action='store',
            dest='amount',
            type=float,
            default=0.10,
            help='Amount to bet.'
        )

    def handle(self, *args, **options):
        odds = (Odds.objects.filter(site=options['site'].upper())
                         .order_by('bet_time')
                         .last())
        bet(odds, amount=options['amount'], position=options['position'])

