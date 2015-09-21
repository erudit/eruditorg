from django.db import models

from django.utils.translation import gettext as _


class Client(models.Model):

    verbose_name = _("Client")

    lastname = models.CharField(
        max_length=50,
        verbose_name=_("Nom")
    )

    firstname = models.CharField(
        max_length=50,
        verbose_name=_("Prénom")
    )

    email = models.EmailField(
        verbose_name=_("Courriel")
    )

    organisation = models.CharField(
        max_length=200
    )

    email = models.EmailField()

    address = models.TextField(
        null=True, blank=True,
        verbose_name="Adresse",
    )

    city = models.CharField(
        max_length=50,
        verbose_name=_("Ville")
    )

    province = models.CharField(
        max_length=50,
        verbose_name=_("Province")
    )

    country = models.CharField(
        max_length=50,
        verbose_name=_("Pays")
    )

    postal_code = models.CharField(
        max_length=50,
        verbose_name=_("Code postal")
    )


class RenewalNotice(models.Model):
    """ RenewalNotice

    A notice that is sent every year to remind the client to
    remind their subscription """

    verbose_name = _("Avis de renouvellement")

    paying_customer = models.ForeignKey(
        'Client',
        related_name="paid_renewals"
    )

    receiving_customer = models.ForeignKey(
        'Client',
        related_name="received_renewals"
    )

    po_number = models.CharField(
        max_length=30
    )

    amount_total = models.DecimalField(
        max_digits=7,
        decimal_places=2
    )

    rebate = models.DecimalField(
        max_digits=7,
        decimal_places=2
    )

    raw_amount = models.DecimalField(
        max_digits=7,
        decimal_places=2
    )

    federal_tax = models.DecimalField(
        max_digits=7,
        decimal_places=2
    )

    provincial_tax = models.DecimalField(
        max_digits=7,
        decimal_places=2
    )

    harmonized_tax = models.DecimalField(
        max_digits=7,
        decimal_places=2
    )

    net_amount = models.DecimalField(
        max_digits=7,
        decimal_places=2
    )

    currency = models.CharField(
        max_length=5,
    )

    date_created = models.DateField()

    products = models.ManyToManyField(
        'Product'
    )

    def get_notice_number(self):
        pass


class Product(models.Model):

    verbose_name = _("Produit")

    title = models.CharField(
        max_length=200
    )

    description = models.CharField(
        max_length=200
    )

    amount = models.DecimalField(
        max_digits=7,
        decimal_places=2
    )

    titles = models.ManyToManyField(
        'subscription.Product'
    )
