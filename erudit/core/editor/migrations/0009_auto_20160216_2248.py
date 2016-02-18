# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django_fsm


class Migration(migrations.Migration):

    dependencies = [
        ('editor', '0008_merge'),
    ]

    operations = [
        migrations.AlterField(
            model_name='issuesubmission',
            name='status',
            field=django_fsm.FSMField(max_length=50, default='D'),
        ),
    ]
