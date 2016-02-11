# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('individual_subscription', '0010_auto_20160104_2156'),
    ]

    operations = [
        migrations.AddField(
            model_name='organizationpolicy',
            name='renew_cycle',
            field=models.PositiveSmallIntegerField(default=365, verbose_name='Cycle du renouvellement (en jours)'),
        ),
    ]
