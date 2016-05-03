from django.db import models
from django.utils.translation import gettext as _

from .core import Currency
from .core import Journal


class GrantingAgency(models.Model):
    """Organisme subventionnaire"""

    code = models.CharField(
        max_length=255,
        verbose_name=_("Code"),
        help_text=_("Acronyme"),
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
        verbose_name = _("Organisme subventionnaire")
        verbose_name_plural = _("Organismes subventionnaires")
        ordering = ['name', ]


class Grant(models.Model):
    """Subvention"""

    granting_agency = models.ForeignKey(
        'GrantingAgency',
        verbose_name=_("Organisme subventionnaire"),
    )
    journal = models.ForeignKey(
        Journal,
        related_name='grants',
        verbose_name=_("Revue"),
        help_text=_("Revue ayant obtenu cette subvention"),
    )

    amount = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        null=True, blank=True,
        verbose_name=_("Montant"),
    )
    currency = models.ForeignKey(
        Currency,
        null=True, blank=True,
        verbose_name=_("Devise"),
    )

    date_start = models.DateField(
        null=True, blank=True,
        verbose_name=_("Date de début"),
    )
    date_end = models.DateField(
        null=True, blank=True,
        verbose_name=_("Date de fin"),
    )

    def __str__(self):
        return "{:s} : {:s} {:s}".format(
            self.journal.code,
            self.granting_agency.code,
            str(self.amount),
        )

    class Meta:
        verbose_name = _("Subvention")
        verbose_name_plural = _("Subventions")
        ordering = ['journal', ]
