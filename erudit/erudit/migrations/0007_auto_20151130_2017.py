# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('erudit', '0006_auto_20151130_1659'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='publisher',
            options={'verbose_name': 'Éditeur', 'ordering': ['name'], 'verbose_name_plural': 'Éditeurs'},
        ),
        migrations.AddField(
            model_name='journal',
            name='series_id',
            field=models.CharField(null=True, verbose_name='Identifiant Edinum', blank=True, max_length=7),
        ),
    ]
