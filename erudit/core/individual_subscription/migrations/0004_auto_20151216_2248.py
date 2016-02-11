# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('individual_subscription', '0003_auto_20151216_2145'),
    ]

    operations = [
        migrations.AddField(
            model_name='organizationpolicy',
            name='date_activation',
            field=models.DateTimeField(blank=True, verbose_name="Date d'activation", null=True),
        ),
        migrations.AddField(
            model_name='organizationpolicy',
            name='date_creation',
            field=models.DateTimeField(default=datetime.datetime(2015, 12, 16, 22, 47, 54, 291959), auto_now_add=True, verbose_name='Date de création'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='organizationpolicy',
            name='date_modification',
            field=models.DateTimeField(default=datetime.datetime(2015, 12, 16, 22, 48, 3, 979577), auto_now=True, verbose_name='Date de modification'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='individualaccount',
            name='organization_policy',
            field=models.ForeignKey(related_name='accounts', to='individual_subscription.OrganizationPolicy', verbose_name="Accès de l'organisation"),
        ),
    ]
