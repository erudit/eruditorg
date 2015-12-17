from datetime import datetime

from django.db import models
from django.utils.translation import ugettext_lazy as _


class IndividualAccount(models.Model):
    """
    Personal account used in erudit.org
    to access protected content.
    """
    email = models.CharField(max_length=120, verbose_name=_("Courriel"))
    password = models.CharField(max_length=50, verbose_name=_("Mot de passe"))
    organization_policy = models.ForeignKey(
        "OrganizationPolicy",
        verbose_name=_("Accès de l'organisation"),
        related_name="accounts"
    )
    firstname = models.CharField(max_length=30, verbose_name=_("Prénom"))
    lastname = models.CharField(max_length=30, verbose_name=_("Nom"))

    class Meta:
        verbose_name = _("Compte personnel")
        verbose_name_plural = _("Comptes personnels")

    def save(self, *args, **kwargs):
        if not self.pk and self.organization_policy.date_activation is None:
            self.organization_policy.date_activation = datetime.now()
            self.organization_policy.save()
        super(IndividualAccount, self).save(*args, **kwargs)

    def __str__(self):
        return '{} {} ({})'.format(self.firstname, self.lastname, self.id)


class OrganizationPolicy(models.Model):
    """
    Entity which describe who and what resource, an organization can access.
    (Wikipedia, AEIQ, Revue).
    date activation is stamp as soon as the first account is created
    """
    date_creation = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("Date de création")
    )
    date_modification = models.DateTimeField(
        auto_now=True,
        verbose_name=_("Date de modification")
    )
    date_activation = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name=_("Date d'activation")
    )

    organization = models.ForeignKey("erudit.Organisation", verbose_name=_("Organisation"),)

    comment = models.TextField(verbose_name=_("Commentaire"), blank=True)

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
        blank=True,
    )

    access_basket = models.ManyToManyField(
        "subscription.Basket",
        verbose_name=_("Paniers"),
        blank=True,
    )

    class Meta:
        verbose_name = _("Accès de l'organisation")
        verbose_name_plural = _("Accès des organisations")

    def __str__(self):
        return '{} ({})'.format(self.organization, self.id)

    @property
    def total_accounts(self):
        return self.accounts.count()
