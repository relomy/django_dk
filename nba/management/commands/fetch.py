import nba.parsers.players as player_parser
import nba.parsers.games as game_parser
import nba.parsers.injuries as injury_parser
import nba.parsers.dkresults as dkresults_parser
from nba.utils import get_contest_ids
from django.core.management.base import BaseCommand, CommandError

class Command(BaseCommand):

    CURR_SEASON = '2015-16'

    help = \
'''
Fetches player data from NBA.com. Usage:
$ python manage.py fetch
'''

    def add_arguments(self, parser):
        parser.add_argument('--players', '-p',
            action='store',
            dest='players',
            default=False,
            help=('Fetch player data from NBA.com'
                  ' (curr for current season)')
        )
        parser.add_argument('--games', '-g',
            action='store',
            dest='games',
            default=False,
            help=('Fetch game data from NBA.com for a season'
                  ' (curr for current season)')
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
            help='Fetch contest result data from draftkings.com by id'
        )
        parser.add_argument('--dk-results-limit', '-rl',
            action='store',
            type=int,
            dest='dk_results_limit',
            default=1,
            help='Fetch contest result data from draftkings.com by previous'
        )
        parser.add_argument('--dk-results-contest', '-dkrcontest',
            action='store_true',
            dest='dk_results_contest',
            default=False,
            help='Fetch contest metadata'
        )
        parser.add_argument('--dk-results-csv', '-dkrcsv',
            action='store_true',
            dest='dk_results_csv',
            default=False,
            help='Fetch contest results csv'
        )
        parser.add_argument('--dk-results-parse', '-dkrparse',
            action='store_true',
            dest='dk_results_parse',
            default=False,
            help='Dump the contest results csv into the database'
        )
        parser.add_argument('--update', '-u',
            action='store_true',
            dest='update',
            default=False,
            help='Update game, injury, and contest result data'
        )

    def handle(self, *args, **options):
        if options['update']:
            game_parser.run('2015-16')
            injury_parser.run()
            dkresults_parser.run(
                contest_ids=get_contest_ids(limit=1),
                contest=True, resultscsv=True, resultsparse=True
            )
        else:
            if options['players']:
                if options['players'] == 'curr':
                    player_parser.run(self.CURR_SEASON)
                else:
                    player_parser.run(options['players'])
            if options['games']:
                if options['games'] == 'curr':
                    game_parser.run(self.CURR_SEASON)
                else:
                    game_parser.run(options['games'])
            if options['injuries']:
                injury_parser.run()
            if options['dk_results']:
                dkresults_parser.run(
                    contest_ids=options['dk_results'],
                    contest=options['dk_results_contest'],
                    resultscsv=options['dk_results_csv'],
                    resultsparse=options['dk_results_parse']
                )
            if options['dk_results_limit']:
                dkresults_parser.run(
                    contest_ids=get_contest_ids(options['dk_results_limit']),
                    contest=options['dk_results_contest'],
                    resultscsv=options['dk_results_csv'],
                    resultsparse=options['dk_results_parse']
                )

