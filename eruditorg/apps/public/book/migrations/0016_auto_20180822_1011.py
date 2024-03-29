# -*- coding: utf-8 -*-
# Generated by Django 1.11.14 on 2018-08-22 15:11
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("book", "0015_auto_20180808_0836"),
    ]

    operations = [
        migrations.AddField(
            model_name="book",
            name="slug",
            field=models.SlugField(default="", max_length=200),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="bookcollection",
            name="slug",
            field=models.SlugField(default="", max_length=200),
            preserve_default=False,
        ),
    ]
