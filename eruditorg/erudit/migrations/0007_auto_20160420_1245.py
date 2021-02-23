# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("erudit", "0006_auto_20160420_1231"),
    ]

    operations = [
        migrations.AlterField(
            model_name="author",
            name="lastname",
            field=models.CharField(verbose_name="Nom", null=True, blank=True, max_length=50),
        ),
    ]
