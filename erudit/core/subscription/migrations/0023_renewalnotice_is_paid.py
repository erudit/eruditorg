# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('subscription', '0022_auto_20160106_1446'),
    ]

    operations = [
        migrations.AddField(
            model_name='renewalnotice',
            name='is_paid',
            field=models.BooleanField(verbose_name='Payé', help_text='Avis de renouvellement payé', default=False),
        ),
    ]
