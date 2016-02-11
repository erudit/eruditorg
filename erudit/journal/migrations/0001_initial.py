# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('erudit', '0019_merge'),
    ]

    operations = [
        migrations.CreateModel(
            name='JournalInformation',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', primary_key=True, auto_created=True)),
                ('about', models.TextField(verbose_name='Revue', null=True, blank=True)),
                ('about_fr', models.TextField(verbose_name='Revue', null=True, blank=True)),
                ('about_en', models.TextField(verbose_name='Revue', null=True, blank=True)),
                ('editorial_policy', models.TextField(verbose_name='Politique éditoriale', null=True, blank=True)),
                ('editorial_policy_fr', models.TextField(verbose_name='Politique éditoriale', null=True, blank=True)),
                ('editorial_policy_en', models.TextField(verbose_name='Politique éditoriale', null=True, blank=True)),
                ('subscriptions', models.TextField(verbose_name='Abonnements', null=True, blank=True)),
                ('subscriptions_fr', models.TextField(verbose_name='Abonnements', null=True, blank=True)),
                ('subscriptions_en', models.TextField(verbose_name='Abonnements', null=True, blank=True)),
                ('team', models.TextField(verbose_name='Équipe', null=True, blank=True)),
                ('team_fr', models.TextField(verbose_name='Équipe', null=True, blank=True)),
                ('team_en', models.TextField(verbose_name='Équipe', null=True, blank=True)),
                ('contact', models.TextField(verbose_name='Contact', null=True, blank=True)),
                ('contact_fr', models.TextField(verbose_name='Contact', null=True, blank=True)),
                ('contact_en', models.TextField(verbose_name='Contact', null=True, blank=True)),
                ('partners', models.TextField(verbose_name='Partenaires', null=True, blank=True)),
                ('partners_fr', models.TextField(verbose_name='Partenaires', null=True, blank=True)),
                ('partners_en', models.TextField(verbose_name='Partenaires', null=True, blank=True)),
                ('journal', models.OneToOneField(to='erudit.Journal', verbose_name='Journal', related_name='information')),
            ],
            options={
                'verbose_name': 'Information de revue',
                'verbose_name_plural': 'Informations de revue',
            },
        ),
    ]
