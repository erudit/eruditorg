# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('erudit', '0023_auto_20160209_1602'),
    ]

    operations = [
        migrations.AddField(
            model_name='journal',
            name='collection',
            field=models.ForeignKey(to='erudit.Collection', blank=True, null=True),
        ),
    ]
