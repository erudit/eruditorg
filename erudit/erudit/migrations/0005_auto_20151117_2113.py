# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('erudit', '0004_auto_20151117_1915'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='journal',
            name='date_created',
        ),
        migrations.RemoveField(
            model_name='journal',
            name='date_modified',
        ),
        migrations.RemoveField(
            model_name='journal',
            name='user_created',
        ),
        migrations.RemoveField(
            model_name='journal',
            name='user_modified',
        ),
    ]
