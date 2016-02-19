# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('erudit', '0030_auto_20160216_1513'),
        ('contenttypes', '0002_remove_content_type_name'),
    ]

    operations = [
        migrations.CreateModel(
            name='IndividualAccount',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, verbose_name='ID', serialize=False)),
                ('email', models.CharField(max_length=120, verbose_name='Courriel')),
                ('password', models.CharField(max_length=50, verbose_name='Mot de passe', blank=True)),
                ('firstname', models.CharField(max_length=30, verbose_name='Prénom')),
                ('lastname', models.CharField(max_length=30, verbose_name='Nom')),
                ('active', models.BooleanField(verbose_name='Actif', default=True)),
            ],
            options={
                'verbose_name_plural': 'Comptes personnels',
                'verbose_name': 'Compte personnel',
            },
        ),
        migrations.CreateModel(
            name='Policy',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, verbose_name='ID', serialize=False)),
                ('generated_title', models.CharField(blank=True, max_length=120, verbose_name='Titre', editable=False)),
                ('date_creation', models.DateTimeField(null=True, verbose_name='Date de création', editable=False, default=django.utils.timezone.now)),
                ('date_modification', models.DateTimeField(null=True, verbose_name='Date de modification', editable=False, default=django.utils.timezone.now)),
                ('date_activation', models.DateTimeField(help_text="Ce champs se remplit automatiquement.             Il est éditable uniquement pour les données existantes qui n'ont pas cette information", verbose_name="Date d'activation", blank=True, null=True)),
                ('date_renew', models.DateTimeField(null=True, verbose_name='Date de renouvellement')),
                ('renew_cycle', models.PositiveSmallIntegerField(verbose_name='Cycle du renouvellement (en jours)', default=365)),
                ('object_id', models.PositiveIntegerField()),
                ('comment', models.TextField(verbose_name='Commentaire', blank=True)),
                ('max_accounts', models.PositiveSmallIntegerField(null=True, verbose_name='Maximum de comptes', blank=True)),
                ('access_full', models.BooleanField(verbose_name='Accès à tous les produits', default=False)),
            ],
            options={
                'verbose_name_plural': 'Accès aux produits',
                'verbose_name': 'Accès aux produits',
            },
        ),
        migrations.CreateModel(
            name='PolicyEvent',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, verbose_name='ID', serialize=False)),
                ('date_creation', models.DateTimeField(null=True, verbose_name='Date de création', editable=False, default=django.utils.timezone.now)),
                ('code', models.CharField(max_length=120, verbose_name='Code', choices=[('LIMIT_REACHED', 'Limite atteinte')])),
                ('message', models.TextField(verbose_name='Texte', blank=True)),
                ('policy', models.ForeignKey(verbose_name='Accès aux produits', to='individual_subscription.Policy')),
            ],
            options={
                'verbose_name_plural': 'Évènements sur les accès',
                'verbose_name': 'Évènement sur les accès',
                'ordering': ('-date_creation',),
            },
        ),
        migrations.CreateModel(
            name='Journal',
            fields=[
            ],
            options={
                'verbose_name': 'Revue',
                'proxy': True,
            },
            bases=('erudit.journal',),
        ),
        migrations.CreateModel(
            name='Organisation',
            fields=[
            ],
            options={
                'proxy': True,
            },
            bases=('erudit.organisation',),
        ),
        migrations.AddField(
            model_name='policy',
            name='access_journal',
            field=models.ManyToManyField(verbose_name='Revues', blank=True, to='erudit.Journal'),
        ),
        migrations.AddField(
            model_name='policy',
            name='content_type',
            field=models.ForeignKey(verbose_name='Type', to='contenttypes.ContentType'),
        ),
        migrations.AddField(
            model_name='policy',
            name='managers',
            field=models.ManyToManyField(to=settings.AUTH_USER_MODEL, verbose_name='Gestionnaires des comptes', blank=True, related_name='organizations_managed'),
        ),
        migrations.AddField(
            model_name='individualaccount',
            name='policy',
            field=models.ForeignKey(to='individual_subscription.Policy', verbose_name='Accès', related_name='accounts'),
        ),
    ]
