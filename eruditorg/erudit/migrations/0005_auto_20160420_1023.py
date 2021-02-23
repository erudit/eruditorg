# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("erudit", "0004_auto_20160415_1315"),
    ]

    operations = [
        migrations.AlterField(
            model_name="article",
            name="surtitle",
            field=models.CharField(max_length=600, blank=True, null=True),
        ),
        migrations.AlterField(
            model_name="article",
            name="title",
            field=models.CharField(max_length=600, blank=True, null=True),
        ),
    ]
