# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("erudit", "0009_auto_20160505_1630"),
    ]

    operations = [
        migrations.AddField(
            model_name="journal",
            name="subtitle_en",
            field=models.CharField(max_length=255, blank=True, null=True),
        ),
        migrations.AddField(
            model_name="journal",
            name="subtitle_fr",
            field=models.CharField(max_length=255, blank=True, null=True),
        ),
    ]
