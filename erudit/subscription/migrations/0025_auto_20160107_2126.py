# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('subscription', '0024_auto_20160107_2124'),
    ]

    operations = [
        migrations.AlterField(
            model_name='country',
            name='locale',
            field=models.CharField(blank=True, verbose_name='Locale', max_length=5, null=True),
        ),
    ]
