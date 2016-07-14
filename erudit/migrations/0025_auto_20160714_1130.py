# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2016-07-14 16:30
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('erudit', '0024_auto_20160629_0944'),
    ]

    operations = [
        migrations.AddField(
            model_name='journal',
            name='next_code',
            field=models.SlugField(blank=True, max_length=255, null=True, verbose_name='Code revue suivante'),
        ),
        migrations.AddField(
            model_name='journal',
            name='previous_code',
            field=models.SlugField(blank=True, max_length=255, null=True, verbose_name='Code revue précédente'),
        ),
    ]
