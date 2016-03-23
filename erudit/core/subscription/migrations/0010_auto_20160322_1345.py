# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('subscription', '0009_auto_20160322_1339'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='policy',
            name='access_journal',
        ),
        migrations.RemoveField(
            model_name='policy',
            name='content_type',
        ),
        migrations.RemoveField(
            model_name='policy',
            name='managers',
        ),
        migrations.DeleteModel(
            name='Journal',
        ),
        migrations.DeleteModel(
            name='Organisation',
        ),
        migrations.RemoveField(
            model_name='institutionalaccount',
            name='policy',
        ),
        migrations.DeleteModel(
            name='Policy',
        ),
    ]
