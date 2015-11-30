import nba.parsers.players as player_parser
import nba.parsers.games as game_parser
import nba.parsers.injuries as injury_parser
import nba.parsers.dkresults as dkresults_parser
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
        parser.add_argument('--injuries', '-i',
            action='store_true',
            dest='injuries',
            default=False,
            help='Fetch injury data from ESPN.com'
        )
        parser.add_argument('--dk-results', '-r',
            action='store',
            nargs='+',
            dest='dk_results',
            default=False,
            help='Fetch contest result data from draftkings.com'
        )

    def handle(self, *args, **options):
        if options['players']:
            player_parser.run()
        if options['games']:
            game_parser.run()
        if options['injuries']:
            injury_parser.run()
        if options['dk_results']:
            dkresults_parser.run(
                contest_ids=options['dk_results'],
                contest=True, resultscsv=False, resultsparse=True
            )
