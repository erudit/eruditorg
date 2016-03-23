# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('erudit', '0012_auto_20160322_1257'),
        ('subscription', '0010_auto_20160322_1345'),
    ]

    operations = [
        migrations.CreateModel(
            name='JournalAccessSubscription',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('title', models.CharField(max_length=120, null=True, verbose_name='Titre', blank=True)),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='Date de création')),
                ('updated', models.DateTimeField(auto_now=True, verbose_name='Date de modification')),
                ('date_activation', models.DateField(null=True, verbose_name="Date d'activation", blank=True)),
                ('date_renew', models.DateField(null=True, verbose_name='Date de renouvellement', blank=True)),
                ('renew_cycle', models.PositiveSmallIntegerField(null=True, verbose_name='Cycle du renouvellement (en jours)', blank=True)),
                ('comment', models.TextField(null=True, verbose_name='Commentaire', blank=True)),
                ('full_access', models.BooleanField(default=False, verbose_name='Accès complet')),
                ('collection', models.ForeignKey(null=True, to='erudit.Collection', related_name='+', blank=True, verbose_name='Collection')),
                ('journal', models.ForeignKey(null=True, to='erudit.Journal', related_name='+', blank=True, verbose_name='Revue')),
                ('journals', models.ManyToManyField(related_name='_journalaccesssubscription_journals_+', to='erudit.Journal', verbose_name='Revues')),
                ('organisation', models.ForeignKey(null=True, to='erudit.Organisation', blank=True, verbose_name='Organisation')),
                ('user', models.ForeignKey(null=True, to=settings.AUTH_USER_MODEL, blank=True, verbose_name='Utilisateur')),
            ],
            options={
                'verbose_name_plural': 'Abonnements aux revues',
                'verbose_name': 'Abonnement aux revues',
            },
        ),
        migrations.CreateModel(
            name='JournalManagementPlan',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('title', models.CharField(max_length=255, null=True, verbose_name='Titre', blank=True)),
                ('code', models.SlugField(max_length=100, unique=True, verbose_name='Code')),
                ('max_accounts', models.PositiveSmallIntegerField(verbose_name='Maximum de comptes')),
            ],
            options={
                'verbose_name_plural': 'Forfaits de gestion de revues',
                'verbose_name': "Forfait de gestion d'une revue",
            },
        ),
        migrations.CreateModel(
            name='JournalManagementSubscription',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('title', models.CharField(max_length=120, null=True, verbose_name='Titre', blank=True)),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='Date de création')),
                ('updated', models.DateTimeField(auto_now=True, verbose_name='Date de modification')),
                ('date_activation', models.DateField(null=True, verbose_name="Date d'activation", blank=True)),
                ('date_renew', models.DateField(null=True, verbose_name='Date de renouvellement', blank=True)),
                ('renew_cycle', models.PositiveSmallIntegerField(null=True, verbose_name='Cycle du renouvellement (en jours)', blank=True)),
                ('comment', models.TextField(null=True, verbose_name='Commentaire', blank=True)),
                ('journal', models.ForeignKey(to='erudit.Journal', verbose_name='Revue')),
                ('plan', models.ForeignKey(to='subscription.JournalManagementPlan', verbose_name='Forfait')),
            ],
            options={
                'verbose_name_plural': 'Abonnements de gestion de revue',
                'verbose_name': 'Abonnement de gestion de revue',
            },
        ),
        migrations.RemoveField(
            model_name='institutionalaccount',
            name='institution',
        ),
        migrations.RemoveField(
            model_name='institutionipaddressrange',
            name='institutional_account',
        ),
        migrations.DeleteModel(
            name='InstitutionalAccount',
        ),
        migrations.AddField(
            model_name='institutionipaddressrange',
            name='subscription',
            field=models.ForeignKey(default=1, to='subscription.JournalAccessSubscription', verbose_name='Abonnement aux revues'),
            preserve_default=False,
        ),
    ]
