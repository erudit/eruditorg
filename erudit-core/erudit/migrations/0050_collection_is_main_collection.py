# -*- coding: utf-8 -*-
# Generated by Django 1.9.9 on 2016-10-20 17:38
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('erudit', '0049_auto_20161014_1623'),
    ]

    operations = [
        migrations.AddField(
            model_name='collection',
            name='is_main_collection',
            field=models.BooleanField(default=False, help_text='Les fonds primaires sont hébergés en partie ou en totalité par Érudit', verbose_name='Fonds primaire'),
        ),
    ]
