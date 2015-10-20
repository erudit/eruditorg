from django.db import models
from django.utils.translation import gettext as _

from post_office.models import Email


class Country(models.Model):
    code = models.CharField(
        max_length=255,
        null=True, blank=True,
    )
    name = models.CharField(
        max_length=255,
        verbose_name=_("Nom")
    )
    currency = models.ForeignKey(
        'Currency',
        null=True, blank=True,
        verbose_name="Devise",
        related_name='pays'
    )

    locale = models.CharField(
        max_length=5,
        verbose_name=_("Locale")
    )

    def __str__(self):
        return "{:s} [{:s}]".format(
            self.name,
            self.code,
        )

    class Meta:
        verbose_name = _("Pays")
        verbose_name_plural = _("Pays")
        ordering = [
            'name',
        ]


class Currency(models.Model):
    code = models.CharField(
        max_length=255,
    )
    name = models.CharField(
        max_length=255,
        verbose_name=_("Nom")
    )

    def __str__(self):
        return "{:s}".format(
            self.code,
        )

    class Meta:
        verbose_name = _("Devise")
        verbose_name_plural = _("Devises")
        ordering = [
            'code',
        ]


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
        null=True, blank=True,
        verbose_name=_("Casier postal")
    )

    province = models.CharField(
        max_length=100,
        null=True, blank=True,
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
        null=True, blank=True,
        verbose_name=_("Code d'exemption")
    )

    currency = models.CharField(
        max_length=3,
        null=True, blank=True,
        verbose_name=_("Devise")
    )

    def __str__(self):
        return "{:s} ({:s}, {:s})".format(
            self.organisation,
            self.lastname,
            self.firstname,
        )

    class Meta:
        verbose_name = _("Client")
        verbose_name_plural = _("Clients")
        ordering = [
            'organisation',
        ]


