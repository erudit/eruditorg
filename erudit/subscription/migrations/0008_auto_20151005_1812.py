# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('subscription', '0007_auto_20151005_1558'),
    ]

    operations = [
        migrations.AddField(
            model_name='client',
            name='erudit_number',
            field=models.CharField(default='', max_length=120),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='client',
            name='firstname',
            field=models.CharField(blank=True, max_length=100, null=True, verbose_name='Prénom'),
        ),
    ]
