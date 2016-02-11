# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('plupload', '__first__'),
        ('editor', '0006_issuesubmission_status'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='issuesubmission',
            name='submission_file',
        ),
        migrations.AddField(
            model_name='issuesubmission',
            name='submissions',
            field=models.ManyToManyField(to='plupload.ResumableFile'),
        ),
    ]
