# -*- coding: utf-*-

import ipaddress
from datetime import timedelta
from functools import reduce

from django.db import models
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from django.core.exceptions import ValidationError
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType

from erudit.models import Organisation as CoreOrganisation
from erudit.models import Journal as CoreJournal


class Organisation(CoreOrganisation):
    class Meta:
        proxy = True


class Journal(CoreJournal):
    class Meta:
        proxy = True
        verbose_name = _('Revue')


class InstitutionalAccount(models.Model):
    """
    An institutional account defines how an institution can access
    protected content.
    """
    institution = models.ForeignKey(CoreOrganisation, verbose_name=_('Organisation'))
    policy = models.ForeignKey(
        'Policy', verbose_name=_('Accès'), related_name='institutional_accounts')

    class Meta:
        verbose_name = _('Compte institutionnel')
        verbose_name_plural = _('Comptes institutionnel')

    def __str__(self):
        return str(self.institution)


class InstitutionIPAddressRange(models.Model):
    institutional_account = models.ForeignKey(
        InstitutionalAccount, verbose_name=_('Compte institutionnel'))
    ip_start = models.GenericIPAddressField(verbose_name=_('Adresse IP de début'))
    ip_end = models.GenericIPAddressField(verbose_name=_('Adresse IP de fin'))

    class Meta:
        verbose_name = _('Plage d\'adresses IP d\'institution')
        verbose_name_plural = _('Plages d\'adresses IP d\'institution')

    def __str__(self):
        return '{institution} / {start} - {end}'.format(
            institution=self.institutional_account, start=self.ip_start, end=self.ip_end)

    def clean(self):
        super(InstitutionIPAddressRange, self).clean()
        start = ipaddress.ip_address(self.ip_start)
        end = ipaddress.ip_address(self.ip_end)
        if start > end:
            raise ValidationError(_(
                'L\'adresse IP de début doit être inférieure à l\'adresse IP de fin'))

    @property
    def ip_addresses(self):
        """ Returns the list of IP addresses contained in the current range. """
        start = ipaddress.ip_address(self.ip_start)
        end = ipaddress.ip_address(self.ip_end)
        return reduce(
            lambda ips, ipn: ips + list(ipn),
            ipaddress.summarize_address_range(start, end), [])


class Policy(models.Model):
    """
    Entity which describe who and what resource, an organization can access.
    (Wikipedia, AEIQ, Revue).
    date activation is stamp as soon as the first account is created
    """
    # this field store __str__ value with generic relation info which is
    # stressfully for the database
    generated_title = models.CharField(max_length=120, verbose_name=_("Titre"),
                                       blank=True,
                                       editable=False)
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
        help_text=_("Ce champs se remplit automatiquement. \
            Il est éditable uniquement pour les données existantes qui n'ont pas cette information")
    )
    date_renew = models.DateTimeField(
        null=True,
        verbose_name=_("Date de renouvellement")
    )
    renew_cycle = models.PositiveSmallIntegerField(
        verbose_name=_("Cycle du renouvellement (en jours)"),
        default=365,
    )

    content_type = models.ForeignKey(
        ContentType,
        limit_choices_to=models.Q(
            app_label='erudit', model__in=('organisation', 'journal')
        ) | models.Q(model='individualaccount'),
        verbose_name=_('Type'),
    )
    content_object = GenericForeignKey('content_type', 'object_id')
    object_id = models.PositiveIntegerField()

    comment = models.TextField(verbose_name=_("Commentaire"), blank=True)

    max_accounts = models.PositiveSmallIntegerField(
        verbose_name=_("Maximum de comptes"),
        blank=True,
        null=True,
    )

    access_full = models.BooleanField(
        default=False,
        verbose_name=_("Accès à tous les produits")
    )

    access_journal = models.ManyToManyField(
        "erudit.journal",
        verbose_name=_("Revues"),
        blank=True,
    )

    managers = models.ManyToManyField(
        "auth.User",
        verbose_name=_("Gestionnaires des comptes"),
        blank=True,
        related_name='organizations_managed',
    )

    class Meta:
        verbose_name = _("Accès aux produits")
        verbose_name_plural = _("Accès aux produits")

    @property
    def total_accounts(self):
        return self.accounts.count()

    def __str__(self):
        if not self.generated_title and self.pk:
            self.generated_title = '{} [{}#{}]'.format(
                self.content_object, self.content_type, self.id)
            self.save()
        return self.generated_title

    def save(self, *args, **kwargs):
        self.date_modification = timezone.now()
        super(Policy, self).save(*args, **kwargs)

    def renew(self):
        if self.date_activation is None:
            raise ValidationError(_("Il n'y a pas de date d'activiation de spécifiée"))
        if self.date_renew is None:
            self.date_renew = self.date_activation
        self.date_renew = self.date_renew + timedelta(days=self.renew_cycle)
        self.save()
