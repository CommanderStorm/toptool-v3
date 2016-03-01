# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2016-03-01 17:43
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('meetings', '0003_auto_20160301_1840'),
    ]

    operations = [
        migrations.AlterField(
            model_name='meeting',
            name='protokollant',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='protokollant', to='persons.Person'),
        ),
        migrations.AlterField(
            model_name='meeting',
            name='sitzungsleitung',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='sitzungsleitung', to='persons.Person'),
        ),
    ]
