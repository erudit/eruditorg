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

    civic = models.TextField(
        null=True, blank=True,
        verbose_name="Adresse",
    )

    street = models.TextField(
        null=True, blank=True,
        verbose_name="Numéro civique"
    )

    city = models.CharField(
        max_length=50,
        verbose_name=_("Ville")
    )

    pobox = models.CharField(
        max_length=50,
        verbose_name=_("Casier postal")
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

    exemption_code = models.CharField(
        max_length=1,
        verbose_name=_("Code d'exemption")
    )

    currency = models.CharField(
        max_length=3,
        verbose_name=_("Devise")
    )

    class Meta:
        verbose_name = _("Client")
        verbose_name_plural = _("Clients")

    def __str__(self):
        return "{} ({}, {})".format(
            self.organisation,
            self.lastname,
            self.firstname
        )


class RenewalNotice(models.Model):
    """ RenewalNotice

    A notice that is sent every year to remind the client to
    remind their subscription """

    renewal_number = models.CharField(
        max_length=10,
        verbose_name="Numéro d'avis"
    )

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

    class Meta:
        verbose_name = _("Avis de renouvellement")
        verbose_name_plural = _("Avis de renouvellement")

    def __str__(self):
        return "Avis ({})".format(
            self.paying_customer,
        )


class Product(models.Model):

    code = models.CharField(
        max_length=30
    )

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

    class Meta:
        verbose_name = _("Produit")
        verbose_name_plural = _("Produits")

    def __str__(self):
        return self.title
