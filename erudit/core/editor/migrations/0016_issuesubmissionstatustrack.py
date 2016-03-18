# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('editor', '0015_auto_20160317_1040'),
    ]

    operations = [
        migrations.CreateModel(
            name='IssueSubmissionStatusTrack',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', primary_key=True, auto_created=True)),
                ('created', models.DateTimeField(verbose_name='Date de création', auto_now_add=True)),
                ('status', models.CharField(verbose_name='statut', max_length=100)),
                ('files_version', models.ForeignKey(verbose_name='Version des fichiers', to='editor.IssueSubmissionFilesVersion', blank=True, null=True)),
                ('issue_submission', models.ForeignKey(verbose_name='Changements de statut', related_name='status_tracks', to='editor.IssueSubmission')),
            ],
            options={
                'verbose_name': "Changement de statut d'un envoi de numéro",
                'ordering': ['created'],
                'verbose_name_plural': "Changements de statut d'envois de numéro",
            },
        ),
    ]