NOTICE_STATUS_CHOICES = (
    ('DONT', 'Ne pas envoyer'),
    ('TODO', 'À envoyer'),
    ('SENT', 'Envoyé'),
    ('REDO', 'À ré-envoyer'),
    ('LATE', 'Envoyer plus tard'),
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
        default=0.0,
        verbose_name="Montant total",
        help_text="Montant des articles demandés (sous-total avant Rabais)",
    )

    rebate = models.DecimalField(
        max_digits=7,
        decimal_places=2,
        default=0.0,
        verbose_name="Rabais",
        help_text="Applicable avant taxes, sur Montant total",
    )

    raw_amount = models.DecimalField(
        max_digits=7,
        decimal_places=2,
        default=0.0,
        verbose_name="Montant brut",
        help_text="Montant total - Rabais (sous-total après Rabais)",
    )

    federal_tax = models.DecimalField(
        max_digits=7,
        decimal_places=2,
        default=0.0,
        verbose_name="Taxe fédérale",
    )

    provincial_tax = models.DecimalField(
        max_digits=7,
        decimal_places=2,
        default=0.0,
        verbose_name="Taxe provinciale",
    )

    harmonized_tax = models.DecimalField(
        max_digits=7,
        decimal_places=2,
        default=0.0,
        verbose_name="Taxe harmonisée",
    )

    net_amount = models.DecimalField(
        max_digits=7,
        decimal_places=2,
        default=0.0,
        verbose_name="Montant net",
        help_text="Montant brut + Taxes (total facturable, taxes incl.)",
    )

    currency = models.CharField(
        max_length=5,
        null=True, blank=True,
        verbose_name="Devise",
    )

    has_basket = models.BooleanField(
        default=False,
        editable=False,
        verbose_name="Avec panier",
    )

    has_rebate = models.BooleanField(
        default=False,
        verbose_name="Avec rabais",
    )

    has_been_answered = models.BooleanField(
        default=False,
        verbose_name=_("A répondu")
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

    is_correct = models.BooleanField(
        editable=False,
        default=True,
        verbose_name="Est correct?",
        help_text="Renseigné automatiquement par système.",
    )

    error_msg = models.TextField(
        editable=False,
        default="",
        verbose_name="Messages d'erreur",
        help_text="Renseigné automatiquement par système si existe erreur(s).",
    )

    sent_emails = models.ManyToManyField(
        Email,
        blank=True,
        verbose_name="Courriels envoyés",
    )

    status = models.CharField(
        max_length=4,
        choices=NOTICE_STATUS_CHOICES,
        default='DONT',
        verbose_name="État",
    )

    comment = models.TextField(
        null=True, blank=True,
        verbose_name="Commentaire",
        help_text="Commentaire libre pour suivi de l'avis",
    )

    has_renewed = models.BooleanField(
        verbose_name=_("Renouvellement confirmé")
    )

    has_refused = models.BooleanField(
        verbose_name=_("Renouvellement refusé")
    )

    def get_premium(self):
        return self.products.filter(code='Premium').first()

    def get_basket(self):
        return self.products.filter(titles__isnull=False).first()

    def get_notice_number(self):
        pass

    def has_errors(self):
        """Checks for business logic errors and returns a
        list of errors.

        Each error is a dict of
        * an error code (number of the rule that failed)
        * an error message (explaining the rule that failed)
        * a proof (string showing the data causing the failure)

        'error' and 'error_msg' fields are filled by the save method
        using 'has_errors' method.
        """
        errors = []

        # amounts are correct?
        # test 1
        error = {
            'code': 1,
            'msg': "Montant des produits demandés différent du Montant total",
            'proof': "",
        }

        total_products = sum([p.amount for p in self.products.all()])
        if self.amount_total != total_products:
            proof = "Montant total: {:s}, Montant des produits: {:s}".format(
                str(self.amount_total),
                str(total_products),
            )
            error['proof'] = proof
            errors.append(error)

        # test 2
        error = {
            'code': 2,
            'msg': "Montant brut est différent du Montant total - Rabais",
            'proof': "",
        }
        if self.raw_amount != (float(self.amount_total) - float(self.rebate)):
            proof = "Montant brut: {:s}, Montant total - rabais: {:s}".format(
                str(self.raw_amount),
                str(self.amount_total - self.rebate),
            )
            error['proof'] = proof
            errors.append(error)

        # test 3
        error = {
            'code': 3,
            'msg': "Montant net est différent du Montant brut + taxes",
            'proof': "",
        }
        taxes = self.federal_tax + self.provincial_tax + self.harmonized_tax
        if self.net_amount != (self.raw_amount + taxes):
            proof = "Montant net: {:s}, Montant brut + taxes: {:s}".format(
                str(self.net_amount),
                str(self.raw_amount + taxes),
            )
            error['proof'] = proof
            errors.append(error)

        # currency is correct?
        # test 4
        error = {
            'code': 4,
            'msg': "Aucune Devise associée",
            'proof': "",
        }
        if not self.currency:
            proof = "Devise: {:s}".format(
                self.currency,
            )
            error['proof'] = proof
            errors.append(error)

        # test 5
        error = {
            'code': 5,
            'msg': "Aucun Pays associé au Client payeur",
            'proof': "",
        }
        if not self.paying_customer.country:
            proof = "Pays: {:s}".format(
                self.paying_customer.country,
            )
            error['proof'] = proof
            errors.append(error)

        # test 6
        error = {
            'code': 6,
            'msg': """La Devise et le Pays ne concordent pas avec
            les données de référence.""",
            'proof': "",
        }
        currency = self.currency.upper()
        country = self.receiving_customer.country
        if currency and country:
            fail = False
            # CAD and EUR must follow Country in reference data
            if currency in ('CAD', 'EUR'):
                try:
                    curr = Currency.objects.get(code__iexact=currency)
                    country = Country.objects.get(
                        name__iexact=country,
                        currency=curr,
                    )
                except:
                    fail = True
            # USD cannot be used for Country in reference data
            elif currency == 'USD':
                try:
                    Country.objects.get(name__iexact=country)
                    fail = True
                except:
                    pass
            # USD : only other accepted Currency and for all other Countries
            else:
                fail = True

            if fail:
                proof = "Devise: {:s}, Pays: {:s}".format(
                    currency,
                    country,
                )
                error['proof'] = proof
                errors.append(error)

        # email is correct?
        # test 7
        error = {
            'code': 7,
            'msg': "Aucun courriel associé au Client payeur",
            'proof': "",
        }
        if not self.paying_customer.email:
            proof = "Courriel: {:s}".format(
                self.paying_customer.email,
            )
            error['proof'] = proof
            errors.append(error)

        return errors

    def test_has_basket(self):
        """Renewal Notice has a basket
        if one of its product has many titles
        (Basket = Product of Products)
        """
        has_basket = False
        for product in self.products.all():
            if len(product.titles.all()) > 0:
                has_basket = True
        return has_basket

    def save(self, *args, **kwargs):
        # has_basket
        if not self.id:
            super(RenewalNotice, self).save(*args, **kwargs)
        self.has_basket = self.test_has_basket()

        # errors
        self.is_correct = True

        self.error_msg = ""
        if self.has_errors():
            self.is_correct = False
            for error in self.has_errors():
                msg = "ERREUR {:d} : {:s}\n    Preuve : {:s}\n\n".format(
                    error['code'],
                    error['msg'],
                    error['proof'],
                )
                self.error_msg = self.error_msg + msg

        # Call the "real" save() method.
        super(RenewalNotice, self).save(*args, **kwargs)

    def __str__(self):
        return "Avis : {:s}".format(
            self.renewal_number,
        )

    class Meta:
        verbose_name = _("Avis de renouvellement")
        verbose_name_plural = _("Avis de renouvellement")
        ordering = [
            'paying_customer',
        ]


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
        default=0.0,
        verbose_name="Montant 2016",
    )

    titles = models.ManyToManyField(
        'subscription.Product',
        blank=True,
        verbose_name="Titres",
    )

    hide_in_renewal_items = models.BooleanField(
        default=False,
        verbose_name=_("Ne pas afficher dans la liste d'items des avis"),
    )

    def is_basket(self):
        return self.titles.count() > 0

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = _("Produit")
        verbose_name_plural = _("Produits")
        ordering = [
            'title',
        ]
