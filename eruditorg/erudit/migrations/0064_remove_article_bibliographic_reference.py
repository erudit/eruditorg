# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2017-01-25 21:12
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("erudit", "0063_auto_20170116_1003"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="article",
            name="bibliographic_reference",
        ),
    ]
