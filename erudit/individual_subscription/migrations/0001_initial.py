# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('subscription', '0021_auto_20151214_1350'),
        ('erudit', '0013_auto_20151214_1350'),
    ]

    operations = [
        migrations.CreateModel(
            name='IndividualAccount',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('email', models.CharField(max_length=120, verbose_name='Courriel')),
                ('password', models.CharField(max_length=50, verbose_name='Mot de passe')),
                ('firstname', models.CharField(max_length=30, verbose_name='Prénom')),
                ('lastname', models.CharField(max_length=30, verbose_name='Nom')),
            ],
            options={
                'verbose_name_plural': 'Comptes personnels',
                'verbose_name': 'Compte personnel',
            },
        ),
        migrations.CreateModel(
            name='OrganizationPolicy',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('comment', models.CharField(max_length=255, verbose_name='Commentaire')),
                ('max_accounts', models.PositiveSmallIntegerField(verbose_name='Maximum de comptes')),
                ('access_full', models.BooleanField(verbose_name='Accès à toutes les ressources', default=False)),
                ('access_basket', models.ManyToManyField(verbose_name='Panier', to='subscription.Basket')),
                ('access_journal', models.ManyToManyField(verbose_name='Revues', to='erudit.Journal')),
                ('organization', models.ForeignKey(verbose_name='Organisation', to='erudit.Organisation')),
            ],
            options={
                'verbose_name_plural': 'Accès des organisations',
                'verbose_name': "Accès de l'organisation",
            },
        ),
        migrations.AddField(
            model_name='individualaccount',
            name='organization_policy',
            field=models.ForeignKey(verbose_name="Accès de l'organisation", to='individual_subscription.OrganizationPolicy'),
        ),
    ]
