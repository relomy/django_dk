from __future__ import absolute_import, unicode_literals
import os
from datetime import timedelta
from celery import Celery
from celery.schedules import crontab

# set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'proj.settings')

app = Celery('proj')

# Using a string here means the worker don't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django app configs.
app.autodiscover_tasks()


@app.task(bind=True)
def debug_task(self):
    print('Request: {0!r}'.format(self.request))


# Periodic task schedule
TASK_SCHEDULE = {
    'pull_moneylines': {
        'task': 'sportsbook.tasks.pull_moneylines',
        'schedule': timedelta(minutes=1)
        # Every minute between 4PM and 10PM
        'schedule': crontab(hour='16,17,18,19,20,21', minute='*')
    },
}

# The crontab scheduler defaults to the server's local timezone:
# http://celery.readthedocs.org/en/latest/userguide/
#     periodic-tasks.html#timezones
# https://docs.djangoproject.com/en/1.8/topics/i18n/timezones/
app.conf.update(CELERYBEAT_SCHEDULE=TASK_SCHEDULE)
