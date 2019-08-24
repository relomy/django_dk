# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [("nba", "0004_auto_20151130_0149")]

    operations = [
        migrations.CreateModel(
            name="DKContest",
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
                ("dk_id", models.CharField(unique=True, max_length=15)),
                ("date", models.DateField(null=True, blank=True)),
                ("name", models.CharField(max_length=100, null=True, blank=True)),
                (
                    "total_prizes",
                    models.DecimalField(
                        null=True, max_digits=18, decimal_places=2, blank=True
                    ),
                ),
                ("entries", models.PositiveIntegerField(null=True, blank=True)),
                ("positions_paid", models.PositiveIntegerField(null=True, blank=True)),
            ],
        ),
        migrations.CreateModel(
            name="DKResult",
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
                ("dk_id", models.CharField(unique=True, max_length=15)),
                ("name", models.CharField(max_length=50)),
                ("rank", models.PositiveIntegerField()),
                ("points", models.FloatField()),
                (
                    "c",
                    models.ForeignKey(
                        related_name="dk_c_results",
                        to="nba.Player",
                        on_delete=models.PROTECT,
                    ),
                ),
                (
                    "contest",
                    models.ForeignKey(
                        related_name="results",
                        to="nba.DKContest",
                        on_delete=models.PROTECT,
                    ),
                ),
                (
                    "f",
                    models.ForeignKey(
                        related_name="dk_f_results",
                        to="nba.Player",
                        on_delete=models.PROTECT,
                    ),
                ),
                (
                    "g",
                    models.ForeignKey(
                        related_name="dk_g_results",
                        to="nba.Player",
                        on_delete=models.PROTECT,
                    ),
                ),
                (
                    "pf",
                    models.ForeignKey(
                        related_name="dk_pf_results",
                        to="nba.Player",
                        on_delete=models.PROTECT,
                    ),
                ),
                (
                    "pg",
                    models.ForeignKey(
                        related_name="dk_pg_results",
                        to="nba.Player",
                        on_delete=models.PROTECT,
                    ),
                ),
                (
                    "sf",
                    models.ForeignKey(
                        related_name="dk_sf_results",
                        to="nba.Player",
                        on_delete=models.PROTECT,
                    ),
                ),
                (
                    "sg",
                    models.ForeignKey(
                        related_name="dk_sg_results",
                        to="nba.Player",
                        on_delete=models.PROTECT,
                    ),
                ),
                (
                    "util",
                    models.ForeignKey(
                        related_name="dk_util_results",
                        to="nba.Player",
                        on_delete=models.PROTECT,
                    ),
                ),
            ],
        ),
    ]
