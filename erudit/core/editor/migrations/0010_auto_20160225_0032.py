# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
import django_fsm


class Migration(migrations.Migration):

    dependencies = [
        ('editor', '0009_auto_20160216_2248'),
    ]

    operations = [
        migrations.AddField(
            model_name='issuesubmission',
            name='parent',
            field=models.OneToOneField(on_delete=django.db.models.deletion.SET_NULL, null=True, to='editor.IssueSubmission', blank=True),
        ),
        migrations.AlterField(
            model_name='issuesubmission',
            name='status',
            field=django_fsm.FSMField(protected=True, max_length=50, default='D'),
        ),
    ]
