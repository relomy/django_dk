# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sportsbook', '0004_auto_20170111_0737'),
    ]

    operations = [
        migrations.CreateModel(
            name='Arb',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('option', models.IntegerField(choices=[(1, b'Odds1 Team1 - Odds2 Team 2'), (2, b'Odds1 Team2 - Odds2 Team 1')])),
                ('percentage', models.FloatField()),
                ('margin', models.FloatField()),
                ('delta', models.DurationField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('odds1', models.ForeignKey(related_name='arb1', to='sportsbook.Odds')),
                ('odds2', models.ForeignKey(related_name='arb2', to='sportsbook.Odds')),
            ],
        ),
        migrations.AlterUniqueTogether(
            name='arb',
            unique_together=set([('option', 'odds1', 'odds2')]),
        ),
    ]
