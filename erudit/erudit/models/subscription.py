from django.db import models
from django.utils.translation import gettext as _

from core.subscription import models as s

from .core import Journal, YEARS


class SubscriptionPrice(models.Model):
    """Tarif d'abonnement"""

    journal = models.ForeignKey(
        Journal,
        verbose_name=_("Revue"),
    )
    year = models.CharField(
        max_length=255,
        choices=YEARS,
        verbose_name=_("Année"),
    )
    type = models.ForeignKey(
        'SubscriptionType',
        verbose_name=_("Type"),
    )
    zone = models.ForeignKey(
        'SubscriptionZone',
        verbose_name=_("Zone"),
    )

    price = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        null=True, blank=True,
        verbose_name=_("Prix"),
    )
    currency = models.ForeignKey(
        s.Currency,
        null=True, blank=True,
        verbose_name=_("Devise"),
    )

    approved = models.BooleanField(
        default=False,
        verbose_name=_("Approuvé"),
    )
    date_approved = models.DateField(
        null=True, blank=True,
        verbose_name=_("Date d'approbation"),
    )

    def __str__(self):
        return "{:s} : {:s} {:s} : {:s} {:s}".format(
            self.journal.code,
            self.type.code,
            self.zone.code,
            str(self.price),
            self.currency.code,
        )

    class Meta:
        verbose_name = _("Tarif d'abonnement")
        verbose_name_plural = _("Tarifs d'abonnement")
        ordering = [
            'journal',
            'year',
            'type',
            'zone',
        ]
        app_label = 'subscription'


class SubscriptionType(models.Model):
    """Type d'abonnement"""
    # TODO : data migration : individual, organisation, ...

    code = models.CharField(
        max_length=255,
        verbose_name=_("Code"),
    )
    name = models.CharField(
        max_length=255,
        verbose_name=_("Nom"),
    )

    def __str__(self):
        return "{:s} [{:s}]".format(
            self.name,
            self.code,
        )

    class Meta:
        verbose_name = _("Type d'abonnement")
        verbose_name_plural = _("Types d'abonnement")
        ordering = ['name', ]
        app_label = 'subscription'


class SubscriptionZone(models.Model):
    """Zone d'abonnement"""
    # TODO : data migration : {UE, CA, other}

    code = models.CharField(
        max_length=255,
        verbose_name=_("Code"),
    )
    name = models.CharField(
        max_length=255,
        verbose_name=_("Nom"),
    )

    def __str__(self):
        return "{:s} [{:s}]".format(
            self.name,
            self.code,
        )

    class Meta:
        verbose_name = _("Zone d'abonnement")
        verbose_name_plural = _("Zones d'abonnement")
        ordering = ['name', ]
        app_label = 'subscription'


class Basket(models.Model):
    """Panier"""
    # TODO : data migration : {all, sc_soc, sc_hum, discovery, legal}

    code = models.CharField(
        max_length=255,
        verbose_name=_("Code"),
    )
    name = models.CharField(
        max_length=255,
        verbose_name=_("Nom"),
    )
    journals = models.ManyToManyField(
        Journal,
        verbose_name=_("Revues"),
        help_text=_("Choisir les revues composant ce panier."),
    )

    def __str__(self):
        return "{:s} [{:s}]".format(
            self.name,
            self.code,
        )

    class Meta:
        verbose_name = _("Panier")
        verbose_name_plural = _("Paniers")
        ordering = ['name', ]
        app_label = 'subscription'
