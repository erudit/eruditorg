# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("erudit", "0008_auto_20160422_1654"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="journal",
            name="display_name",
        ),
        migrations.AddField(
            model_name="journal",
            name="name_en",
            field=models.CharField(
                help_text="Nom officiel", max_length=255, verbose_name="Nom", null=True
            ),
        ),
        migrations.AddField(
            model_name="journal",
            name="name_fr",
            field=models.CharField(
                help_text="Nom officiel", max_length=255, verbose_name="Nom", null=True
            ),
        ),
    ]
