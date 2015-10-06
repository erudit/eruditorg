# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('subscription', '0008_auto_20151005_1922'),
    ]

    operations = [
        migrations.AddField(
            model_name='renewalnotice',
            name='has_basket',
            field=models.BooleanField(default=False, editable=False),
        ),
    ]
