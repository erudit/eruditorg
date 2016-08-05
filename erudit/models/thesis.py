# -*- coding: utf-8 -*-

from django.db import models
from django.utils.translation import gettext as _
from taggit.managers import TaggableManager

from ..abstract_models import OAIDated

from .core import Author
from .core import Collection
from .core import EruditDocument


class Thesis(EruditDocument, OAIDated):
    """ Represents a single thesis. """
    collection = models.ForeignKey(Collection, verbose_name=_('Collection'))
    """ The collection associated with the considered thesis. """

    author = models.ForeignKey(Author, verbose_name=_('Auteur'))
    """ The author associated with the considered thesis. """

    title = models.CharField(max_length=600, verbose_name=_('Titre'))
    """ The title of the thesis. """

    url = models.URLField(verbose_name=_('URL'))
    """ The URL of the considered thesis. """

    publication_year = models.PositiveIntegerField(verbose_name=_('Année de publication'))
    """ The publication year of the thesis. """

    description = models.TextField(verbose_name=_('Résumé'), blank=True, null=True)
    """ A thesis can have a description. """

    keywords = TaggableManager()
    """ A thesis can be associated with multiple keywords. """

    class Meta:
        verbose_name = _('Thèse')
        verbose_name_plural = _('Thèses')

    def __str__(self):
        return self.title
