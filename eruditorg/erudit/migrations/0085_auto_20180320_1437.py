# -*- coding: utf-8 -*-
# Generated by Django 1.10.8 on 2018-03-20 19:37
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("erudit", "0084_merge_20180309_1448"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="article",
            name="formatted_title",
        ),
        migrations.RemoveField(
            model_name="article",
            name="surtitle",
        ),
    ]
