# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2017-10-09 13:20
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hsapp', '0027_tournament_prize'),
    ]

    operations = [
        migrations.AddField(
            model_name='match',
            name='vod_link',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
    ]
