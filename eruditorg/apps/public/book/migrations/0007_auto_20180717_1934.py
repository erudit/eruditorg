# -*- coding: utf-8 -*-
# Generated by Django 1.11.14 on 2018-07-18 00:34
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("book", "0006_auto_20180717_1857"),
    ]

    operations = [
        migrations.AddField(
            model_name="book",
            name="year",
            field=models.PositiveIntegerField(
                blank=True, null=True, verbose_name="Année de publication"
            ),
        ),
        migrations.AlterField(
            model_name="book",
            name="type",
            field=models.CharField(
                choices=[("li", "Livre"), ("co", "Actes")], default="li", max_length=2
            ),
        ),
    ]
