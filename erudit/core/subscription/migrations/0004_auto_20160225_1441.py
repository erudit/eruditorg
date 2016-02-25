# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('subscription', '0003_auto_20160225_1345'),
    ]

    operations = [
        migrations.AlterField(
            model_name='institutionalaccount',
            name='badge',
            field=models.ImageField(verbose_name='Badge', null=True, blank=True, upload_to='institutional_accounts_badges'),
        ),
    ]
