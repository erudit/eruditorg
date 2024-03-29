# Generated by Django 2.0.13 on 2019-03-22 17:55

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="SiteMessage",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
                    ),
                ),
                (
                    "label",
                    models.CharField(
                        default="",
                        help_text="Pour l'administration.",
                        max_length=64,
                        verbose_name="Libelé",
                    ),
                ),
                (
                    "message",
                    models.TextField(
                        help_text="Message à afficher. Peut contenir du HTML.",
                        verbose_name="Message",
                    ),
                ),
                (
                    "message_fr",
                    models.TextField(
                        help_text="Message à afficher. Peut contenir du HTML.",
                        null=True,
                        verbose_name="Message",
                    ),
                ),
                (
                    "message_en",
                    models.TextField(
                        help_text="Message à afficher. Peut contenir du HTML.",
                        null=True,
                        verbose_name="Message",
                    ),
                ),
                (
                    "level",
                    models.CharField(
                        choices=[
                            ("DEBUG", "Normal (gris)"),
                            ("INFO", "Information (vert)"),
                            ("WARNING", "Avertissement (jaune)"),
                            ("ERROR", "Alerte (orange)"),
                            ("CRITICAL", "Critique (rouge)"),
                        ],
                        default="DEBUG",
                        help_text="Niveau du message (couleur d'affichage).",
                        max_length=8,
                        verbose_name="Niveau",
                    ),
                ),
                (
                    "active",
                    models.BooleanField(
                        default=False,
                        help_text="Pour activer manuellement le message.",
                        verbose_name="Actif",
                    ),
                ),
                (
                    "start_date",
                    models.DateTimeField(
                        blank=True,
                        help_text="Date à laquelle débuter l'affichage du message.",
                        null=True,
                        verbose_name="Date de début d'affichage",
                    ),
                ),
                (
                    "end_date",
                    models.DateTimeField(
                        blank=True,
                        help_text="Date à laquelle arrêter l'affichage du message.",
                        null=True,
                        verbose_name="Date de fin d'affichage",
                    ),
                ),
                (
                    "setting",
                    models.CharField(
                        blank=True,
                        help_text="Si le site contient un réglage avec ce nom et que ce réglage est à <em>True</em>, le message sera afficher.",
                        max_length=64,
                        null=True,
                        verbose_name="Réglage",
                    ),
                ),
            ],
            options={
                "verbose_name": "Message global du site",
                "verbose_name_plural": "Messages globaux du site",
            },
        ),
    ]
