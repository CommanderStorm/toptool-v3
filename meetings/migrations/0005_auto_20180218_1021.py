# Generated by Django 1.11 on 2018-02-18 09:21
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("meetings", "0004_meeting_pad"),
    ]

    operations = [
        migrations.AlterField(
            model_name="meeting",
            name="title",
            field=models.CharField(
                blank=True,
                help_text="Wenn kein Titel gesetzt ist, wird der Name der Sitzungsgruppe verwendet.",
                max_length=200,
                verbose_name="Alternativer Titel",
            ),
        ),
        migrations.AlterField(
            model_name="meeting",
            name="topdeadline",
            field=models.DateTimeField(
                blank=True,
                help_text="Frist, bis zu der TOPs eingereicht werden können. "
                "Wenn keine Frist gesetzt ist, können bis zum Beginn der Sitzung TOPs eingetragen werden.",
                null=True,
                verbose_name="TOP-Einreichungsfrist",
            ),
        ),
    ]
