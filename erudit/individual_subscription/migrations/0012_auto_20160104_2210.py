# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('individual_subscription', '0011_organizationpolicy_renew_cycle'),
    ]

    operations = [
        migrations.AlterField(
            model_name='organizationpolicy',
            name='date_activation',
            field=models.DateTimeField(blank=True, verbose_name="Date d'activation", null=True),
        ),
    ]
