# Generated by Django 2.0.1 on 2018-08-05 10:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hsapp', '0042_auto_20180804_1926'),
    ]

    operations = [
        migrations.AddField(
            model_name='tournament',
            name='official_link',
            field=models.CharField(blank=True, max_length=500, null=True),
        ),
    ]
