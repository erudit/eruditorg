# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('erudit', '0002_auto_20151105_2129'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='journalsubmission',
            name='contact',
        ),
        migrations.RemoveField(
            model_name='journalsubmission',
            name='journal',
        ),
        migrations.DeleteModel(
            name='JournalSubmission',
        ),
    ]
