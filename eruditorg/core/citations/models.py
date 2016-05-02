# -*- coding: utf-8 -*-

from django.conf import settings
from django.db import models
from django.utils.translation import ugettext_lazy as _

from erudit.models import Article


class SavedCitationList(models.Model):
    """ Associates a list of saved articles to a specific registered user. """
    user = models.OneToOneField(settings.AUTH_USER_MODEL, verbose_name=_('Utilisateur'))
    articles = models.ManyToManyField(Article, verbose_name=_('Articles'))

    class Meta:
        verbose_name = _('Liste de notices')
        verbose_name_plural = _('Listes de notices')
