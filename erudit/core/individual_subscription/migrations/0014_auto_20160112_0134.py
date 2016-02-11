# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        ('individual_subscription', '0013_auto_20160112_0046'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='policy',
            name='organization',
        ),
        migrations.AddField(
            model_name='policy',
            name='content_type',
            field=models.ForeignKey(to='contenttypes.ContentType', default=1),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='policy',
            name='object_id',
            field=models.PositiveIntegerField(default=1),
            preserve_default=False,
        ),
    ]
