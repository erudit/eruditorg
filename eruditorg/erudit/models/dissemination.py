from django.db import models
from django.utils.translation import gettext as _

from .core import Journal


class Indexer(models.Model):
    """Service or Organisation indexing Érudit Journal content"""
    name = models.CharField(
        max_length=255,
        verbose_name=_("Nom"),
    )

    def __str__(self):
        return "{:s}".format(
            self.name,
        )

    class Meta:
        verbose_name = _("Indexeur")
        verbose_name_plural = _("Indexeurs")
        ordering = ['name', ]


class Indexation(models.Model):
    """Indexation of an Érudit Journal content by an Indexer"""
    journal = models.ForeignKey(
        Journal,
        verbose_name=_("Revue"),
    )
    indexer = models.ForeignKey(
        'Indexer',
        verbose_name=_("Indexeur"),
    )

    def __str__(self):
        return "{:s} {:s}".format(
            self.journal.code,
            self.indexer,
        )

    class Meta:
        verbose_name = _("Indexation")
        verbose_name_plural = _("Indexations")
        ordering = ['journal', ]
