# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2016-03-05 01:46
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('protokolle', '0004_auto_20160304_2345'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='protokoll',
            name='html',
        ),
        migrations.RemoveField(
            model_name='protokoll',
            name='pdf',
        ),
        migrations.RemoveField(
            model_name='protokoll',
            name='tex',
        ),
        migrations.RemoveField(
            model_name='protokoll',
            name='txt',
        ),
    ]
