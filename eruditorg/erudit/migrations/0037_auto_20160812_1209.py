# -*- coding: utf-8 -*-
# Generated by Django 1.9.9 on 2016-08-12 17:09
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("erudit", "0036_auto_20160812_0956"),
    ]

    operations = [
        migrations.AlterField(
            model_name="author",
            name="firstname",
            field=models.CharField(blank=True, max_length=150, null=True, verbose_name="Prénom"),
        ),
        migrations.AlterField(
            model_name="author",
            name="lastname",
            field=models.CharField(blank=True, max_length=150, null=True, verbose_name="Nom"),
        ),
    ]
