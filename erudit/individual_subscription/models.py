import hashlib
from random import choice
import base64

from django.conf import settings
from django.utils import timezone
from django.db import models
from django.utils.translation import ugettext_lazy as _


class IndividualAccount(models.Model):
    """
    Personal account used in erudit.org
    to access protected content.
    """
    email = models.CharField(max_length=120, verbose_name=_("Courriel"))
    password = models.CharField(max_length=50, verbose_name=_("Mot de passe"), blank=True)
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
        # Stamp first user created date
        if not self.pk and self.organization_policy.date_activation is None:
            self.organization_policy.date_activation = timezone.now()
            self.organization_policy.save()

        # Password encryption
        if self.pk:
            old_crypted_password = IndividualAccount.objects.get(pk=self.pk).password
            if not (self.password == old_crypted_password):
                self.update_password(self.password)
        else:
            new_password = self.generate_password()
            self.update_password(new_password)
        super(IndividualAccount, self).save(*args, **kwargs)

    def __str__(self):
        return '{} {} ({})'.format(self.firstname, self.lastname, self.id)

    def generate_password(self):
        return ''.join([choice('abcdefghijklmnopqrstuvwxyz0123456789%*(-_=+)') for i in range(8)])

    def update_password(self, password):
        self.password = self.sha1(password)
        # TODO mail to user te new password

    def sha1(self, msg, salt=None):
        "Crypt function from legacy system"
        if salt is None:
            salt = settings.INDIVIDUAL_SUBSCRIPTION_SALT
        to_sha = msg.encode('utf-8') + salt.encode('utf-8')
        hashy = hashlib.sha1(to_sha).digest()
        return base64.b64encode(hashy + salt.encode('utf-8')).decode('utf-8')


class OrganizationPolicy(models.Model):
    """
    Entity which describe who and what resource, an organization can access.
    (Wikipedia, AEIQ, Revue).
    date activation is stamp as soon as the first account is created
    """
    date_creation = models.DateTimeField(
        editable=False,
        null=True,
        default=timezone.now,
        verbose_name=_("Date de création")
    )
    date_modification = models.DateTimeField(
        editable=False,
        null=True,
        default=timezone.now,
        verbose_name=_("Date de modification")
    )
    date_activation = models.DateTimeField(
        editable=False,
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

    @property
    def total_accounts(self):
        return self.accounts.count()

    def __str__(self):
        return '{} ({})'.format(self.organization, self.id)

    def save(self, *args, **kwargs):
        self.date_modification = timezone.now()
        super(OrganizationPolicy, self).save(*args, **kwargs)


class IndividualAccountJournal(models.Model):
    """
    Class association to define who can access the journal
    """
    journal = models.ForeignKey("erudit.journal", verbose_name=_("Revue"),)
    account = models.ForeignKey("IndividualAccount", verbose_name=_("Compte personnel"),)

    class Meta:
        unique_together = (('journal', 'account'),)
