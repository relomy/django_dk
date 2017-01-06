# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sportsbook', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='odds',
            name='timestamp',
            field=models.DateTimeField(auto_now=True, db_index=True),
        ),
    ]
