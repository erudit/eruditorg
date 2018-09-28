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
                ('id', models.AutoField(primary_key=True, auto_created=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=50, blank=True, verbose_name='Mot de passe')),
                ('user', models.OneToOneField(on_delete=models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='Utilisateur')),
            ],
            options={
                'verbose_name_plural': 'Comptes personnels',
                'verbose_name': 'Compte personnel',
            },
        ),
        migrations.CreateModel(
            name='MandragoreProfile',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, serialize=False, verbose_name='ID')),
                ('synced_with_mandragore', models.BooleanField(default=False, verbose_name='Synchronisé avec Mandragore')),
                ('mandragore_id', models.CharField(max_length=7, blank=True, null=True, verbose_name='Identifiant Mandragore')),
                ('sync_date', models.DateField(blank=True, null=True)),
                ('user', models.OneToOneField(on_delete=models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='Utilisateur')),
            ],
        ),
    ]
