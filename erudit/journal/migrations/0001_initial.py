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
                ('id', models.AutoField(primary_key=True, serialize=False, verbose_name='ID', auto_created=True)),
                ('about', models.TextField(verbose_name='Revue')),
                ('about_en', models.TextField(null=True, verbose_name='Revue')),
                ('about_fr_ca', models.TextField(null=True, verbose_name='Revue')),
                ('editorial_policy', models.TextField(null=True, verbose_name='Politique éditoriale', blank=True)),
                ('editorial_policy_en', models.TextField(null=True, verbose_name='Politique éditoriale', blank=True)),
                ('editorial_policy_fr_ca', models.TextField(null=True, verbose_name='Politique éditoriale', blank=True)),
                ('subscriptions', models.TextField(null=True, verbose_name='Abonnements', blank=True)),
                ('subscriptions_en', models.TextField(null=True, verbose_name='Abonnements', blank=True)),
                ('subscriptions_fr_ca', models.TextField(null=True, verbose_name='Abonnements', blank=True)),
                ('team', models.TextField(null=True, verbose_name='Équipe', blank=True)),
                ('team_en', models.TextField(null=True, verbose_name='Équipe', blank=True)),
                ('team_fr_ca', models.TextField(null=True, verbose_name='Équipe', blank=True)),
                ('contact', models.TextField(null=True, verbose_name='Contact', blank=True)),
                ('contact_en', models.TextField(null=True, verbose_name='Contact', blank=True)),
                ('contact_fr_ca', models.TextField(null=True, verbose_name='Contact', blank=True)),
                ('partners', models.TextField(null=True, verbose_name='Partenaires', blank=True)),
                ('partners_en', models.TextField(null=True, verbose_name='Partenaires', blank=True)),
                ('partners_fr_ca', models.TextField(null=True, verbose_name='Partenaires', blank=True)),
                ('journal', models.OneToOneField(to='erudit.Journal', verbose_name='Journal')),
            ],
            options={
                'verbose_name': 'Information de revue',
                'verbose_name_plural': 'Informations de revue',
            },
        ),
    ]
