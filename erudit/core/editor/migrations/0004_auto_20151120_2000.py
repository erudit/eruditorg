# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('editor', '0003_auto_20151117_2125'),
    ]

    operations = [
        migrations.AddField(
            model_name='issuesubmission',
            name='number',
            field=models.CharField(default='', max_length=100, verbose_name='Numéro'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='issuesubmission',
            name='year',
            field=models.CharField(default='2000', max_length=4, verbose_name='Année'),
            preserve_default=False,
        ),
    ]
