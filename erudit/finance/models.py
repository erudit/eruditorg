from django.db import models
from erudit import models as e


class Currency(models.Model):
    """Devise"""

    code
    name


class Quotation(models.Model):
    """Devis"""
    contractor
    journal
    description

    items

    date_start
    date_end


class QuotationItem(models.Model):

    quotation
    period
    total


class Invoice(models.Model):
    """Facture"""

    # identification
    id_sage
    id_subcontractor
    quotation

    # header
    date
    journal #client? library
    total_invoice_subcontractor
    total

    # followup
    status
    comment
