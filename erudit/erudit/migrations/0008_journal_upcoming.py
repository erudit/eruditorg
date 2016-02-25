# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('erudit', '0007_auto_20160223_1546'),
    ]

    operations = [
        migrations.AddField(
            model_name='journal',
            name='upcoming',
            field=models.BooleanField(default=False, verbose_name='Prochainement disponible'),
        ),
    ]
