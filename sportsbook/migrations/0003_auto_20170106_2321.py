# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sportsbook', '0002_auto_20170105_2122'),
    ]

    operations = [
        migrations.AddField(
            model_name='odds',
            name='game',
            field=models.CharField(default='NULL', max_length=100),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='odds',
            name='odds1',
            field=models.FloatField(),
        ),
        migrations.AlterField(
            model_name='odds',
            name='odds2',
            field=models.FloatField(),
        ),
        migrations.AlterUniqueTogether(
            name='odds',
            unique_together=set([('site', 'type', 'timestamp', 'game')]),
        ),
    ]
