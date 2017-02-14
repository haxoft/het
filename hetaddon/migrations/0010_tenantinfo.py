# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-02-14 01:39
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hetaddon', '0009_auto_20170202_2322'),
    ]

    operations = [
        migrations.CreateModel(
            name='TenantInfo',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('key', models.CharField(max_length=128)),
                ('client_key', models.CharField(max_length=128)),
                ('shared_secret', models.CharField(max_length=128)),
            ],
        ),
    ]