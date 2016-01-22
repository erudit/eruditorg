# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('individual_subscription', '0007_auto_20151220_2342'),
    ]

    operations = [
        migrations.AlterField(
            model_name='organizationpolicy',
            name='date_creation',
            field=models.DateTimeField(default=django.utils.timezone.now, verbose_name='Date de création', editable=False, null=True),
        ),
        migrations.AlterField(
            model_name='organizationpolicy',
            name='date_modification',
            field=models.DateTimeField(default=django.utils.timezone.now, verbose_name='Date de modification', editable=False, null=True),
        ),
        migrations.AlterField(
            model_name='organizationpolicy',
            name='max_accounts',
            field=models.PositiveSmallIntegerField(verbose_name='Maximum de comptes', null=True, blank=True),
        ),
    ]
