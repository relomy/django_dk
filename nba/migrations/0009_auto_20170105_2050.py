# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [("nba", "0008_dkcontest_datetime")]

    operations = [
        migrations.AlterField(
            model_name="dkcontest",
            name="entry_fee",
            field=models.FloatField(null=True, blank=True),
        )
    ]
