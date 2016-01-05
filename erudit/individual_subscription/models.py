import hashlib
from random import choice
import base64
from datetime import timedelta

from django.conf import settings
from django.utils import timezone
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.core.exceptions import ValidationError

from erudit.models import Journal


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
            self.organization_policy.date_renew = self.organization_policy.date_activation
            self.organization_policy.renew()

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


class FlatAccessMixin(object):
    """
    Mixin to generate Flat access legacy from new organisation model.
    """
    def fa_cleanup(self):
        IndividualAccountJournal.objects.filter(
            account__in=self.accounts.all()
        ).delete()

    def fa_link_journals(self, journals):
        for account in self.accounts.all():
            for journal in journals:
                rule, created = IndividualAccountJournal.objects.get_or_create(
                    account=account,
                    journal=journal)

    def fa_link_baskets(self):
        for basket in self.access_basket.all():
            self.fa_link_journals(basket.journals.all())

    def generate_flat_access(self):
        # Cleanup
        self.fa_cleanup()

        # Full access
        if self.access_full:
            journals = Journal.objects.all()
            self.fa_link_journals(journals)

        # Journals from basket access
        if self.access_basket.count() > 0:
            self.fa_link_baskets()

        # Journals selected
        if self.access_journal.count() > 0:
            self.fa_link_journals(self.access_journal.all())


class OrganizationPolicy(FlatAccessMixin, models.Model):
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
        blank=True,
        null=True,
        verbose_name=_("Date d'activation"),
        help_text=_("Ce champs se remplit automatiquement. Il est éditable uniquement pour les données existantes qui n'ont pas cette information")
    )
    date_renew = models.DateTimeField(
        null=True,
        verbose_name=_("Date de renouvellement")
    )
    renew_cycle = models.PositiveSmallIntegerField(
        verbose_name=_("Cycle du renouvellement (en jours)"),
        default=365,
    )

    organization = models.ForeignKey("erudit.Organisation", verbose_name=_("Organisation"),)

    comment = models.TextField(verbose_name=_("Commentaire"), blank=True)

    max_accounts = models.PositiveSmallIntegerField(
        verbose_name=_("Maximum de comptes"),
        blank=True,
        null=True,
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

    managers = models.ManyToManyField(
        "auth.User",
        verbose_name=_("Gestionnaires des comptes"),
        blank=True,
        related_name='organizations_managed',
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

    def renew(self):
        if self.date_activation is None:
            raise ValidationError(_("Il n'y a pas de date d'activiation de spécifiée"))
        if self.date_renew is None:
            self.date_renew = self.date_activation
        self.date_renew = self.date_renew + timedelta(days=self.renew_cycle)
        self.save()


class IndividualAccountJournal(models.Model):
    """
    Class association to define who can access the journal
    This class is used to make the glue with erudit.org system auth perms.
    """
    # TODO define where to target this models (router.py will make the trick to popule
    # in the right database)
    journal = models.ForeignKey("erudit.journal", verbose_name=_("Revue"),)
    account = models.ForeignKey("IndividualAccount", verbose_name=_("Compte personnel"),)

    class Meta:
        unique_together = (('journal', 'account'),)
