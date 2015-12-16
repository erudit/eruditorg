# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('erudit', '0013_auto_20151214_1350'),
    ]

    operations = [
        migrations.CreateModel(
            name='IndividualAccount',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True, serialize=False)),
                ('email', models.CharField(verbose_name='Courriel', max_length=120)),
                ('password', models.CharField(verbose_name='Mot de passe', max_length=50)),
                ('firstname', models.CharField(verbose_name='Prénom', max_length=30)),
                ('lastname', models.CharField(verbose_name='Nom', max_length=30)),
            ],
            options={
                'verbose_name': 'Compte personnel',
                'verbose_name_plural': 'Comptes personnels',
            },
        ),
        migrations.CreateModel(
            name='Organization',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True, serialize=False)),
                ('name', models.CharField(verbose_name='Nom', max_length=255)),
                ('max_accounts', models.PositiveSmallIntegerField(verbose_name='Maximum de comptes')),
                ('access_full', models.BooleanField(verbose_name='Accès à toutes les ressources', default=False)),
                ('access_journal', models.ManyToManyField(verbose_name='Revue', to='erudit.Journal')),
            ],
            options={
                'verbose_name': 'Organisation',
                'verbose_name_plural': 'Organisations',
            },
        ),
        migrations.AddField(
            model_name='individualaccount',
            name='organization',
            field=models.ForeignKey(verbose_name='Organisation', to='individual_subscription.Organization'),
        ),
    ]
