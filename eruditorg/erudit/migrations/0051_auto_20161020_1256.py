# -*- coding: utf-8 -*-
# Generated by Django 1.9.9 on 2016-10-20 17:56
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('erudit', '0050_collection_is_main_collection'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='collection',
            options={'verbose_name': 'Fond', 'verbose_name_plural': 'Fonds'},
        ),
        migrations.AlterField(
            model_name='collection',
            name='code',
            field=models.CharField(max_length=10, unique=True, verbose_name='Code'),
        ),
        migrations.AlterField(
            model_name='collection',
            name='localidentifier',
            field=models.CharField(blank=True, help_text='Identifiant Fedora du fonds', max_length=10, null=True, verbose_name='Identifiant Fedora'),
        ),
        migrations.AlterField(
            model_name='collection',
            name='name',
            field=models.CharField(max_length=200, verbose_name='Nom'),
        ),
    ]