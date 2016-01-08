# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('subscription', '0023_renewalnotice_is_paid'),
    ]

    operations = [
        migrations.AlterField(
            model_name='country',
            name='locale',
            field=models.CharField(verbose_name='Locale', blank=True, max_length=5),
        ),
    ]
