# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('erudit', '0004_auto_20151117_1915'),
        ('editor', '0001_squashed_0004_auto_20151112_2037'),
    ]

    operations = [
        migrations.CreateModel(
            name='IssueSubmission',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', serialize=False, auto_created=True)),
                ('volume', models.CharField(max_length=100, verbose_name='Volume')),
                ('date_created', models.DateField(verbose_name="Date de l'envoi")),
                ('comment', models.TextField(null=True, verbose_name='Commentaire', blank=True)),
                ('submission_file', models.FileField(upload_to='uploads', verbose_name='Fichier')),
                ('contact', models.ForeignKey(verbose_name='Personne contact', to=settings.AUTH_USER_MODEL)),
                ('journal', models.ForeignKey(verbose_name='Revue', to='erudit.Journal')),
            ],
            options={
                'verbose_name': 'Envoi de numéro',
                'verbose_name_plural': 'Envois de numéros',
            },
        ),
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
