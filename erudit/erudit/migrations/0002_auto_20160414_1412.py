# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('erudit', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='collection',
            name='edinum_id',
        ),
        migrations.RemoveField(
            model_name='collection',
            name='sync_date',
        ),
        migrations.RemoveField(
            model_name='collection',
            name='synced_with_edinum',
        ),
        migrations.RemoveField(
            model_name='journal',
            name='edinum_id',
        ),
        migrations.RemoveField(
            model_name='journal',
            name='sync_date',
        ),
        migrations.RemoveField(
            model_name='journal',
            name='synced_with_edinum',
        ),
        migrations.RemoveField(
            model_name='publisher',
            name='edinum_id',
        ),
        migrations.RemoveField(
            model_name='publisher',
            name='sync_date',
        ),
        migrations.RemoveField(
            model_name='publisher',
            name='synced_with_edinum',
        ),
        migrations.AddField(
            model_name='collection',
            name='localidentifier',
            field=models.CharField(blank=True, max_length=10, null=True),
        ),
        migrations.AlterField(
            model_name='collection',
            name='code',
            field=models.CharField(max_length=10, default='code', unique=True),
            preserve_default=False,
        ),
    ]
