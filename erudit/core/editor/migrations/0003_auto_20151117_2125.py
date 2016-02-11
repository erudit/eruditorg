# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('editor', '0002_auto_20151117_1915'),
    ]

    operations = [
        migrations.AlterField(
            model_name='issuesubmission',
            name='submission_file',
            field=models.FileField(null=True, blank=True, verbose_name='Fichier', upload_to='uploads'),
        ),
    ]
