# -*- coding: utf-8 -*-

from django.db import models
from django.utils.translation import ugettext_lazy as _

from erudit.models import Journal


class JournalInformation(models.Model):
    journal = models.OneToOneField(Journal, verbose_name=_('Journal'))

    # Information fields
    about = models.TextField(verbose_name=_('Revue'))
    editorial_policy = models.TextField(
        verbose_name=_('Politique éditoriale'), blank=True, null=True)
    subscriptions = models.TextField(verbose_name=_('Abonnements'), blank=True, null=True)
    team = models.TextField(verbose_name=_('Équipe'), blank=True, null=True)
    contact = models.TextField(verbose_name=_('Contact'), blank=True, null=True)
    partners = models.TextField(verbose_name=_('Partenaires'), blank=True, null=True)

    class Meta:
        verbose_name = _('Information de revue')
        verbose_name_plural = _('Informations de revue')

    def __str__(self):
        return self.journal.name
