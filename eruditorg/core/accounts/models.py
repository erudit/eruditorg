# -*- coding: utf-8 -*-

from django.conf import settings
from django.db import models
from django.utils.translation import ugettext_lazy as _

from erudit.models import Organisation


class LegacyAccountProfile(models.Model):
    """ Defines the information associated with a legacy account that was imported from a user DB.

    This model associates a user instance with informations related to its previous database:

    * which database?
    * which identifier into this database?
    * ...

    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, verbose_name=_('Utilisateur'),
        on_delete=models.CASCADE
    )
    """ The user associated with the considered legacy profile. """

    # Mandragore used to be 3
    DB_ABONNEMENTS, DB_RESTRICTION, DB_DRUPAL = 1, 2, 4
    ORIGIN_CHOICES = (
        (DB_ABONNEMENTS, _('Base de données Abonnements')),
        (DB_RESTRICTION, _('Base de données Restrictions')),
        (DB_DRUPAL, _('Base de données Drupal')),
    )
    origin = models.PositiveSmallIntegerField(choices=ORIGIN_CHOICES, verbose_name=_('Origine'))
    """ Defines the origin of the legacy profile (the original database). """

    legacy_id = models.CharField(
        max_length=20, verbose_name=_('Identifiant original'), blank=True, null=True)
    """ Defines the legacy identifier associated with the account (the ID in the legacy DB). """

    organisation = models.OneToOneField(
        Organisation, verbose_name=_('Organisation'), blank=True, null=True,
        on_delete=models.CASCADE)
    """ The legacy profile can be associated with an organisation. """

    synced_with_origin = models.BooleanField(
        verbose_name=_('Synchronisé avec la base de donnée originale'), default=False)
    """ Defines if the legacy account is synced with the original database. Defaults to False. """

    sync_date = models.DateField(verbose_name=_('Date de synchronisation'), blank=True, null=True)
    """ Date at which the legacy account was last synchronized with its database. """

    class Meta:
        verbose_name = _('Profil de compte utilisateur importé')
        verbose_name_plural = _('Profils de comptes utilisateur importés')

    def __str__(self):
        return "legacy_id={}, email={}, origin={}".format(
            self.legacy_id, self.user.email, self.origin
        )
