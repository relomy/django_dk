# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [("nba", "0005_dkcontest_dkresult")]

    operations = [
        migrations.CreateModel(
            name="DKContestPayout",
            fields=[
                (
                    "id",
                    models.AutoField(
                        verbose_name="ID",
                        serialize=False,
                        auto_created=True,
                        primary_key=True,
                    ),
                ),
                ("upper_rank", models.PositiveIntegerField()),
                ("lower_rank", models.PositiveIntegerField()),
                ("payout", models.DecimalField(max_digits=18, decimal_places=2)),
            ],
        ),
        migrations.AddField(
            model_name="dkcontest",
            name="entry_fee",
            field=models.DecimalField(
                null=True, max_digits=18, decimal_places=2, blank=True
            ),
        ),
        migrations.AddField(
            model_name="dkcontestpayout",
            name="contest",
            field=models.ForeignKey(
                related_name="payouts", to="nba.DKContest", on_delete=models.PROTECT
            ),
        ),
        migrations.AlterUniqueTogether(
            name="dkcontestpayout",
            unique_together=set([("contest", "upper_rank", "lower_rank")]),
        ),
    ]
