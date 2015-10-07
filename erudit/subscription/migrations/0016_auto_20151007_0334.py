# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('subscription', '0015_auto_20151007_0223'),
    ]

    operations = [
        migrations.AlterField(
            model_name='client',
            name='currency',
            field=models.CharField(max_length=3, blank=True, verbose_name='Devise', null=True),
        ),
        migrations.AlterField(
            model_name='client',
            name='exemption_code',
            field=models.CharField(max_length=1, blank=True, verbose_name="Code d'exemption", null=True),
        ),
        migrations.AlterField(
            model_name='client',
            name='pobox',
            field=models.CharField(max_length=100, blank=True, verbose_name='Casier postal', null=True),
        ),
        migrations.AlterField(
            model_name='client',
            name='province',
            field=models.CharField(max_length=100, blank=True, verbose_name='Province', null=True),
        ),
    ]
