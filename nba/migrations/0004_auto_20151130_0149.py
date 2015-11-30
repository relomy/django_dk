# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('nba', '0003_auto_20151129_2058'),
    ]

    operations = [
        migrations.CreateModel(
            name='Injury',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('status', models.CharField(max_length=50)),
                ('date', models.DateField()),
                ('comment', models.CharField(max_length=500, null=True, blank=True)),
                ('player', models.ForeignKey(related_name='injuries', to='nba.Player')),
            ],
        ),
        migrations.AlterUniqueTogether(
            name='game',
            unique_together=set([('home_team', 'away_team', 'date')]),
        ),
        migrations.AlterUniqueTogether(
            name='gamestats',
            unique_together=set([('game', 'player')]),
        ),
        migrations.AlterUniqueTogether(
            name='injury',
            unique_together=set([('player', 'date', 'comment')]),
        ),
    ]
