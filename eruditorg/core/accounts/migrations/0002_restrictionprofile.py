# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("erudit", "0012_auto_20160510_1002"),
        ("accounts", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="RestrictionProfile",
            fields=[
                (
                    "id",
                    models.AutoField(
                        serialize=False, auto_created=True, primary_key=True, verbose_name="ID"
                    ),
                ),
                (
                    "password",
                    models.CharField(blank=True, max_length=50, verbose_name="Mot de passe"),
                ),
                (
                    "restriction_id",
                    models.PositiveIntegerField(verbose_name="Identifiant DB Restriction"),
                ),
                (
                    "organisation",
                    models.OneToOneField(
                        on_delete=models.deletion.CASCADE,
                        to="erudit.Organisation",
                        verbose_name="Organisation",
                    ),
                ),
                (
                    "user",
                    models.OneToOneField(
                        on_delete=models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="Utilisateur",
                    ),
                ),
            ],
            options={
                "verbose_name_plural": "Comptes personnels Restriction",
                "verbose_name": "Compte personnel Restriction",
            },
        ),
    ]
