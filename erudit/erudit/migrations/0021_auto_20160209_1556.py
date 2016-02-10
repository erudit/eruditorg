# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('erudit', '0020_collection'),
    ]

    operations = [
        migrations.AlterField(
            model_name='collection',
            name='prefix',
            field=models.CharField(null=True, blank=True, max_length=5),
        ),
    ]
