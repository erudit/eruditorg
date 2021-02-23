# -*- coding: utf-8 -*-
# Generated by Django 1.9.9 on 2016-08-15 19:00
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("erudit", "0038_remove_journal_formerly"),
    ]

    operations = [
        migrations.AddField(
            model_name="journal",
            name="website_url",
            field=models.URLField(blank=True, null=True, verbose_name="Site web"),
        ),
    ]
