# -*- coding: utf-8 -*-

from django.db import models
from django.utils.translation import gettext as _

from .core import Currency
from .core import Journal


class Quotation(models.Model):
    """Devis"""

    # contractor
    journal = models.ForeignKey(Journal, null=True, blank=True,)
    description = models.TextField(null=True, blank=True,)

    date_start = models.DateField(null=True, blank=True,)
    date_end = models.DateField(null=True, blank=True,)


class QuotationItem(models.Model):
    """Élément du devis"""

    quotation = models.ForeignKey('Quotation')

    # period
    total = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        null=True, blank=True,
    )
    currency = models.ForeignKey(Currency, null=True, blank=True,)


INVOICE_STATUS_CHOICES = [
    ('D', 'Draft'),
    ('V', 'Valid'),
    ('S', 'Sent'),
    ('P', 'Paid'),
]


class Invoice(models.Model):
    """Facture"""

    # identification
    id_sage = models.IntegerField(
        null=True, blank=True,
        verbose_name=_("Id facture SAGE"),
        help_text=_("Identifiant de la facture dans SAGE."),
    )
    id_subcontractor = models.IntegerField(
        null=True, blank=True,
        verbose_name=_("Id facture sous-contractant"),
        help_text=_(
            "Identifiant de la facture du sous-contractant qui couvre cette facture (ex.: CEN-R)."
        ),
    )
#    quotation = models.ForeignKey(
#        'Quotation',
#        null=True, blank=True,
#        verbose_name="Soumission",
#        help_text="Identifiant de la soumission du sous-contractant qui couvre cette facture (ex.: CEN-R)",  # noqa
#    )

    # header
    date = models.DateField(null=True, blank=True,)
    journal = models.ForeignKey(
        Journal,
        null=True, blank=True,
        verbose_name=_("Revue"),
        help_text=_("Revue facturée"),
    )
    total_invoice_subcontractor = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        null=True, blank=True,
        verbose_name=_("Total facture sous-contractant"),
        help_text=_("Total de la facture du sous-contractant (ex.: CEN-R)"),
    )
    total = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        null=True, blank=True,
        verbose_name=_("Total"),
    )
    currency = models.ForeignKey(
        Currency,
        null=True, blank=True,
        verbose_name=_("Devise"),
    )

    # followup
    status = models.CharField(
        max_length=255,
        choices=INVOICE_STATUS_CHOICES,
        verbose_name=_("Statut"),
    )

    def __str__(self):
        return "{:s} {:s} : {:s} {:s}".format(
            self.journal.code,
            str(self.date),
            str(self.total),
            self.currency,
        )

    class Meta:
        verbose_name = _("Facture")
        verbose_name_plural = _("Factures")
        ordering = ['journal', ]
