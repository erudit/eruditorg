# -*- coding: utf-8 -*-
# Generated by Django 1.10.8 on 2018-05-01 13:54
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("erudit", "0090_auto_20180501_0719"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="author",
            name="affiliations",
        ),
        migrations.RemoveField(
            model_name="author",
            name="organisation",
        ),
        migrations.RemoveField(
            model_name="article",
            name="authors",
        ),
        migrations.DeleteModel(
            name="Affiliation",
        ),
        migrations.DeleteModel(
            name="Author",
        ),
    ]
