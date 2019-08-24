# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [("nba", "0007_auto_20151208_0509")]

    operations = [
        migrations.AddField(
            model_name="dkcontest",
            name="datetime",
            field=models.DateTimeField(null=True, blank=True),
        )
    ]
