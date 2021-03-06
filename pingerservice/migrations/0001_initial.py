# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2018-03-06 12:00
from __future__ import unicode_literals

import datetime
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Computer',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ip', models.GenericIPAddressField(unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='ComputerDay',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField()),
                ('duration', models.DurationField(default=datetime.timedelta(0), editable=False)),
                ('computer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='pingerservice.Computer', unique_for_date='date')),
            ],
        ),
        migrations.CreateModel(
            name='Interval',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('start_time', models.DateTimeField()),
                ('end_time', models.DateTimeField(blank=True, null=True)),
                ('day', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='pingerservice.ComputerDay')),
            ],
        ),
        migrations.CreateModel(
            name='Pool',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('room_no', models.CharField(max_length=20, unique=True)),
                ('keyboard_layout', models.CharField(choices=[('DE', 'German'), ('EN', 'English')], default='DE', max_length=2)),
                ('printer', models.BooleanField()),
                ('pc_power_consumption', models.IntegerField()),
            ],
        ),
        migrations.AddField(
            model_name='computer',
            name='pool',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='pingerservice.Pool'),
        ),
    ]
