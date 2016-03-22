# -*- coding: utf-*-

import ipaddress
from functools import reduce

from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.core.exceptions import ValidationError

from erudit.models import Organisation


class InstitutionalAccount(models.Model):
    """
    An institutional account defines how an institution can access
    protected content.
    """
    institution = models.ForeignKey(Organisation, verbose_name=_('Organisation'))

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
