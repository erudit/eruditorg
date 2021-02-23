# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ("erudit", "0001_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="InstitutionIPAddressRange",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
                    ),
                ),
                ("ip_start", models.GenericIPAddressField(verbose_name="Adresse IP de début")),
                ("ip_end", models.GenericIPAddressField(verbose_name="Adresse IP de fin")),
            ],
            options={
                "verbose_name": "Plage d'adresses IP d'institution",
                "verbose_name_plural": "Plages d'adresses IP d'institution",
            },
        ),
        migrations.CreateModel(
            name="JournalAccessSubscription",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
                    ),
                ),
                (
                    "title",
                    models.CharField(verbose_name="Titre", max_length=120, null=True, blank=True),
                ),
                (
                    "created",
                    models.DateTimeField(verbose_name="Date de création", auto_now_add=True),
                ),
                (
                    "updated",
                    models.DateTimeField(verbose_name="Date de modification", auto_now=True),
                ),
                (
                    "date_activation",
                    models.DateField(verbose_name="Date d'activation", null=True, blank=True),
                ),
                (
                    "date_renew",
                    models.DateField(verbose_name="Date de renouvellement", null=True, blank=True),
                ),
                (
                    "renew_cycle",
                    models.PositiveSmallIntegerField(
                        verbose_name="Cycle du renouvellement (en jours)", null=True, blank=True
                    ),
                ),
                ("comment", models.TextField(verbose_name="Commentaire", null=True, blank=True)),
                ("full_access", models.BooleanField(verbose_name="Accès complet", default=False)),
                (
                    "collection",
                    models.ForeignKey(
                        on_delete=models.deletion.CASCADE,
                        to="erudit.Collection",
                        related_name="+",
                        blank=True,
                        verbose_name="Collection",
                        null=True,
                    ),
                ),
                (
                    "journal",
                    models.ForeignKey(
                        on_delete=models.deletion.CASCADE,
                        to="erudit.Journal",
                        related_name="+",
                        blank=True,
                        verbose_name="Revue",
                        null=True,
                    ),
                ),
                (
                    "journals",
                    models.ManyToManyField(
                        verbose_name="Revues",
                        to="erudit.Journal",
                        related_name="_journalaccesssubscription_journals_+",
                        blank=True,
                    ),
                ),
                (
                    "organisation",
                    models.ForeignKey(
                        on_delete=models.deletion.CASCADE,
                        to="erudit.Organisation",
                        blank=True,
                        verbose_name="Organisation",
                        null=True,
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                        blank=True,
                        verbose_name="Utilisateur",
                        null=True,
                    ),
                ),
            ],
            options={
                "verbose_name": "Abonnement aux revues",
                "verbose_name_plural": "Abonnements aux revues",
            },
        ),
        migrations.CreateModel(
            name="JournalManagementPlan",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
                    ),
                ),
                (
                    "title",
                    models.CharField(verbose_name="Titre", max_length=255, null=True, blank=True),
                ),
                ("code", models.SlugField(verbose_name="Code", max_length=100, unique=True)),
                (
                    "max_accounts",
                    models.PositiveSmallIntegerField(verbose_name="Maximum de comptes"),
                ),
            ],
            options={
                "verbose_name": "Forfait de gestion d'une revue",
                "verbose_name_plural": "Forfaits de gestion de revues",
            },
        ),
        migrations.CreateModel(
            name="JournalManagementSubscription",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
                    ),
                ),
                (
                    "title",
                    models.CharField(verbose_name="Titre", max_length=120, null=True, blank=True),
                ),
                (
                    "created",
                    models.DateTimeField(verbose_name="Date de création", auto_now_add=True),
                ),
                (
                    "updated",
                    models.DateTimeField(verbose_name="Date de modification", auto_now=True),
                ),
                (
                    "date_activation",
                    models.DateField(verbose_name="Date d'activation", null=True, blank=True),
                ),
                (
                    "date_renew",
                    models.DateField(verbose_name="Date de renouvellement", null=True, blank=True),
                ),
                (
                    "renew_cycle",
                    models.PositiveSmallIntegerField(
                        verbose_name="Cycle du renouvellement (en jours)", null=True, blank=True
                    ),
                ),
                ("comment", models.TextField(verbose_name="Commentaire", null=True, blank=True)),
                (
                    "journal",
                    models.ForeignKey(
                        on_delete=models.deletion.CASCADE, verbose_name="Revue", to="erudit.Journal"
                    ),
                ),
                (
                    "plan",
                    models.ForeignKey(
                        on_delete=models.deletion.CASCADE,
                        verbose_name="Forfait",
                        to="subscription.JournalManagementPlan",
                    ),
                ),
            ],
            options={
                "verbose_name": "Abonnement de gestion de revue",
                "verbose_name_plural": "Abonnements de gestion de revue",
            },
        ),
        migrations.AddField(
            model_name="institutionipaddressrange",
            name="subscription",
            field=models.ForeignKey(
                on_delete=models.deletion.CASCADE,
                verbose_name="Abonnement aux revues",
                to="subscription.JournalAccessSubscription",
            ),
        ),
    ]
