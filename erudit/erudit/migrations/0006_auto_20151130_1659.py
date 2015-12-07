# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('erudit', '0005_auto_20151117_2113'),
    ]

    operations = [
        migrations.AddField(
            model_name='publisher',
            name='person_id',
            field=models.CharField(max_length=7, null=True, verbose_name='Identifiant Edinum', blank=True),
        ),
        migrations.AddField(
            model_name='publisher',
            name='sync_date',
            field=models.DateField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='publisher',
            name='synced_with_edinum',
            field=models.BooleanField(verbose_name='Synchronisé avec Edinum', default=False),
        ),
    ]
