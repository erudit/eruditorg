# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('erudit', '0013_auto_20151214_1350'),
        ('individual_subscription', '0004_auto_20151216_2248'),
    ]

    operations = [
        migrations.CreateModel(
            name='IndividualAccountJournal',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, verbose_name='ID', auto_created=True)),
            ],
        ),
        migrations.AlterField(
            model_name='individualaccount',
            name='password',
            field=models.CharField(blank=True, verbose_name='Mot de passe', max_length=50),
        ),
        migrations.AddField(
            model_name='individualaccountjournal',
            name='account',
            field=models.ForeignKey(to='individual_subscription.IndividualAccount', verbose_name='Compte personnel'),
        ),
        migrations.AddField(
            model_name='individualaccountjournal',
            name='journal',
            field=models.ForeignKey(to='erudit.Journal', verbose_name='Revue'),
        ),
    ]
