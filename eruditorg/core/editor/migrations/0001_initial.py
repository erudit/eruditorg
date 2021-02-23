# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django_fsm
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ("erudit", "0001_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("resumable_uploads", "0004_auto_20151218_1612"),
    ]

    operations = [
        migrations.CreateModel(
            name="IssueSubmission",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True, serialize=False, verbose_name="ID", primary_key=True
                    ),
                ),
                ("status", django_fsm.FSMField(max_length=50, default="D")),
                ("year", models.CharField(max_length=9, verbose_name="Année")),
                (
                    "volume",
                    models.CharField(max_length=100, verbose_name="Volume", null=True, blank=True),
                ),
                ("number", models.CharField(max_length=100, verbose_name="Numéro")),
                (
                    "date_created",
                    models.DateTimeField(verbose_name="Date de l'envoi", auto_now_add=True),
                ),
                (
                    "date_modified",
                    models.DateTimeField(auto_now=True, verbose_name="Date de modification"),
                ),
                ("comment", models.TextField(verbose_name="Commentaire", null=True, blank=True)),
                (
                    "contact",
                    models.ForeignKey(
                        on_delete=models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="Personne contact",
                    ),
                ),
                (
                    "journal",
                    models.ForeignKey(
                        on_delete=models.deletion.CASCADE, to="erudit.Journal", verbose_name="Revue"
                    ),
                ),
            ],
            options={
                "verbose_name": "Envoi de numéro",
                "verbose_name_plural": "Envois de numéros",
            },
        ),
        migrations.CreateModel(
            name="IssueSubmissionFilesVersion",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True, serialize=False, verbose_name="ID", primary_key=True
                    ),
                ),
                (
                    "created",
                    models.DateTimeField(verbose_name="Date de création", auto_now_add=True),
                ),
                (
                    "updated",
                    models.DateTimeField(auto_now=True, verbose_name="Date de modification"),
                ),
                (
                    "issue_submission",
                    models.ForeignKey(
                        on_delete=models.deletion.CASCADE,
                        verbose_name="Envoi de numéro",
                        to="editor.IssueSubmission",
                        related_name="files_versions",
                    ),
                ),
                ("submissions", models.ManyToManyField(to="resumable_uploads.ResumableFile")),
            ],
            options={
                "verbose_name": "Version de fichiers d'un envoi de numéro",
                "verbose_name_plural": "Versions de fichiers d'envois de numéro",
                "ordering": ["created"],
            },
        ),
        migrations.CreateModel(
            name="IssueSubmissionStatusTrack",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True, serialize=False, verbose_name="ID", primary_key=True
                    ),
                ),
                (
                    "created",
                    models.DateTimeField(verbose_name="Date de création", auto_now_add=True),
                ),
                ("status", models.CharField(max_length=100, verbose_name="statut")),
                (
                    "files_version",
                    models.ForeignKey(
                        on_delete=models.deletion.CASCADE,
                        verbose_name="Version des fichiers",
                        to="editor.IssueSubmissionFilesVersion",
                        null=True,
                        blank=True,
                    ),
                ),
                (
                    "issue_submission",
                    models.ForeignKey(
                        on_delete=models.deletion.CASCADE,
                        verbose_name="Changements de statut",
                        to="editor.IssueSubmission",
                        related_name="status_tracks",
                    ),
                ),
            ],
            options={
                "verbose_name": "Changement de statut d'un envoi de numéro",
                "verbose_name_plural": "Changements de statut d'envois de numéro",
                "ordering": ["created"],
            },
        ),
    ]
