# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('erudit', '0008_journal_subtitle'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='publisher',
            name='person_id',
        ),
        migrations.RemoveField(
            model_name='publisher',
            name='sync_date',
        ),
        migrations.RemoveField(
            model_name='publisher',
            name='synced_with_edinum',
        ),
    ]
