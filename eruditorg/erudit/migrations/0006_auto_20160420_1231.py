# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("erudit", "0005_auto_20160420_1023"),
    ]

    operations = [
        migrations.AlterField(
            model_name="author",
            name="suffix",
            field=models.CharField(blank=True, null=True, max_length=50, verbose_name="Suffixe"),
        ),
    ]
