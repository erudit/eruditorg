# -*- coding: utf-8 -*-
# Generated by Django 1.11.14 on 2018-07-17 20:41
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("book", "0002_auto_20180717_1529"),
    ]

    operations = [
        migrations.AddField(
            model_name="book",
            name="publisher_url",
            field=models.URLField(blank=True, null=True, verbose_name="Site web de l’éditeur"),
        ),
        migrations.AlterField(
            model_name="book",
            name="type",
            field=models.CharField(
                blank=True, choices=[("li", "Livre"), ("co", "Actes")], max_length=2, null=True
            ),
        ),
    ]
