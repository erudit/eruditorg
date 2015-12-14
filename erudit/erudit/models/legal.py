from django.db import models
from django.utils.translation import gettext as _

from .core import Journal


class Contract(models.Model):
    """Contrat"""

    # parties
    journal = models.ForeignKey(
        Journal,
        related_name='contracts',
        verbose_name=_("Revue"),
    )

    type = models.ForeignKey(
        'ContractType',
        related_name='contracts',
        verbose_name=_("Type"),
    )
    date_start = models.DateField(
        verbose_name=_("Début"),
        help_text=_("Date de début du contrat, format aaaa-mm-jj"),
    )
    date_end = models.DateField(
        verbose_name=_("Fin"),
        help_text=_("Date de fin du contrat, format aaaa-mm-jj"),
    )
    date_signature = models.DateField(
        null=True, blank=True,
        verbose_name=_("Signé le"),
        help_text=_("Date de signature du contrat, format aaaa-mm-jj"),
    )
    # signatory

    # quotation # cen-r devis production

    # files upload

    status = models.ForeignKey(
        'ContractStatus',
        related_name='contracts',
        null=True, blank=True,
        verbose_name=_("État"),
    )

    def __str__(self):
        return "{:s} {:s} {:d}".format(
            self.journal.code,
            self.type.code,
            self.date_start.year,
        )

    class Meta:
        verbose_name = _("Contrat")
        verbose_name_plural = _("Contrats")
        ordering = ['journal', ]


class ContractType(models.Model):
    """Type de contrat"""

    code = models.CharField(
        max_length=255,
        verbose_name=_("Code"),
        help_text=_("Court identifiant utilisé dans le nom automatique des contrats"),
    )
    name = models.CharField(
        max_length=255,
        verbose_name=_("Nom"),
    )

    def __str__(self):
        return "{:s} : {:s}".format(
            self.code,
            self.name,
        )

    class Meta:
        verbose_name = _("Type de contrat")
        verbose_name_plural = _("Types de contrat")
        ordering = ['name', ]


class ContractStatus(models.Model):
    """Statuts de contrat"""

    name = models.CharField(
        max_length=255,
        verbose_name=_("Nom"),
    )

    def __str__(self):
        return "{:s}".format(
            self.name,
        )

    class Meta:
        verbose_name = _("Statut de contrat")
        verbose_name_plural = _("Statuts de contrat")
        ordering = ['name', ]
