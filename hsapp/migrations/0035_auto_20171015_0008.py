# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2017-10-14 21:08
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('hsapp', '0034_auto_20171014_1430'),
    ]

    operations = [
        migrations.AddField(
            model_name='deckset',
            name='player',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='hsapp.Player'),
        ),
        migrations.AlterField(
            model_name='match',
            name='date',
            field=models.DateField(default=django.utils.timezone.now),
        ),
    ]
