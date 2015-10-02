from django.db import models

from django.utils.translation import gettext as _


class Client(models.Model):

    lastname = models.CharField(
        max_length=50,
        null=True, blank=True,
        verbose_name=_("Nom"),
    )

    firstname = models.CharField(
        max_length=50,
        null=True, blank=True,
        verbose_name=_("Prénom"),
    )

    email = models.EmailField(
        null=True, blank=True,
        verbose_name=_("Courriel"),
        help_text="L'avis de renouvellement sera envoyé à cette adresse",
    )

    organisation = models.CharField(
        max_length=200,
        null=True, blank=True,
    )

    address = models.TextField(
        null=True, blank=True,
        verbose_name="Adresse",
    )

    city = models.CharField(
        max_length=50,
        null=True, blank=True,
        verbose_name=_("Ville"),
    )

    province = models.CharField(
        max_length=50,
        null=True, blank=True,
        verbose_name=_("Province"),
    )

    country = models.CharField(
        max_length=50,
        null=True, blank=True,
        verbose_name=_("Pays"),
    )

    postal_code = models.CharField(
        max_length=50,
        null=True, blank=True,
        verbose_name=_("Code postal"),
    )

    class Meta:
        verbose_name = _("Client")
        verbose_name_plural = _("Clients")
        ordering = ['organisation',]

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

    paying_customer = models.ForeignKey(
        'Client',
        related_name="paid_renewals",
        null=True, blank=True,
        verbose_name="Client payeur",
    )

    receiving_customer = models.ForeignKey(
        'Client',
        related_name="received_renewals",
        null=True, blank=True,
        verbose_name="Client receveur",
    )

    po_number = models.CharField(
        max_length=30,
        null=True, blank=True,
        verbose_name="Bon de commande",
        help_text="Numéro de bon de commande",
    )

    amount_total = models.DecimalField(
        max_digits=7,
        decimal_places=2,
        null=True, blank=True,
        verbose_name="Montant total",
        help_text="Montant des articles demandés (sous-total avant rabais)",
    )

    rebate = models.DecimalField(
        max_digits=7,
        decimal_places=2,
        null=True, blank=True,
        verbose_name="Rabais",
        help_text="Applicable avant taxes, sur montant total",
    )

    raw_amount = models.DecimalField(
        max_digits=7,
        decimal_places=2,
        null=True, blank=True,
        verbose_name="Montant brut",
        help_text="Montant total - rabais (sous-total après rabais)",
    )

    federal_tax = models.DecimalField(
        max_digits=7,
        decimal_places=2,
        null=True, blank=True,
        verbose_name="Taxe fédérale",
    )

    provincial_tax = models.DecimalField(
        max_digits=7,
        decimal_places=2,
        null=True, blank=True,
        verbose_name="Taxe provinciale",
    )

    harmonized_tax = models.DecimalField(
        max_digits=7,
        decimal_places=2,
        null=True, blank=True,
        verbose_name="Taxe harmonisée",
    )

    net_amount = models.DecimalField(
        max_digits=7,
        decimal_places=2,
        null=True, blank=True,
        verbose_name="Montant net",
        help_text="Montant brut + taxes (total facturable, taxes incl.)",
    )

    currency = models.CharField(
        max_length=5,
        null=True, blank=True,
        verbose_name="Devise",
    )

    date_created = models.DateField(
        null=True, blank=True,
        verbose_name="Date de création",
    )

    products = models.ManyToManyField(
        'Product',
        null=True, blank=True,
        verbose_name="Produits",
    )

    status = models.ForeignKey('RenewalNoticeStatus', related_name='renewal_notices',
        null=True, blank=True,
        verbose_name="État",
        help_text="Choisir ou ajouter une option à volonté (tag pour mémoire)",
    )

    def get_notice_number(self):
        pass

    class Meta:
        verbose_name = _("Avis de renouvellement")
        verbose_name_plural = _("Avis de renouvellement")
        ordering = ['paying_customer',]

    def __str__(self):
        return "Avis ({})".format(
            self.paying_customer,
        )


class RenewalNoticeStatus(models.Model):
    """États d'avis de renouvellement"""

    name = models.CharField(max_length=255,
        verbose_name="Nom",
    )

    def __str__(self):
        return "{:s}".format(
            self.name,
        )

    class Meta:
        verbose_name = "État d'avis de renouvellement"
        verbose_name_plural = "États d'avis de renouvellement"
        ordering = ['name',]


class Product(models.Model):

    title = models.CharField(
        max_length=200,
        null=True, blank=True,
        verbose_name="Titre",
    )

    description = models.CharField(
        max_length=200,
        null=True, blank=True,
    )

    amount = models.DecimalField(
        max_digits=7,
        decimal_places=2,
        null=True, blank=True,
        verbose_name="Montant",
        verbose_name="Montant 2016",
    )

    titles = models.ManyToManyField(
        'subscription.Product',
        null=True, blank=True,
        verbose_name="Titres",
    )

    class Meta:
        verbose_name = _("Produit")
        verbose_name_plural = _("Produits")
        ordering = ['title',]

    def __str__(self):
        return self.title
