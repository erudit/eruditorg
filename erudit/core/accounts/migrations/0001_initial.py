# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='AbonnementProfile',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('password', models.CharField(max_length=50, verbose_name='Mot de passe', blank=True)),
                ('user', models.OneToOneField(to=settings.AUTH_USER_MODEL, verbose_name='Utilisateur')),
            ],
            options={
                'verbose_name_plural': 'Comptes personnels',
                'verbose_name': 'Compte personnel',
            },
        ),
        migrations.CreateModel(
            name='MandragoreProfile',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('synced_with_mandragore', models.BooleanField(verbose_name='Synchronisé avec Mandragore', default=False)),
                ('mandragore_id', models.CharField(max_length=7, verbose_name='Identifiant Mandragore', blank=True, null=True)),
                ('sync_date', models.DateField(blank=True, null=True)),
                ('user', models.OneToOneField(to=settings.AUTH_USER_MODEL, verbose_name='Utilisateur')),
            ],
        ),
    ]
