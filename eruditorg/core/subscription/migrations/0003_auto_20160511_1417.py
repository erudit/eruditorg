# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('subscription', '0002_journalaccesssubscription_sponsor'),
    ]

    operations = [
        migrations.CreateModel(
            name='JournalAccessSubscriptionPeriod',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, verbose_name='ID', auto_created=True)),
                ('start', models.DateField(verbose_name='Date de début')),
                ('end', models.DateField(verbose_name='Date de fin')),
            ],
            options={
                'verbose_name_plural': "Périodes d'abonnement aux revues",
                'verbose_name': "Période d'abonnement aux revues",
            },
        ),
        migrations.CreateModel(
            name='JournalManagementSubscriptionPeriod',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, verbose_name='ID', auto_created=True)),
                ('start', models.DateField(verbose_name='Date de début')),
                ('end', models.DateField(verbose_name='Date de fin')),
            ],
            options={
                'verbose_name_plural': "Périodes d'abonnement de gestion de revue",
                'verbose_name': "Période d'abonnement de gestion de revue",
            },
        ),
        migrations.RemoveField(
            model_name='journalaccesssubscription',
            name='date_activation',
        ),
        migrations.RemoveField(
            model_name='journalaccesssubscription',
            name='date_renew',
        ),
        migrations.RemoveField(
            model_name='journalaccesssubscription',
            name='renew_cycle',
        ),
        migrations.RemoveField(
            model_name='journalmanagementsubscription',
            name='date_activation',
        ),
        migrations.RemoveField(
            model_name='journalmanagementsubscription',
            name='date_renew',
        ),
        migrations.RemoveField(
            model_name='journalmanagementsubscription',
            name='renew_cycle',
        ),
        migrations.AddField(
            model_name='journalmanagementsubscriptionperiod',
            name='subscription',
            field=models.ForeignKey(on_delete=models.deletion.CASCADE, to='subscription.JournalManagementSubscription', verbose_name='Abonnement'),
        ),
        migrations.AddField(
            model_name='journalaccesssubscriptionperiod',
            name='subscription',
            field=models.ForeignKey(on_delete=models.deletion.CASCADE, to='subscription.JournalAccessSubscription', verbose_name='Abonnement'),
        ),
    ]
