# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2016-06-02 14:56
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("tops", "0002_auto_20160306_1709"),
    ]

    operations = [
        migrations.AlterField(
            model_name="top",
            name="email",
            field=models.EmailField(max_length=254, verbose_name="Deine E-Mailadresse"),
        ),
    ]
