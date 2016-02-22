# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.utils.timezone
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('erudit', '0003_auto_20160219_1716'),
    ]

    operations = [
        migrations.CreateModel(
            name='IndividualAccount',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('email', models.CharField(verbose_name='Courriel', max_length=120)),
                ('password', models.CharField(verbose_name='Mot de passe', blank=True, max_length=50)),
                ('firstname', models.CharField(verbose_name='Prénom', max_length=30)),
                ('lastname', models.CharField(verbose_name='Nom', max_length=30)),
                ('active', models.BooleanField(verbose_name='Actif', default=True)),
            ],
            options={
                'verbose_name': 'Compte personnel',
                'verbose_name_plural': 'Comptes personnels',
            },
        ),
        migrations.CreateModel(
            name='Policy',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('generated_title', models.CharField(editable=False, blank=True, max_length=120, verbose_name='Titre')),
                ('date_creation', models.DateTimeField(verbose_name='Date de création', null=True, default=django.utils.timezone.now, editable=False)),
                ('date_modification', models.DateTimeField(verbose_name='Date de modification', null=True, default=django.utils.timezone.now, editable=False)),
                ('date_activation', models.DateTimeField(null=True, blank=True, help_text="Ce champs se remplit automatiquement.             Il est éditable uniquement pour les données existantes qui n'ont pas cette information", verbose_name="Date d'activation")),
                ('date_renew', models.DateTimeField(null=True, verbose_name='Date de renouvellement')),
                ('renew_cycle', models.PositiveSmallIntegerField(verbose_name='Cycle du renouvellement (en jours)', default=365)),
                ('object_id', models.PositiveIntegerField()),
                ('comment', models.TextField(verbose_name='Commentaire', blank=True)),
                ('max_accounts', models.PositiveSmallIntegerField(null=True, blank=True, verbose_name='Maximum de comptes')),
                ('access_full', models.BooleanField(verbose_name='Accès à tous les produits', default=False)),
            ],
            options={
                'verbose_name': 'Accès aux produits',
                'verbose_name_plural': 'Accès aux produits',
            },
        ),
        migrations.CreateModel(
            name='PolicyEvent',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('date_creation', models.DateTimeField(verbose_name='Date de création', null=True, default=django.utils.timezone.now, editable=False)),
                ('code', models.CharField(verbose_name='Code', choices=[('LIMIT_REACHED', 'Limite atteinte')], max_length=120)),
                ('message', models.TextField(verbose_name='Texte', blank=True)),
                ('policy', models.ForeignKey(to='subscription.Policy', verbose_name='Accès aux produits')),
            ],
            options={
                'verbose_name': 'Évènement sur les accès',
                'ordering': ('-date_creation',),
                'verbose_name_plural': 'Évènements sur les accès',
            },
        ),
        migrations.CreateModel(
            name='Journal',
            fields=[
            ],
            options={
                'proxy': True,
                'verbose_name': 'Revue',
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
            field=models.ForeignKey(to='contenttypes.ContentType', verbose_name='Type'),
        ),
        migrations.AddField(
            model_name='policy',
            name='managers',
            field=models.ManyToManyField(verbose_name='Gestionnaires des comptes', blank=True, related_name='organizations_managed', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='individualaccount',
            name='policy',
            field=models.ForeignKey(verbose_name='Accès', related_name='accounts', to='subscription.Policy'),
        ),
    ]
