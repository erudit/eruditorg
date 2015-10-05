from django.db import models
from django.utils.translation import gettext as _

from post_office.models import Email


class Client(models.Model):

    lastname = models.CharField(
        max_length=100,
        verbose_name=_("Nom")
    )

    firstname = models.CharField(
        max_length=100,
        null=True, blank=True,
        verbose_name=_("Prénom"),
    )

    erudit_number = models.CharField(
        max_length=120
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

    civic = models.TextField(
        null=True, blank=True,
        verbose_name="Numéro civique"
    )

    street = models.TextField(
        null=True, blank=True,
        verbose_name="Rue"
    )

    city = models.CharField(
        max_length=100,
        null=True, blank=True,
        verbose_name=_("Ville"),
    )

    pobox = models.CharField(
        max_length=100,
        verbose_name=_("Casier postal")
    )

    province = models.CharField(
        max_length=100,
        verbose_name=_("Province")
    )

    country = models.CharField(
        max_length=100,
        null=True, blank=True,
        verbose_name=_("Pays"),
    )

    postal_code = models.CharField(
        max_length=50,
        null=True, blank=True,
        verbose_name=_("Code postal"),
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
        ordering = ['organisation', ]

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
        max_length=20,
        verbose_name="Numéro d'avis"
    )

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
        help_text="Montant des articles demandés (sous-total avant Rabais)",
    )

    rebate = models.DecimalField(
        max_digits=7,
        decimal_places=2,
        null=True, blank=True,
        verbose_name="Rabais",
        help_text="Applicable avant taxes, sur Montant total",
    )

    raw_amount = models.DecimalField(
        max_digits=7,
        decimal_places=2,
        null=True, blank=True,
        verbose_name="Montant brut",
        help_text="Montant total - Rabais (sous-total après Rabais)",
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
        help_text="Montant brut + Taxes (total facturable, taxes incl.)",
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
        blank=True,
        verbose_name="Produits",
    )

    sent_emails = models.ManyToManyField(
        Email,
        blank=True,
        verbose_name="Courriels envoyés",
    )

    @property
    def has_premium(self):
        return self.products.filter(code='Premium').count()

    status = models.ForeignKey('RenewalNoticeStatus', related_name='renewal_notices',
        null=True, blank=True,
        verbose_name="État",
        help_text="Choisir ou ajouter une option à volonté (tagger l'Avis pour suivi)",
    )

    comment = models.TextField(
        null=True, blank=True,
        verbose_name="Commentaire",
        help_text="Commentaire libre pour suivi de l'avis",
    )

    class Meta:
        verbose_name = _("Avis de renouvellement")
        verbose_name_plural = _("Avis de renouvellement")
        ordering = ['paying_customer',]

    def __str__(self):
        return "Avis : {}".format(
            self.paying_customer,
        )


class RenewalNoticeStatus(models.Model):
    """États d'Avis de renouvellement"""

    name = models.CharField(max_length=255,
        verbose_name="Nom",
    )

    def __str__(self):
        return "{:s}".format(
            self.name,
        )

    class Meta:
        verbose_name = "État d'Avis de renouvellement"
        verbose_name_plural = "États d'Avis de renouvellement"
        ordering = ['name',]


class Product(models.Model):

    code = models.CharField(
        max_length=30
    )

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
        verbose_name="Montant 2016",
    )

    titles = models.ManyToManyField(
        'subscription.Product',
        blank=True,
        verbose_name="Titres",
    )

    def is_basket(self):
        return self.titles.count() > 0

    class Meta:
        verbose_name = _("Produit")
        verbose_name_plural = _("Produits")
        ordering = ['title',]

    def __str__(self):
        return self.title
