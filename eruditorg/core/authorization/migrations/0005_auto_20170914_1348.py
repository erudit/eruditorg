# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2017-09-14 18:48
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('authorization', '0004_auto_20170628_1323'),
    ]

    operations = [
        migrations.AlterField(
            model_name='authorization',
            name='authorization_codename',
            field=models.CharField(choices=[('royalty_reports:can_consult_royalty_reports', 'Consulter les rapports de redevances'), ('editor:can_edit_journal_information', 'Modifier la page À propos'), ('authorization:can_manage_authorizations', 'Autorisations'), ('subscriptions:can_manage_individual_subscription', 'Gérer les abonnements '), ('editor:can_manage_issuesubmission', 'Déposer des fichiers de production'), ('subscriptions:can_manage_organisation_members', 'Gérer les membres d’un abonnement'), ('subscriptions:can_manage_organisation_subscription_information', 'Gérer les informations d’un abonnement'), ('subscriptions:can_manage_organisation_subscription_ips', 'Gérer les adresses IP de l’abonnement'), ('editor:can_review_issuesubmission', 'Valider les numéros')], max_length=100, verbose_name='Autorisation'),
        ),
    ]
