# -*- coding: utf-8 -*-
# Generated by Django 1.9.9 on 2016-08-12 17:36
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("erudit", "0037_auto_20160812_1209"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="journal",
            name="formerly",
        ),
    ]
