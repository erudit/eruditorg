# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    replaces = [('editor', '0001_initial'), ('editor', '0002_auto_20151112_1938'), ('editor', '0003_auto_20151112_1942'), ('editor', '0004_auto_20151112_2037')]

    dependencies = [
        ('erudit', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='JournalSubmission',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, verbose_name='ID', serialize=False)),
                ('volume', models.CharField(verbose_name='Volume', max_length=100)),
                ('date_created', models.DateField(verbose_name="Date de l'envoi")),
                ('comment', models.TextField(verbose_name='Commentaire', null=True, blank=True)),
                ('submission_file', models.FileField(verbose_name='Fichier', upload_to='uploads')),
                ('contact', models.ForeignKey(to=settings.AUTH_USER_MODEL, verbose_name='Personne contact')),
                ('journal', models.ForeignKey(to='erudit.Journal', verbose_name='Revue')),
            ],
            options={
                'verbose_name': 'Envoi de numéro',
                'verbose_name_plural': 'Envois de numéros',
            },
        ),
    ]
