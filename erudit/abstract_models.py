# -*- coding: utf-8 -*-

from django.db import models
from django.utils.text import slugify
from django.utils.translation import ugettext_lazy as _


class FedoraDated(models.Model):
    """ Provides a creation date and an update date for Fedora-related models.

    Note that these fields do not used the auto_now_add/auto_now attributes. So these values should
    be set manually.
    """
    fedora_created = models.DateTimeField(
        verbose_name=_('Date de création sur Fedora'), blank=True, null=True)

    fedora_updated = models.DateTimeField(
        verbose_name=_('Date de modification sur Fedora'), blank=True, null=True)

    class Meta:
        abstract = True


class OAIDated(models.Model):
    """ Provides a datestamp for OAI-related models.

    Note that these fields do not used the auto_now_add/auto_now attributes. So these values should
    be set manually.
    """
    oai_datestamp = models.DateTimeField(verbose_name=_('Datestamp OAI'), blank=True, null=True)

    class Meta:
        abstract = True


class Person(models.Model):
    """ Represents a single person. """
    lastname = models.CharField(max_length=50, null=True, blank=True, verbose_name=_('Nom'))
    firstname = models.CharField(max_length=50, null=True, blank=True, verbose_name=_('Prénom'))
    othername = models.CharField(max_length=150, null=True, blank=True, verbose_name=_('Autre nom'))
    email = models.EmailField(null=True, blank=True, verbose_name=_('Courriel'))
    organisation = models.ForeignKey(
        'Organisation', null=True, blank=True, verbose_name=_('Organisation'))

    class Meta:
        abstract = True

    def __str__(self):
        return self.full_name

    @property
    def full_name(self):
        return '{:s} {:s}'.format(self.firstname, self.lastname.upper()) \
            if self.firstname and self.lastname \
            else (self.lastname or self.othername or self.firstname)

    @property
    def letter_prefix(self):
        name = self.lastname or self.othername or self.firstname
        name = slugify(name.strip())[0].upper() if name else None
        return name[0] if name else None
