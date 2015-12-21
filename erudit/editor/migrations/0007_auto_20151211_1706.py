# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('plupload', '__first__'),
        ('editor', '0006_issuesubmission_status'),
    ]

    operations = [
        migrations.AlterField(
            model_name='issuesubmission',
            name='volume',
            field=models.CharField(blank=True, null=True, max_length=100, verbose_name='Volume'),
        ),
        migrations.AlterField(
            model_name='issuesubmission',
            name='year',
            field=models.CharField(max_length=9, verbose_name='Année'),
        ),
    ]
