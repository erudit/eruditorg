# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('subscription', '0019_auto_20151020_1522'),
    ]

    operations = [
        migrations.AlterField(
            model_name='client',
            name='organisation',
            field=models.CharField(default='', max_length=200),
        ),
        migrations.AlterField(
            model_name='renewalnotice',
            name='has_refused',
            field=models.BooleanField(verbose_name='Renouvellement refusé', default=False),
        ),
        migrations.AlterField(
            model_name='renewalnotice',
            name='has_renewed',
            field=models.BooleanField(verbose_name='Renouvellement confirmé', default=False),
        ),
    ]
