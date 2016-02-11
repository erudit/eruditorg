# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('individual_subscription', '0002_auto_20151216_2142'),
    ]

    operations = [
        migrations.AlterField(
            model_name='organizationpolicy',
            name='access_basket',
            field=models.ManyToManyField(verbose_name='Paniers', blank=True, to='subscription.Basket'),
        ),
        migrations.AlterField(
            model_name='organizationpolicy',
            name='access_journal',
            field=models.ManyToManyField(verbose_name='Revues', blank=True, to='erudit.Journal'),
        ),
    ]
