# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('individual_subscription', '0009_organizationpolicy_managers'),
    ]

    operations = [
        migrations.AddField(
            model_name='organizationpolicy',
            name='date_renew',
            field=models.DateTimeField(null=True, verbose_name='Date de renouvellement'),
        ),
        migrations.AlterField(
            model_name='organizationpolicy',
            name='managers',
            field=models.ManyToManyField(verbose_name='Gestionnaires des comptes', related_name='organizations_managed', to=settings.AUTH_USER_MODEL, blank=True),
        ),
    ]
