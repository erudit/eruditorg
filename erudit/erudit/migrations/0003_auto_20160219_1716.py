# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('erudit', '0002_auto_20160219_1714'),
    ]

    operations = [
        migrations.AddField(
            model_name='grant',
            name='currency',
            field=models.ForeignKey(null=True, blank=True, to='erudit.Currency', verbose_name='Devise'),
        ),
        migrations.AddField(
            model_name='invoice',
            name='currency',
            field=models.ForeignKey(null=True, blank=True, to='erudit.Currency', verbose_name='Devise'),
        ),
        migrations.AddField(
            model_name='quotationitem',
            name='currency',
            field=models.ForeignKey(null=True, blank=True, to='erudit.Currency'),
        ),
    ]
