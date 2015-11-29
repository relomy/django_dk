# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('nba', '0002_auto_20151129_2052'),
    ]

    operations = [
        migrations.AlterField(
            model_name='gamestats',
            name='plus_minus',
            field=models.IntegerField(null=True, blank=True),
        ),
    ]
