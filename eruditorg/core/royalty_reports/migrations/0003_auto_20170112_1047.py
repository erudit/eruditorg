# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2017-01-12 15:47
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('royalty_reports', '0002_auto_20160727_0928'),
    ]

    operations = [
        migrations.AlterField(
            model_name='royaltyreport',
            name='published',
            field=models.BooleanField(default=False, verbose_name='Publié dans le tableau de bord'),
        ),
    ]
