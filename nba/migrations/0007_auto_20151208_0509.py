# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('nba', '0006_auto_20151207_0014'),
    ]

    operations = [
        migrations.CreateModel(
            name='DKSalary',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('date', models.DateField(null=True, blank=True)),
                ('salary', models.PositiveIntegerField()),
                ('player', models.ForeignKey(related_name='dk_salaries', to='nba.Player')),
            ],
        ),
        migrations.AlterUniqueTogether(
            name='dksalary',
            unique_together=set([('player', 'date')]),
        ),
    ]
