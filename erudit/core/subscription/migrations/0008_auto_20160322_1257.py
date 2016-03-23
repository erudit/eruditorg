# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('subscription', '0007_remove_institutionalaccount_badge'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='individualaccountprofile',
            name='policy',
        ),
        migrations.RemoveField(
            model_name='individualaccountprofile',
            name='user',
        ),
        migrations.DeleteModel(
            name='IndividualAccountProfile',
        ),
    ]
