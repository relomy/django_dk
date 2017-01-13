# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sportsbook', '0005_auto_20170111_2020'),
    ]

    operations = [
        migrations.AddField(
            model_name='odds',
            name='game_id',
            field=models.CharField(max_length=50, null=True, blank=True),
        ),
        migrations.AddField(
            model_name='odds',
            name='pos1',
            field=models.IntegerField(default=1),
        ),
        migrations.AddField(
            model_name='odds',
            name='pos2',
            field=models.IntegerField(default=2),
        ),
        migrations.AddField(
            model_name='odds',
            name='prop_id',
            field=models.CharField(max_length=50, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='odds',
            name='bet_time',
            field=models.DateTimeField(db_index=True),
        ),
    ]
