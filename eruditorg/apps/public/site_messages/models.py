from django.db import models
from django.utils.translation import gettext_lazy as _


class SiteMessage(models.Model):
    """
    Site message to be displayed at the bottom of every pages.
    """
    label = models.CharField(
        verbose_name=_('Libelé'),
        blank=False,
        null=False,
        default='',
        max_length=64,
        help_text=_("Pour l'administration."),
    )
    """ The administration label. """
    message = models.TextField(
        verbose_name=_('Message'),
        help_text=_('Message à afficher. Peut contenir du HTML.'),
    )
    """ The message to be displayed. """
    level = models.CharField(
        verbose_name=_('Niveau'),
        choices=(
            ('DEBUG', _('Normal (gris)')),
            ('INFO', _('Information (vert)')),
            ('WARNING', _('Avertissement (jaune)')),
            ('ERROR', _('Alerte (orange)')),
            ('CRITICAL', _('Critique (rouge)')),
        ),
        default='DEBUG',
        max_length=8,
        help_text=_("Niveau du message (couleur d'affichage)."),
    )
    """ The level of the message, which will detemine it's displayed color. """
    active = models.BooleanField(
        verbose_name=_('Actif'),
        default=False,
        help_text=_('Pour activer manuellement le message.'),
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
        verbose_name=_('Réglage'),
        blank=True,
        null=True,
        max_length=64,
        help_text=_('Si le site contient un réglage avec ce nom et que ce réglage est à \
            <em>True</em>, le message sera afficher.'),
    )
    """ The name of a site setting to display the message if it's set to True. """

    class Meta:
        verbose_name = _('Message global du site')
        verbose_name_plural = _('Messages globaux du site')

    def __str__(self):
        return self.label
