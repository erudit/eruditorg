# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('individual_subscription', '0005_auto_20151220_2133'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='individualaccountjournal',
            unique_together=set([('journal', 'account')]),
        ),
    ]
