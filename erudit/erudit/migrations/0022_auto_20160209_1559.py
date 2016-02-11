# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('erudit', '0021_auto_20160209_1556'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='collection',
            name='prefix',
        ),
        migrations.AddField(
            model_name='collection',
            name='code',
            field=models.CharField(blank=True, max_length=10, null=True),
        ),
    ]
