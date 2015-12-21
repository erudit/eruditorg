# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('individual_subscription', '0006_auto_20151220_2253'),
    ]

    operations = [
        migrations.AlterField(
            model_name='organizationpolicy',
            name='date_activation',
            field=models.DateTimeField(verbose_name="Date d'activation", blank=True, null=True, editable=False),
        ),
        migrations.AlterField(
            model_name='organizationpolicy',
            name='date_creation',
            field=models.DateTimeField(verbose_name='Date de création', default=django.utils.timezone.now, editable=False),
        ),
        migrations.AlterField(
            model_name='organizationpolicy',
            name='date_modification',
            field=models.DateTimeField(verbose_name='Date de modification', default=django.utils.timezone.now, editable=False),
        ),
    ]
