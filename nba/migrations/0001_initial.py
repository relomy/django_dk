# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Game',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('nba_id', models.CharField(max_length=15, unique=True, null=True, blank=True)),
                ('date', models.DateField()),
                ('home_score', models.PositiveIntegerField(null=True, blank=True)),
                ('away_score', models.PositiveIntegerField(null=True, blank=True)),
                ('season_id', models.CharField(max_length=15, null=True, blank=True)),
                ('season', models.CharField(max_length=9, null=True, blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='GameStats',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('min', models.PositiveIntegerField(null=True, blank=True)),
                ('fgm', models.PositiveIntegerField(null=True, blank=True)),
                ('fga', models.PositiveIntegerField(null=True, blank=True)),
                ('fg3m', models.PositiveIntegerField(null=True, blank=True)),
                ('fg3a', models.PositiveIntegerField(null=True, blank=True)),
                ('ftm', models.PositiveIntegerField(null=True, blank=True)),
                ('fta', models.PositiveIntegerField(null=True, blank=True)),
                ('oreb', models.PositiveIntegerField(null=True, blank=True)),
                ('dreb', models.PositiveIntegerField(null=True, blank=True)),
                ('reb', models.PositiveIntegerField(null=True, blank=True)),
                ('ast', models.PositiveIntegerField(null=True, blank=True)),
                ('stl', models.PositiveIntegerField(null=True, blank=True)),
                ('blk', models.PositiveIntegerField(null=True, blank=True)),
                ('tov', models.PositiveIntegerField(null=True, blank=True)),
                ('pf', models.PositiveIntegerField(null=True, blank=True)),
                ('pts', models.PositiveIntegerField(null=True, blank=True)),
                ('plus_minus', models.PositiveIntegerField(null=True, blank=True)),
                ('game_id', models.ForeignKey(related_name='game_stats', to='nba.Game', on_delete=models.PROTECT)),
            ],
        ),
        migrations.CreateModel(
            name='Player',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('nba_id', models.CharField(max_length=15, unique=True, null=True, blank=True)),
                ('first_name', models.CharField(max_length=30, null=True, blank=True)),
                ('last_name', models.CharField(max_length=50, null=True, blank=True)),
                ('position', models.CharField(max_length=20, null=True, blank=True)),
                ('dk_position', models.CharField(max_length=2, null=True, blank=True)),
                ('height', models.PositiveIntegerField(null=True, blank=True)),
                ('weight', models.PositiveIntegerField(null=True, blank=True)),
                ('birthdate', models.DateField(null=True, blank=True)),
                ('school', models.CharField(max_length=80, null=True, blank=True)),
                ('country', models.CharField(max_length=80, null=True, blank=True)),
                ('start_year', models.PositiveIntegerField(null=True, blank=True)),
                ('end_year', models.PositiveIntegerField(null=True, blank=True)),
                ('seasons', models.PositiveIntegerField(null=True, blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='Team',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('nba_id', models.CharField(max_length=15, unique=True, null=True, blank=True)),
                ('name', models.CharField(unique=True, max_length=50)),
                ('abbr', models.CharField(unique=True, max_length=3)),
                ('city', models.CharField(max_length=50)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.AddField(
            model_name='player',
            name='team',
            field=models.ForeignKey(related_name='players', blank=True, to='nba.Team', null=True, on_delete=models.PROTECT),
        ),
        migrations.AddField(
            model_name='gamestats',
            name='player_id',
            field=models.ForeignKey(related_name='game_stats', to='nba.Player', on_delete=models.PROTECT),
        ),
        migrations.AddField(
            model_name='game',
            name='away_team',
            field=models.ForeignKey(related_name='away_games', to='nba.Team', on_delete=models.PROTECT),
        ),
        migrations.AddField(
            model_name='game',
            name='home_team',
            field=models.ForeignKey(related_name='home_games', to='nba.Team', on_delete=models.PROTECT),
        ),
        migrations.AddField(
            model_name='game',
            name='winner',
            field=models.ForeignKey(related_name='won_games', blank=True, to='nba.Team', null=True, on_delete=models.PROTECT),
        ),
    ]
