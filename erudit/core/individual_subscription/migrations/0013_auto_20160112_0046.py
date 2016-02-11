# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings
import django.utils.timezone
import core.individual_subscription.models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('erudit', '0014_auto_20160106_1527'),
        ('subscription', '0025_auto_20160107_2126'),
        ('individual_subscription', '0012_auto_20160104_2210'),
    ]

    operations = [
        migrations.CreateModel(
            name='Policy',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', serialize=False, auto_created=True)),
                ('date_creation', models.DateTimeField(verbose_name='Date de création', null=True, default=django.utils.timezone.now, editable=False)),
                ('date_modification', models.DateTimeField(verbose_name='Date de modification', null=True, default=django.utils.timezone.now, editable=False)),
                ('date_activation', models.DateTimeField(null=True, verbose_name="Date d'activation", blank=True, help_text="Ce champs se remplit automatiquement. Il est éditable uniquement pour les données existantes qui n'ont pas cette information")),
                ('date_renew', models.DateTimeField(null=True, verbose_name='Date de renouvellement')),
                ('renew_cycle', models.PositiveSmallIntegerField(default=365, verbose_name='Cycle du renouvellement (en jours)')),
                ('comment', models.TextField(verbose_name='Commentaire', blank=True)),
                ('max_accounts', models.PositiveSmallIntegerField(null=True, verbose_name='Maximum de comptes', blank=True)),
                ('access_full', models.BooleanField(default=False, verbose_name='Accès à tous les produits')),
                ('access_basket', models.ManyToManyField(to='subscription.Basket', verbose_name='Paniers', blank=True)),
                ('access_journal', models.ManyToManyField(to='erudit.Journal', verbose_name='Revues', blank=True)),
                ('managers', models.ManyToManyField(to=settings.AUTH_USER_MODEL, verbose_name='Gestionnaires des comptes', blank=True, related_name='organizations_managed')),
                ('organization', models.ForeignKey(verbose_name='Organisation', to='erudit.Organisation')),
            ],
            options={
                'verbose_name_plural': 'Accès aux produits',
                'verbose_name': 'Accès aux produits',
            },
            bases=(core.individual_subscription.models.FlatAccessMixin, models.Model),
        ),
        migrations.RemoveField(
            model_name='organizationpolicy',
            name='access_basket',
        ),
        migrations.RemoveField(
            model_name='organizationpolicy',
            name='access_journal',
        ),
        migrations.RemoveField(
            model_name='organizationpolicy',
            name='managers',
        ),
        migrations.RemoveField(
            model_name='organizationpolicy',
            name='organization',
        ),
        migrations.RemoveField(
            model_name='individualaccount',
            name='organization_policy',
        ),
        migrations.DeleteModel(
            name='OrganizationPolicy',
        ),
        migrations.AddField(
            model_name='individualaccount',
            name='policy',
            field=models.ForeignKey(default=1, to='individual_subscription.Policy', verbose_name='Accès', related_name='accounts'),
            preserve_default=False,
        ),
    ]
