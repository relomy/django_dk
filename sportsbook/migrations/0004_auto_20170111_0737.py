# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import datetime
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('sportsbook', '0003_auto_20170106_2321'),
    ]

    operations = [
        migrations.RenameField(
            model_name='odds',
            old_name='type',
            new_name='bet_type',
        ),
        migrations.RenameField(
            model_name='odds',
            old_name='timestamp',
            new_name='bet_time',
        ),
        migrations.AlterUniqueTogether(
            name='odds',
            unique_together=set([('site', 'bet_type', 'bet_time', 'game')]),
        ),
    ]
