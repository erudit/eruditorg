# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('erudit', '0024_journal_collection'),
    ]

    operations = [
        migrations.CreateModel(
            name='JournalInformation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('about', models.TextField(null=True, blank=True, verbose_name='Revue')),
                ('about_fr', models.TextField(null=True, blank=True, verbose_name='Revue')),
                ('about_en', models.TextField(null=True, blank=True, verbose_name='Revue')),
                ('editorial_policy', models.TextField(null=True, blank=True, verbose_name='Politique éditoriale')),
                ('editorial_policy_fr', models.TextField(null=True, blank=True, verbose_name='Politique éditoriale')),
                ('editorial_policy_en', models.TextField(null=True, blank=True, verbose_name='Politique éditoriale')),
                ('subscriptions', models.TextField(null=True, blank=True, verbose_name='Abonnements')),
                ('subscriptions_fr', models.TextField(null=True, blank=True, verbose_name='Abonnements')),
                ('subscriptions_en', models.TextField(null=True, blank=True, verbose_name='Abonnements')),
                ('team', models.TextField(null=True, blank=True, verbose_name='Équipe')),
                ('team_fr', models.TextField(null=True, blank=True, verbose_name='Équipe')),
                ('team_en', models.TextField(null=True, blank=True, verbose_name='Équipe')),
                ('contact', models.TextField(null=True, blank=True, verbose_name='Contact')),
                ('contact_fr', models.TextField(null=True, blank=True, verbose_name='Contact')),
                ('contact_en', models.TextField(null=True, blank=True, verbose_name='Contact')),
                ('partners', models.TextField(null=True, blank=True, verbose_name='Partenaires')),
                ('partners_fr', models.TextField(null=True, blank=True, verbose_name='Partenaires')),
                ('partners_en', models.TextField(null=True, blank=True, verbose_name='Partenaires')),
                ('journal', models.OneToOneField(to='erudit.Journal', related_name='information', verbose_name='Journal')),
            ],
            options={
                'verbose_name_plural': 'Informations de revue',
                'verbose_name': 'Information de revue',
            },
        ),
    ]
