# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ("erudit", "0012_auto_20160510_1002"),
    ]

    operations = [
        migrations.AlterField(
            model_name="issue",
            name="date_published",
            field=models.DateField(
                verbose_name="Date de publication", default=datetime.date(2016, 5, 17)
            ),
            preserve_default=False,
        ),
    ]
