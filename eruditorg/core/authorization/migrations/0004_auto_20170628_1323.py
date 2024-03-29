# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2017-06-28 18:23
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("authorization", "0003_auto_20161007_0900"),
    ]

    operations = [
        migrations.AlterField(
            model_name="authorization",
            name="authorization_codename",
            field=models.CharField(
                choices=[
                    (
                        "royalty_reports:can_consult_royalty_reports",
                        "Consultation des rapports de redevances",
                    ),
                    ("editor:can_edit_journal_information", "Éditer l'à-propos"),
                    ("authorization:can_manage_authorizations", "Autorisations"),
                    ("subscriptions:can_manage_individual_subscription", "Abonnements"),
                    ("editor:can_manage_issuesubmission", "Dépôt de fichiers"),
                    (
                        "subscriptions:can_manage_organisation_members",
                        "Gestion des membres d'un abonnement",
                    ),
                    (
                        "subscriptions:can_manage_organisation_subscription_information",
                        "Gestion des informations d'un abonnement",
                    ),
                    (
                        "subscriptions:can_manage_organisation_subscription_ips",
                        "Gestion des adresses IP de l'abonnement",
                    ),
                    ("editor:can_review_issuesubmission", "Valider les numéros"),
                ],
                max_length=100,
                verbose_name="Autorisation",
            ),
        ),
    ]
