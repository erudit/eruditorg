# -*- coding: utf-8 -*-
# Generated by Django 1.10.8 on 2018-02-08 18:31
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('erudit', '0081_auto_20180201_1605'),
    ]

    operations = [
        migrations.AlterField(
            model_name='organisation',
            name='name',
            field=models.CharField(max_length=300, verbose_name='Nom'),
        ),
    ]
