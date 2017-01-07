"""
Runs celery tasks defined in sportsbook.tasks. Used to test periodic tasks or
run one-off instances.
"""

from django.core.management.base import BaseCommand, CommandError
from sportsbook import tasks

class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('--name', '-n',
            action='store',
            dest='name',
            default='',
            help='Name of the task to run.'
        )
        parser.add_argument('--apply', '-a',
            action='store_true',
            dest='apply',
            default=False,
            help=('Whether to call apply() on the function. Helpful when'
                  ' debuggins (prints stack traces.')
        )

    def handle(self, *args, **options):
        if options['name']:
            try:
                if callable(getattr(tasks, options['name'])):
                    if options['apply']:
                        getattr(tasks, options['name']).apply()
                    else:
                        getattr(tasks, options['name'])()
                else:
                    print 'Task with name %s is not callable' % options['name']
            except AttributeError, e:
                print 'No task found with name: %s' % options['name']
