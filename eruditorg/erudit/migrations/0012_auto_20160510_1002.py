# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("erudit", "0011_auto_20160509_1517"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="journal",
            name="address",
        ),
        migrations.AlterField(
            model_name="journal",
            name="localidentifier",
            field=models.CharField(
                max_length=50, null=True, unique=True, blank=True, verbose_name="Identifiant Fedora"
            ),
        ),
    ]
