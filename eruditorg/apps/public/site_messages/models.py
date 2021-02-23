from django.db import models
from django.utils.translation import gettext_lazy as _

from .managers import SiteMessageManager


class TargetSite(models.Model):
    """
    Target site where to display site messages.
    """

    TARGET_SITE_PUBLIC, TARGET_SITE_LIBRARY, TARGET_SITE_JOURNAL = "P", "L", "J"
    TARGET_SITE_CHOICES = (
        (TARGET_SITE_PUBLIC, _("Public")),
        (TARGET_SITE_LIBRARY, _("Tableau de bord des bibliothèques")),
        (TARGET_SITE_JOURNAL, _("Tableau de bord des revues")),
    )
    site = models.CharField(
        verbose_name=_("Site cible"),
        choices=TARGET_SITE_CHOICES,
        blank=False,
        null=False,
        default=TARGET_SITE_PUBLIC,
        max_length=8,
        help_text=_("Site cible"),
    )
    """ The target site. """

    class Meta:
        verbose_name = _("Site cible")
        verbose_name_plural = _("Sites cibles")

    def __str__(self):
        for key, site in self.TARGET_SITE_CHOICES:
            if key == self.site:
                return str(site)
        return self.site


class SiteMessage(models.Model):
    """
    Site message to be displayed on the targeted site.
    """

    label = models.CharField(
        verbose_name=_("Libelé"),
        blank=False,
        null=False,
        default="",
        max_length=64,
        help_text=_("Pour l'administration."),
    )
    """ The administration label. """
    message = models.TextField(
        verbose_name=_("Message"),
        help_text=_("Message à afficher. Peut contenir du HTML."),
    )
    """ The message to be displayed. """
    level = models.CharField(
        verbose_name=_("Niveau"),
        choices=(
            ("DEBUG", _("Normal (gris)")),
            ("INFO", _("Information (vert)")),
            ("WARNING", _("Avertissement (jaune)")),
            ("ERROR", _("Alerte (orange)")),
            ("CRITICAL", _("Critique (rouge)")),
        ),
        default="DEBUG",
        max_length=8,
        help_text=_("Niveau du message (couleur d'affichage)."),
    )
    """ The level of the message, which will detemine it's displayed color. """
    target_sites = models.ManyToManyField(
        TargetSite,
        verbose_name=_("Sites cibles"),
        related_name="+",
        blank=False,
    )
    """ The targeted sites where the message should be displayed. """
    active = models.BooleanField(
        verbose_name=_("Actif"),
        default=False,
        help_text=_("Pour activer manuellement le message."),
    )
    """ Switch to manualy activate the message. """
    start_date = models.DateTimeField(
        verbose_name=_("Date de début d'affichage"),
        blank=True,
        null=True,
        help_text=_("Date à laquelle débuter l'affichage du message."),
    )
    """ Date and time when to start displaying the message. """
    end_date = models.DateTimeField(
        verbose_name=_("Date de fin d'affichage"),
        blank=True,
        null=True,
        help_text=_("Date à laquelle arrêter l'affichage du message."),
    )
    """ Date and time when to stop displaying the message. """
    setting = models.CharField(
        verbose_name=_("Réglage"),
        blank=True,
        null=True,
        max_length=64,
        help_text=_(
            "Si le site contient un réglage avec ce nom et que ce réglage est à \
            <em>True</em>, le message sera affiché."
        ),
    )
    """ The name of a site setting to display the message if it's set to True. """

    objects = SiteMessageManager()

    class Meta:
        verbose_name = _("Message global du site")
        verbose_name_plural = _("Messages globaux du site")

    def __str__(self):
        return self.label
