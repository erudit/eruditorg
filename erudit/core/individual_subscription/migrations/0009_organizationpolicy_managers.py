# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('individual_subscription', '0008_auto_20151229_0819'),
    ]

    operations = [
        migrations.AddField(
            model_name='organizationpolicy',
            name='managers',
            field=models.ManyToManyField(to=settings.AUTH_USER_MODEL, blank=True, verbose_name='Gestionnaires des comptes'),
        ),
    ]
