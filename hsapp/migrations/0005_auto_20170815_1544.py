# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2017-08-15 12:44
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hsapp', '0004_auto_20170815_1543'),
    ]

    operations = [
        migrations.AlterField(
            model_name='player',
            name='image',
            field=models.ImageField(null=True, upload_to='hsapp/players'),
        ),
    ]
