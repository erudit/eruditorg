# -*- coding: utf-8 -*-
# Generated by Django 1.10.8 on 2018-05-01 15:56
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("erudit", "0093_auto_20180501_0947"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="issuetheme",
            name="issue",
        ),
        migrations.DeleteModel(
            name="IssueTheme",
        ),
    ]
