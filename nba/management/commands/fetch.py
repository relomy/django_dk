import nba.parsers.players as player_parser
import nba.parsers.games as game_parser
from django.core.management.base import BaseCommand, CommandError

class Command(BaseCommand):

    help = \
'''
Fetches player data from NBA.com. Usage:
$ python manage.py fetch
'''

    def add_arguments(self, parser):
        parser.add_argument('--players', '-p',
            action='store_true',
            dest='players',
            default=False,
            help='Fetch player data from NBA.com'
        )
        parser.add_argument('--games', '-g',
            action='store_true',
            dest='games',
            default=False,
            help='Fetch game data from NBA.com'
        )

    def handle(self, *args, **options):
        if options['players']:
            player_parser.run()
        if options['games']:
            game_parser.run()
