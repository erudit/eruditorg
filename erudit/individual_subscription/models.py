# from .legacy.legacy_models import *  # NOQA

from django.db import models
from django.utils.translation import ugettext_lazy as _


class IndividualAccount(models.Model):
    """
    Personal account used in erudit.org
    to access protected content.
    """
    email = models.CharField(max_length=120, verbose_name=_("Courriel"))
    password = models.CharField(max_length=50, verbose_name=_("Mot de passe"))
    organization = models.ForeignKey("Organization", verbose_name=_("Organisation"),)
    firstname = models.CharField(max_length=30, verbose_name=_("Prénom"))
    lastname = models.CharField(max_length=30, verbose_name=_("Nom"))

    class Meta:
        verbose_name = _("Compte personnel")
        verbose_name_plural = _("Comptes personnels")


class Organization(models.Model):
    """
    Entity which deals with member individual accounts :
    Wikipedia, AEIQ, Revue.
    """
    name = models.CharField(
        max_length=255,
        verbose_name=_("Nom")
    )

    max_accounts = models.PositiveSmallIntegerField(
        verbose_name=_("Maximum de comptes")
    )

    access_full = models.BooleanField(
        default=False,
        verbose_name=_("Accès à toutes les ressources")
    )

    access_journal = models.ManyToManyField(
        "erudit.journal",
        verbose_name=_("Revues"),
    )

    # TODO not yet in erudit models
    # access_basket = models.ManyToManyField(
    #    "Basket",
    #    verbose_name=_("Panier"),
    # )

    class Meta:
        verbose_name = _("Organisation")
        verbose_name_plural = _("Organisations")
