# -*- coding: utf-8 -*-
# Generated by Django 1.11.13 on 2018-07-26 20:28
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('book', '0012_book_contributors'),
    ]

    operations = [
        migrations.AlterField(
            model_name='book',
            name='title',
            field=models.CharField(max_length=400, verbose_name='Titre'),
        ),
    ]
