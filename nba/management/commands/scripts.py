import logging
import nba.scripts.results as result_scripts
import nba.scripts.lineups as lineup_scripts
import nba.scripts.score as score_scripts
import nba.scripts.validate as validation_scripts
from nba.models import Player, DKContest
from django.core.management.base import BaseCommand, CommandError

class Command(BaseCommand):

    help = \
'''
Executes arbitrary scripts. Usage:
$ python manage.py scripts
'''

    def add_arguments(self, parser):
        parser.add_argument('--contestants', '-c',
            action='store_true',
            dest='contestants',
            default=False,
            help='Compare contestant frequency vs standings'
        )
        parser.add_argument('--ownerships-contest', '-oc',
            action='store',
            nargs='+',
            dest='ownerships_contest',
            default=False,
            help='Compare player ownership percentages over multiple contests'
        )
        parser.add_argument('--ownerships-contest-all', '-oca',
            action='store_true',
            dest='ownerships_contest_all',
            default=False,
            help='Compare player ownership percentages over all contests'
        )
        parser.add_argument('--ownerships-player', '-op',
            action='store',
            dest='ownerships_player',
            default=False,
            help='Compare player ownership percentages by player'
        )
        parser.add_argument('--ownerships-player-all', '-opa',
            action='store_true',
            dest='ownerships_player_all',
            default=False,
            help='Compare player ownership percentages for all players'
        )
        parser.add_argument('--percentile', '-p',
            action='store',
            type=int,
            dest='percentile',
            default=50,
            help=('Percentile to split the data (cohort level - used in'
                  ' ownerships-player and ownerships-contest')
        )
        parser.add_argument('--weighted-scores', '-ws',
            action='store_true',
            dest='weighted_scores',
            default=False,
            help='Compare weighted scores ($ made/player) for all players'
        )
        parser.add_argument('--score-points-per-salary', '-spps',
            action='store_true',
            dest='score_points_per_salary',
            default=False,
            help='Create a score mapping'
        )
        parser.add_argument('--score-linear-regression', '-slr',
            action='store_true',
            dest='score_linear_regression',
            default=False,
            help='Create a score mapping using linear regression'
        )
        parser.add_argument('--lineup', '-l',
            action='store_true',
            dest='lineup',
            default=False,
            help='Generate lineups'
        )
        parser.add_argument('--validate', '-val',
            action='store_true',
            dest='validate',
            default=False,
            help='Validate lineup generation model'
        )
        parser.add_argument('--info', '-i',
            action='store_true',
            dest='info',
            default=False,
            help='Validate lineup generation model'
        )

    def handle(self, *args, **options):
        if options['info']:
            logging.basicConfig(level=logging.INFO, format='%(message)s')

        if options['contestants']:
            result_scripts.print_contestant_results()
        if options['ownerships_contest']:
            for contest_id in options['ownerships_contest']:
                contest = DKContest.objects.get(dk_id=contest_id)
                print '=================='
                print contest.dk_id, contest.date, contest.name
                result_scripts.print_player_ownerships(
                    contest.dk_id, percentile=options['percentile']
                )
        if options['ownerships_contest_all']:
            for contest in DKContest.objects.all().order_by('dk_id'):
                print '=================='
                print contest.dk_id, contest.date, contest.name
                result_scripts.print_player_ownerships(
                    contest.dk_id, percentile=options['percentile']
                )
        if options['ownerships_player']:
            result_scripts.print_player_ownerships_timeseries(
                options['ownerships_player'], percentile=options['percentile']
            )
        if options['ownerships_player_all']:
            for player in (Player.objects.all()
                                         .order_by('last_name', 'first_name')):
                print player.full_name
                result_scripts.print_player_ownerships_timeseries(
                    player.full_name, percentile=options['percentile']
                )

        if options['lineup']:
            if options['weighted_scores']:
                lineup_scripts.generate(result_scripts.get_weighted_scores())
            elif options['score_points_per_salary']:
                lineup_scripts.generate(
                    score_scripts.median_points_per_salary()
                )
        if options['validate']:
            if options['weighted_scores']:
                validation_scripts.run(result_scripts.get_weighted_scores,
                                       lineup_scripts.generate)
            elif options['score_points_per_salary']:
                validation_scripts.run(score_scripts.median_points_per_salary,
                                       lineup_scripts.generate)
            elif options['score_linear_regression']:
                validation_scripts.run(score_scripts.linear_regression,
                                       lineup_scripts.generate)

