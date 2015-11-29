# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('nba', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='gamestats',
            old_name='game_id',
            new_name='game',
        ),
        migrations.RenameField(
            model_name='gamestats',
            old_name='player_id',
            new_name='player',
        ),
    ]
