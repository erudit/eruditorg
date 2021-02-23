# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.utils.timezone
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("contenttypes", "0002_remove_content_type_name"),
        ("auth", "0006_require_contenttypes_0002"),
    ]

    operations = [
        migrations.CreateModel(
            name="Authorization",
            fields=[
                (
                    "id",
                    models.AutoField(
                        verbose_name="ID", auto_created=True, primary_key=True, serialize=False
                    ),
                ),
                (
                    "date_creation",
                    models.DateTimeField(
                        default=django.utils.timezone.now,
                        verbose_name="Date de création",
                        editable=False,
                        null=True,
                    ),
                ),
                (
                    "date_modification",
                    models.DateTimeField(
                        default=django.utils.timezone.now,
                        verbose_name="Date de modification",
                        editable=False,
                        null=True,
                    ),
                ),
                ("object_id", models.PositiveIntegerField(null=True, blank=True)),
                (
                    "authorization_codename",
                    models.CharField(
                        choices=[
                            ("authorization:can_manage_authorizations", "Autorisations"),
                            (
                                "subscriptions:can_manage_individual_subscription",
                                "Valider les numéros",
                            ),
                            ("editor:can_manage_issuesubmission", "Dépôt de fichiers"),
                            ("editor:can_review_issuesubmission", "Valider les numéros"),
                        ],
                        max_length=100,
                    ),
                ),
                (
                    "content_type",
                    models.ForeignKey(
                        on_delete=models.deletion.CASCADE,
                        to="contenttypes.ContentType",
                        blank=True,
                        verbose_name="Type",
                        null=True,
                    ),
                ),
                (
                    "group",
                    models.ForeignKey(
                        on_delete=models.deletion.CASCADE, to="auth.Group", blank=True, null=True
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                        blank=True,
                        null=True,
                    ),
                ),
            ],
            options={
                "verbose_name": "Autorisation",
            },
        ),
    ]
