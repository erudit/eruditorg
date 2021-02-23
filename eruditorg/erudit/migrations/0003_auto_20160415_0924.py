# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("erudit", "0002_auto_20160414_1321"),
    ]

    operations = [
        migrations.AlterField(
            model_name="article",
            name="issue",
            field=models.ForeignKey(
                on_delete=models.deletion.CASCADE,
                to="erudit.Issue",
                related_name="articles",
                verbose_name="Numéro",
            ),
        ),
    ]
