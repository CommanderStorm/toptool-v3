# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2016-03-01 11:48
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('persons', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Meeting',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('time', models.DateTimeField()),
                ('room', models.CharField(max_length=200)),
                ('semester', models.CharField(max_length=200)),
                ('title', models.CharField(blank=True, max_length=200)),
                ('topdeadline', models.DateTimeField()),
                ('attendees', models.ManyToManyField(blank=True, related_name='attendees', to='persons.Person')),
            ],
        ),
    ]
