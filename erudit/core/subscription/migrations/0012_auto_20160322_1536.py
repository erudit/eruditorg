# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('subscription', '0011_auto_20160322_1417'),
    ]

    operations = [
        migrations.AlterField(
            model_name='journalaccesssubscription',
            name='journals',
            field=models.ManyToManyField(verbose_name='Revues', related_name='_journalaccesssubscription_journals_+', to='erudit.Journal', blank=True),
        ),
    ]
