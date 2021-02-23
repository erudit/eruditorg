# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2016-06-21 14:39
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("erudit", "0017_issue_thematic_issue"),
    ]

    operations = [
        migrations.AddField(
            model_name="article",
            name="publication_allowed_by_authors",
            field=models.BooleanField(
                default=True, verbose_name="Publication autorisée par l'auteur"
            ),
        ),
    ]
