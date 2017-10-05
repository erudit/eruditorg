# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2017-10-02 20:01
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('subscription', '0011_auto_20171002_0921'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='journalmanagementsubscription',
            options={'ordering': ['journal__name'], 'verbose_name': "Abonnement aux forfaits d'abonnements individuels", 'verbose_name_plural': "Abonnements aux forfaits d'abonnements individuels"},
        ),
        migrations.AlterModelOptions(
            name='journalmanagementsubscriptionperiod',
            options={'verbose_name': "Période d'abonnement de aux forfaits d'abonnements individuels", 'verbose_name_plural': "Périodes d'abonnement aux forfaits d'abonnements individuels"},
        ),
    ]
