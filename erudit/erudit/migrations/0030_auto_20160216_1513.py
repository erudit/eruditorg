# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('erudit', '0029_merge'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='article',
            name='edinum_id',
        ),
        migrations.RemoveField(
            model_name='article',
            name='sync_date',
        ),
        migrations.RemoveField(
            model_name='article',
            name='synced_with_edinum',
        ),
    ]
