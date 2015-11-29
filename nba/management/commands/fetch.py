import nba.parsers.players as players
from django.core.management.base import BaseCommand, CommandError

class Command(BaseCommand):

    help = \
'''
Fetches player data from NBA.com. Usage:
$ python manage.py fetch
'''

    def handle(self, *args, **options):
        players.run()
