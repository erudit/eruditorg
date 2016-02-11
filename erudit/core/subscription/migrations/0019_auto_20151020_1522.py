# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('subscription', '0018_auto_20151015_1506'),
    ]

    operations = [
        migrations.AddField(
            model_name='renewalnotice',
            name='has_refused',
            field=models.BooleanField(default=False, verbose_name='Renouvellement refusé'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='renewalnotice',
            name='has_renewed',
            field=models.BooleanField(default=False, verbose_name='Renouvellement confirmé'),
            preserve_default=False,
        ),
    ]
