# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('erudit', '0004_auto_20160223_1319'),
    ]

    operations = [
        migrations.AddField(
            model_name='author',
            name='suffix',
            field=models.CharField(max_length=20, blank=True, null=True, verbose_name='Suffixe'),
        ),
    ]
