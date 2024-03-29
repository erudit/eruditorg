# -*- coding: utf-8 -*-
# Generated by Django 1.9.9 on 2016-12-12 15:38
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("erudit", "0058_remove_article_subtitle"),
    ]

    operations = [
        migrations.AlterField(
            model_name="journal",
            name="publishers",
            field=models.ManyToManyField(
                blank=True, related_name="journals", to="erudit.Publisher", verbose_name="Éditeurs"
            ),
        ),
    ]
