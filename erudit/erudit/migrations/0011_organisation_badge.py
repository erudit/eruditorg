# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('erudit', '0010_auto_20160316_1400'),
    ]

    operations = [
        migrations.AddField(
            model_name='organisation',
            name='badge',
            field=models.ImageField(upload_to='organisation_badges', null=True, blank=True, verbose_name='Badge'),
        ),
    ]
