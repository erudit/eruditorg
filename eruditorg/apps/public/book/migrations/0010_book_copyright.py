# -*- coding: utf-8 -*-
# Generated by Django 1.11.14 on 2018-07-18 01:29
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("book", "0009_auto_20180717_2009"),
    ]

    operations = [
        migrations.AddField(
            model_name="book",
            name="copyright",
            field=models.CharField(
                blank=True, max_length=200, null=True, verbose_name="Mention du droit d’auteur"
            ),
        ),
    ]
