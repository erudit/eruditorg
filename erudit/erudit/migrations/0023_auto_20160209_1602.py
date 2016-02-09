# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('erudit', '0022_auto_20160209_1559'),
    ]

    operations = [
        migrations.AddField(
            model_name='collection',
            name='edinum_id',
            field=models.CharField(null=True, blank=True, max_length=7, verbose_name='Identifiant Edinum'),
        ),
        migrations.AddField(
            model_name='collection',
            name='sync_date',
            field=models.DateField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='collection',
            name='synced_with_edinum',
            field=models.BooleanField(default=False, verbose_name='Synchronisé avec Edinum'),
        ),
    ]
