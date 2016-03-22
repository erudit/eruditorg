# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('subscription', '0008_auto_20160322_1257'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='policyevent',
            name='policy',
        ),
        migrations.DeleteModel(
            name='PolicyEvent',
        ),
    ]
