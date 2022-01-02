# Generated by Django 1.11 on 2018-02-10 10:22
from __future__ import unicode_literals

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("meetingtypes", "0005_meetingtype_attachment_protokoll"),
    ]

    operations = [
        migrations.AlterField(
            model_name="meetingtype",
            name="id",
            field=models.CharField(
                max_length=20,
                primary_key=True,
                serialize=False,
                validators=[
                    django.core.validators.RegexValidator(
                        "^[a-z]+$",
                        "Nur Buchstaben von a-z erlaubt!",
                    ),
                    django.core.validators.RegexValidator(
                        "^(admin|login|logout|overview|all|add|protokolle|static|profile)$",
                        "Name ist reserviert!",
                        inverse_match=True,
                    ),
                ],
                verbose_name="Kurzname",
            ),
        ),
    ]
