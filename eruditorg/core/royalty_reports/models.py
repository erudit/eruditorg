# -*- coding: utf-8 -*-

from django.db import models
from django.utils.translation import ugettext_lazy as _
from erudit.models import Journal


class RoyaltyReport(models.Model):
    """ A royalty report. """
    start = models.DateField(verbose_name=_('Date de début'))
    end = models.DateField(verbose_name=_('Date de fin'))
    report_file = models.FileField(verbose_name=_('Fichier'), upload_to='royalty_reports/')

    class Meta:
        verbose_name = _('Rapport de redevances')
        verbose_name_plural = _('Rapports de redevances')

    def __str__(self):
        return '{start} - {end}'.format(start=self.start, end=self.end)


class JournalRoyalty(models.Model):
    """ A journal royalty. """
    royalty_report = models.ForeignKey(RoyaltyReport, verbose_name=_('Rapport de redevances'))
    journal = models.ForeignKey(Journal, verbose_name=_('Revue'))
    report_file = models.FileField(verbose_name=_('Fichier'), upload_to='royalty_reports/')
    published = models.BooleanField(
        verbose_name=_("Publié dans l'espace utilisateur"), default=False)

    class Meta:
        verbose_name = _('Redevance de revue')
        verbose_name_plural = _('Redevances de revues')
