# -*- coding: utf-8 -*-
# Generated by Django 1.11.13 on 2018-07-27 18:25
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('book', '0013_auto_20180726_1528'),
    ]

    operations = [
        migrations.AlterField(
            model_name='book',
            name='collection',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='books', to='book.BookCollection'),
        ),
        migrations.AlterField(
            model_name='book',
            name='cover',
            field=models.ImageField(blank=True, null=True, upload_to='book_cover', verbose_name='Couverture'),
        ),
    ]
