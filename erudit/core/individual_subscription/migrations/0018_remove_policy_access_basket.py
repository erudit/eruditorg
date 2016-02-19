# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('individual_subscription', '0017_auto_20160128_2205'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='policy',
            name='access_basket',
        ),
    ]
