# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import datetime
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('plupload', '0004_auto_20151218_1612'),
        ('editor', '0013_auto_20160227_2328'),
    ]

    operations = [
        migrations.CreateModel(
            name='IssueSubmissionFilesVersion',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, verbose_name='ID', primary_key=True)),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='Date de création')),
                ('updated', models.DateTimeField(auto_now=True, verbose_name='Date de modification')),
            ],
            options={
                'verbose_name_plural': "Versions de fichiers d'envois de numéro",
                'verbose_name': "Version de fichiers d'un envoi de numéro",
                'ordering': ['created'],
            },
        ),
        migrations.RemoveField(
            model_name='issuesubmission',
            name='parent',
        ),
        migrations.RemoveField(
            model_name='issuesubmission',
            name='submissions',
        ),
        migrations.AlterField(
            model_name='issuesubmission',
            name='date_created',
            field=models.DateTimeField(auto_now_add=True, default=datetime.datetime(2016, 3, 17, 14, 45, 39, 696222, tzinfo=utc), verbose_name="Date de l'envoi"),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='issuesubmission',
            name='date_modified',
            field=models.DateTimeField(auto_now=True, default=datetime.datetime(2016, 3, 17, 14, 45, 45, 200079, tzinfo=utc), verbose_name='Date de modification'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='issuesubmissionfilesversion',
            name='issue_submission',
            field=models.ForeignKey(verbose_name='Envoi de numéro', to='editor.IssueSubmission', related_name='files_versions'),
        ),
        migrations.AddField(
            model_name='issuesubmissionfilesversion',
            name='submissions',
            field=models.ManyToManyField(to='plupload.ResumableFile'),
        ),
    ]
