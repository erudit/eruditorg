# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('subscription', '0006_auto_20160308_1426'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='institutionalaccount',
            name='badge',
        ),
    ]
