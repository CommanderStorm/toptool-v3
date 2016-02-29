# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2016-02-29 20:44
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('meetingtypes', '0001_initial'),
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
                ('title', models.CharField(max_length=200)),
                ('topdeadline', models.DateTimeField()),
                ('attendees', models.ManyToManyField(related_name='attendees', to='persons.Person')),
                ('meetingtype', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='meetingtypes.MeetingType')),
                ('protokollant', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='protokollant', to='persons.Person')),
                ('sitzungsleitung', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='sitzungsleitung', to='persons.Person')),
            ],
        ),
    ]
