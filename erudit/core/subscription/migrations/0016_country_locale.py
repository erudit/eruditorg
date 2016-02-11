# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('subscription', '0015_auto_20151007_0223'),
    ]

    operations = [
        migrations.AddField(
            model_name='country',
            name='locale',
            field=models.CharField(default='fr_CA', max_length=5, verbose_name='Locale'),
            preserve_default=False,
        ),
    ]
