# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('nba', '0009_auto_20170105_2050'),
    ]

    operations = [
        migrations.CreateModel(
            name='Odds',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('site', models.CharField(max_length=20)),
                ('type', models.CharField(max_length=20)),
                ('timestamp', models.DateTimeField(auto_now=True)),
                ('odds1', models.IntegerField()),
                ('odds2', models.IntegerField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('team1', models.ForeignKey(related_name='odds1', to='nba.Team')),
                ('team2', models.ForeignKey(related_name='odds2', to='nba.Team')),
            ],
        ),
        migrations.AlterUniqueTogether(
            name='odds',
            unique_together=set([('site', 'type', 'timestamp', 'team1', 'team2')]),
        ),
    ]
