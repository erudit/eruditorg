# -*- coding: utf-8 -*-
# Generated by Django 1.11.16 on 2018-10-29 13:59
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("erudit", "0101_auto_20181026_1513"),
    ]

    operations = [
        migrations.AddField(
            model_name="journalinformation",
            name="frequency",
            field=models.IntegerField(
                blank=True, null=True, verbose_name="Fréquence de publication"
            ),
        ),
    ]
