# -*- coding: utf-8 -*-
# Generated by Django 1.9.9 on 2016-08-11 19:42
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("erudit", "0034_auto_20160810_1256"),
    ]

    operations = [
        migrations.RenameField(
            model_name="journal",
            old_name="url",
            new_name="external_url",
        ),
        migrations.AddField(
            model_name="article",
            name="external_url",
            field=models.URLField(blank=True, null=True, verbose_name="URL"),
        ),
        migrations.AddField(
            model_name="article",
            name="oai_datestamp",
            field=models.DateTimeField(blank=True, null=True, verbose_name="Datestamp OAI"),
        ),
        migrations.AddField(
            model_name="issue",
            name="external_url",
            field=models.URLField(blank=True, null=True, verbose_name="URL"),
        ),
        migrations.AddField(
            model_name="issue",
            name="oai_datestamp",
            field=models.DateTimeField(blank=True, null=True, verbose_name="Datestamp OAI"),
        ),
        migrations.AddField(
            model_name="journal",
            name="oai_datestamp",
            field=models.DateTimeField(blank=True, null=True, verbose_name="Datestamp OAI"),
        ),
    ]
