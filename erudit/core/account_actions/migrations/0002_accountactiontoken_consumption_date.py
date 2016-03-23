# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account_actions', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='accountactiontoken',
            name='consumption_date',
            field=models.DateTimeField(verbose_name='Date de consommation', blank=True, null=True),
        ),
    ]
