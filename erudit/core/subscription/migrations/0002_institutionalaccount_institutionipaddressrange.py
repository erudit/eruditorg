# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('erudit', '0003_auto_20160219_1716'),
        ('subscription', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='InstitutionalAccount',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True, serialize=False)),
                ('institution', models.ForeignKey(verbose_name='Organisation', to='erudit.Organisation')),
                ('policy', models.ForeignKey(to='subscription.Policy', verbose_name='Accès', related_name='institutional_accounts')),
            ],
            options={
                'verbose_name': 'Compte institutionnel',
                'verbose_name_plural': 'Comptes institutionnel',
            },
        ),
        migrations.CreateModel(
            name='InstitutionIPAddressRange',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True, serialize=False)),
                ('ip_start', models.GenericIPAddressField(verbose_name='Adresse IP de début')),
                ('ip_end', models.GenericIPAddressField(verbose_name='Adresse IP de fin')),
                ('institutional_account', models.ForeignKey(verbose_name='Compte institutionnel', to='subscription.InstitutionalAccount')),
            ],
            options={
                'verbose_name': "Plage d'adresses IP d'institution",
                'verbose_name_plural': "Plages d'adresses IP d'institution",
            },
        ),
    ]
