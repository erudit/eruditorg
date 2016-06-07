# -*- coding: utf-8 -*-

from django.db import models
from django.utils.translation import gettext as _

from .core import Journal


class ProductionCenter(models.Model):
    """Centre de production"""
    # TODO : data migration {UDEM, ULAVAL, UNB}

    code = models.CharField(
        max_length=255,
        verbose_name=_("Code"),
    )
    name = models.CharField(
        max_length=255,
        verbose_name=_("Nom"),
    )

    def __str__(self):
        return "{:s} [{:s}]".format(
            self.name,
            self.code,
        )

    class Meta:
        verbose_name = _("Centre de production")
        verbose_name_plural = _("Centres de production")
        ordering = ['name', ]


class ProductionType(models.Model):
    """Type de production"""
    # TODO : data migration {MIN, COMP}

    code = models.CharField(
        max_length=255,
        verbose_name=_("Code"),
    )
    name = models.CharField(
        max_length=255,
        verbose_name=_("Nom"),
    )

    def __str__(self):
        return "{:s} [{:s}]".format(
            self.name,
            self.code,
        )

    class Meta:
        verbose_name = _("Type de production")
        verbose_name_plural = _("Types de production")
        ordering = ['name', ]


class JournalProduction(models.Model):
    """Info on the production of a journal"""

    journal = models.ForeignKey(
        Journal,
        related_name='production',
        verbose_name=_("Revue"),
    )
    production_center = models.ForeignKey(
        'ProductionCenter',
        null=True, blank=True,
        verbose_name=_("Centre de production"),
        help_text=_("""Centre de production responsable
            de la production de la revue."""),
    )
    production_type = models.ForeignKey(
        'ProductionType',
        null=True, blank=True,
        verbose_name=_("Type de production"),
    )

    def __str__(self):
        return "{:s} : {:s}".format(
            self.journal.code,
            self.production_center.code,
        )

    class Meta:
        verbose_name = _("Production de revue")
        verbose_name_plural = _("Productions de revue")
        ordering = ['journal', ]
