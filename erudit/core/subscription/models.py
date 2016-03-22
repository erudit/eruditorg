# -*- coding: utf-*-

import ipaddress
from functools import reduce

from django.conf import settings
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.core.exceptions import ValidationError

from erudit.models import Collection
from erudit.models import Journal
from erudit.models import Organisation

from .abstract_models import AbstractSubscription


class JournalAccessSubscription(AbstractSubscription):
    """ Defines a subscription allowing a user or an organisation to access journals.

    The subscription can associate many Journal instances to the user or the organisation.
    A subscription for collection of journals or a "full access" subscription can also be specified.
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, verbose_name=_('Utilisateur'), blank=True, null=True)
    organisation = models.ForeignKey(
        Organisation, verbose_name=_('Organisation'), blank=True, null=True)

    # Which Journal instances can be accessed using this subscription?
    journal = models.ForeignKey(
        Journal, verbose_name=_('Revue'), blank=True, null=True, related_name='+')
    collection = models.ForeignKey(
        Collection, verbose_name=_('Collection'), blank=True, null=True, related_name='+')
    journals = models.ManyToManyField(Journal, verbose_name=_('Revues'), related_name='+')
    full_access = models.BooleanField(default=False, verbose_name=_('Accès complet'))

    class Meta:
        verbose_name = _('Abonnement aux revues')
        verbose_name_plural = _('Abonnements aux revues')


class InstitutionIPAddressRange(models.Model):
    subscription = models.ForeignKey(
        JournalAccessSubscription, verbose_name=_('Abonnement aux revues'))
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


class JournalManagementSubscription(AbstractSubscription):
    """ Defines a subscription allowing the members of a journal to manage its subscriptions. """
    journal = models.ForeignKey(Journal, verbose_name=_('Revue'))
    plan = models.ForeignKey('JournalManagementPlan', verbose_name=_('Forfait'))

    class Meta:
        verbose_name = _('Abonnement de gestion de revue')
        verbose_name_plural = _('Abonnements de gestion de revue')


class JournalManagementPlan(models.Model):
    """ Defines the limits of the possibilities provided by a journal management subscription. """
    title = models.CharField(max_length=255, verbose_name=_('Titre'), blank=True, null=True)
    code = models.SlugField(max_length=100, unique=True, verbose_name=_('Code'))
    max_accounts = models.PositiveSmallIntegerField(verbose_name=_('Maximum de comptes'))

    class Meta:
        verbose_name = _("Forfait de gestion d'une revue")
        verbose_name_plural = _("Forfaits de gestion de revues")
