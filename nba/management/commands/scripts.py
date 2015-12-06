import nba.scripts.results as results_scripts
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

    def handle(self, *args, **options):
        if options['contestants']:
            results_scripts.contestant_results()
        if options['ownerships_contest']:
            for contest_id in options['ownerships_contest']:
                contest = DKContest.objects.get(dk_id=contest_id)
                print '=================='
                print contest.dk_id, contest.date, contest.name
                results_scripts.player_ownerships(
                    contest.dk_id, percentile=options['percentile']
                )
        if options['ownerships_contest_all']:
            for contest in DKContest.objects.all().order_by('dk_id'):
                print '=================='
                print contest.dk_id, contest.date, contest.name
                results_scripts.player_ownerships(
                    contest.dk_id, percentile=options['percentile']
                )
        if options['ownerships_player']:
            results_scripts.player_ownerships_timeseries(
                options['ownerships_player'], percentile=options['percentile']
            )
        if options['ownerships_player_all']:
            for player in (Player.objects.all()
                                         .order_by('last_name', 'first_name')):
                print player.full_name
                results_scripts.player_ownerships_timeseries(
                    player.full_name, percentile=options['percentile']
                )
