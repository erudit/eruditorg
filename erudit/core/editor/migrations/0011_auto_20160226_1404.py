# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django_fsm
import datetime
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('editor', '0010_auto_20160225_0032'),
    ]

    operations = [
        migrations.AddField(
            model_name='issuesubmission',
            name='date_modified',
            field=models.DateTimeField(auto_now=True, default=datetime.datetime(2016, 2, 26, 19, 4, 42, 410268, tzinfo=utc), verbose_name='Date de modification'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='issuesubmission',
            name='date_created',
            field=models.DateTimeField(auto_now_add=True, verbose_name="Date de l'envoi"),
        ),
        migrations.AlterField(
            model_name='issuesubmission',
            name='status',
            field=django_fsm.FSMField(default='D', max_length=50),
        ),
    ]
