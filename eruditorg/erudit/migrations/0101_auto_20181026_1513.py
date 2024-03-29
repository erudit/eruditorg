# -*- coding: utf-8 -*-
# Generated by Django 1.11.16 on 2018-10-26 20:13
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("erudit", "0100_auto_20181025_1532"),
    ]

    operations = [
        migrations.CreateModel(
            name="Language",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
                    ),
                ),
                ("code", models.CharField(max_length=2, unique=True, verbose_name="Code")),
                ("name", models.CharField(max_length=20, unique=True, verbose_name="Nom")),
                (
                    "name_fr",
                    models.CharField(max_length=20, null=True, unique=True, verbose_name="Nom"),
                ),
                (
                    "name_en",
                    models.CharField(max_length=20, null=True, unique=True, verbose_name="Nom"),
                ),
            ],
        ),
        migrations.AddField(
            model_name="journalinformation",
            name="languages",
            field=models.ManyToManyField(blank=True, to="erudit.Language", verbose_name="Langues"),
        ),
    ]
