# Generated by Django 1.9 on 2016-08-22 19:05
from __future__ import unicode_literals

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("meetings", "0002_auto_20160306_1709"),
        ("meetingtypes", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="Attendee",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=200, verbose_name="Name")),
                ("version", models.DateTimeField(verbose_name="Version")),
            ],
        ),
        migrations.CreateModel(
            name="Function",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=200, verbose_name="Amt")),
                (
                    "plural",
                    models.CharField(
                        blank=True,
                        max_length=200,
                        verbose_name="Amt im Plural",
                    ),
                ),
                (
                    "meetingtype",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="meetingtypes.MeetingType",
                        verbose_name="Sitzungsgruppe",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Person",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=200, verbose_name="Name")),
                (
                    "version",
                    models.DateTimeField(
                        auto_now_add=True,
                        verbose_name="Zuletzt geaendert",
                    ),
                ),
                (
                    "last_selected",
                    models.DateTimeField(
                        auto_now_add=True,
                        verbose_name="Zuletzt anwesend",
                    ),
                ),
                (
                    "functions",
                    models.ManyToManyField(
                        blank=True,
                        to="persons.Function",
                        verbose_name="Aemter",
                    ),
                ),
                (
                    "meetingtype",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="meetingtypes.MeetingType",
                        verbose_name="Sitzungsgruppe",
                    ),
                ),
            ],
        ),
        migrations.AddField(
            model_name="attendee",
            name="functions",
            field=models.ManyToManyField(
                blank=True,
                to="persons.Function",
                verbose_name="Aemter",
            ),
        ),
        migrations.AddField(
            model_name="attendee",
            name="meeting",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                to="meetings.Meeting",
                verbose_name="Sitzung",
            ),
        ),
        migrations.AddField(
            model_name="attendee",
            name="person",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to="persons.Person",
                verbose_name="Person",
            ),
        ),
    ]
