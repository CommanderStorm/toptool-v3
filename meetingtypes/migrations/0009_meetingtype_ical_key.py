# Generated by Django 1.11 on 2018-02-12 11:57
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("meetingtypes", "0008_auto_20180212_1007"),
    ]

    operations = [
        migrations.AddField(
            model_name="meetingtype",
            name="ical_key",
            field=models.UUIDField(blank=True, null=True, verbose_name="iCal-Key"),
        ),
    ]
