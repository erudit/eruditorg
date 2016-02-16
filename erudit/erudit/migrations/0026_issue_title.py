# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('erudit', '0025_journalinformation'),
    ]

    operations = [
        migrations.AddField(
            model_name='issue',
            name='title',
            field=models.CharField(null=True, blank=True, max_length=255),
        ),
    ]
