# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('erudit', '0009_auto_20151130_2043'),
    ]

    operations = [
        migrations.AddField(
            model_name='journal',
            name='edinum_id',
            field=models.CharField(blank=True, max_length=7, null=True, verbose_name='Identifiant Edinum'),
        ),
        migrations.AddField(
            model_name='journal',
            name='sync_date',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='journal',
            name='synced_with_edinum',
            field=models.BooleanField(default=False, verbose_name='Synchronisé avec Edinum'),
        ),
        migrations.AddField(
            model_name='publisher',
            name='edinum_id',
            field=models.CharField(blank=True, max_length=7, null=True, verbose_name='Identifiant Edinum'),
        ),
        migrations.AddField(
            model_name='publisher',
            name='sync_date',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='publisher',
            name='synced_with_edinum',
            field=models.BooleanField(default=False, verbose_name='Synchronisé avec Edinum'),
        ),
    ]
