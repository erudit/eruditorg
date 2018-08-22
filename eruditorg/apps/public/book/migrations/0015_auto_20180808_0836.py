# -*- coding: utf-8 -*-
# Generated by Django 1.11.14 on 2018-08-08 13:36
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('book', '0014_auto_20180727_1325'),
    ]

    operations = [
        migrations.AddField(
            model_name='book',
            name='path',
            field=models.CharField(blank=True, max_length=200, null=True, verbose_name='répertoire'),
        ),
        migrations.AddField(
            model_name='bookcollection',
            name='path',
            field=models.CharField(blank=True, max_length=200, null=True, verbose_name='répertoire'),
        ),
        migrations.AlterField(
            model_name='book',
            name='type',
            field=models.CharField(choices=[('li', 'Livre'), ('ac', 'Actes')], default='li', max_length=2),
        ),
    ]