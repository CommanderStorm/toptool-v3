# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2016-03-06 16:09
from __future__ import unicode_literals

import uuid

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tops', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='standardtop',
            name='id',
            field=models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='top',
            name='id',
            field=models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False),
        ),
    ]
