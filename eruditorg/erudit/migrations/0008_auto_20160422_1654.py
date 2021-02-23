# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("erudit", "0007_auto_20160420_1245"),
    ]

    operations = [
        migrations.AlterField(
            model_name="eruditdocument",
            name="localidentifier",
            field=models.CharField(
                unique=True, db_index=True, max_length=50, verbose_name="Identifiant Fedora"
            ),
        ),
    ]
