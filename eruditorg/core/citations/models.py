# -*- coding: utf-8 -*-

from django.conf import settings
from django.db import models
from django.utils.translation import ugettext_lazy as _

from erudit.models import EruditDocument


class SavedCitationList(models.Model):
    """ Associates a list of saved Érudit documents to a specific registered user. """
    user = models.OneToOneField(settings.AUTH_USER_MODEL, verbose_name=_('Utilisateur'))
    documents = models.ManyToManyField(EruditDocument, verbose_name=_('Documents Érudit'))

    class Meta:
        verbose_name = _('Liste de notices')
        verbose_name_plural = _('Listes de notices')
