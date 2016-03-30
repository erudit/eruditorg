# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account_actions', '0002_accountactiontoken_consumption_date'),
    ]

    operations = [
        migrations.AddField(
            model_name='accountactiontoken',
            name='active',
            field=models.BooleanField(verbose_name='Actif', default=True),
        ),
    ]
