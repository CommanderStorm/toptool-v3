# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-02-12 15:09
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("meetingtypes", "0009_meetingtype_ical_key"),
    ]

    operations = [
        migrations.AddField(
            model_name="meetingtype",
            name="write_protokoll_button",
            field=models.BooleanField(
                default=True,
                verbose_name="Nicht-Admins können sich selbst zum Protokollanten machen",
            ),
            preserve_default=False,
        ),
    ]
