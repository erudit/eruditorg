# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('erudit', '0007_auto_20151130_2017'),
    ]

    operations = [
        migrations.AddField(
            model_name='journal',
            name='subtitle',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
