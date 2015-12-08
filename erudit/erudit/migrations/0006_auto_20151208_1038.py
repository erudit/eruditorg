# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('erudit', '0005_auto_20151117_2113'),
    ]

    operations = [
        migrations.AlterField(
            model_name='publisher',
            name='members',
            field=models.ManyToManyField(to=settings.AUTH_USER_MODEL, related_name='publishers'),
        ),
    ]
