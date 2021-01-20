from django.contrib.auth.models import User
from django.db import models
from django.utils.translation import gettext as _

from ..managers.core import JournalCollectionManager
from ..modelfields import SizeConstrainedImageField


class Organisation(models.Model):
    """ A single organisation. """
    account_id = models.CharField(max_length=10, verbose_name=_('Identifiant'))

    name = models.CharField(max_length=300, verbose_name=_('Nom'))

    badge = SizeConstrainedImageField(
        verbose_name=_('Badge'), blank=True, null=True, upload_to='organisation_badges', width=140,
        height=140)

    members = models.ManyToManyField(User, related_name='organisations', verbose_name=_('Membres'))

    sushi_requester_id = models.CharField(
        max_length=10,
        verbose_name=_('Identifiant SUSHI'),
        blank=True,
        null=True
    )

    google_scholar_opt_out = models.BooleanField(
        default=False, verbose_name=_('Ne pas inclure dans les programmes de Google Scholar'))

    objects = models.Manager()

    class Meta:
        verbose_name = _('Organisation')
        verbose_name_plural = _('Organisations')
        ordering = ['name', ]

    def __str__(self):
        return self.name


class Collection(models.Model):
    """ A collection of journals or theses.

    Set of :py:class:`Journals <erudit.models.core.Journal>` for which a partner
    provides digital publishing services """

    name = models.CharField(max_length=200, verbose_name=_('Nom'))
    """ The name of the collection """

    code = models.CharField(max_length=10, unique=True, verbose_name=_('Code'))
    """ The code of the collection. It should be unique. """

    localidentifier = models.CharField(
        max_length=10,
        verbose_name=_('Identifiant Fedora'),
        help_text=_('Identifiant Fedora du fonds'),
        blank=True,
        null=True
    )
    """ The localidentifier of the collection in Fedora """

    logo = models.ImageField(verbose_name=_('Logo'), blank=True, null=True)
    """ The logo that can be associated with a specific collection. """

    is_main_collection = models.BooleanField(
        verbose_name=_('Fonds primaire'),
        help_text=_('Les fonds primaires sont hébergés en partie ou en totalité par Érudit'),
        default=False,
    )
    """ Main collections are hosted on Érudit """

    objects = models.Manager()
    journal_collections = JournalCollectionManager()

    class Meta:
        verbose_name = _('Fond')
        verbose_name_plural = _('Fonds')

    def __str__(self):
        return self.name


class Discipline(models.Model):
    """ A simple discipline. """
    name = models.CharField(max_length=255, verbose_name=_('Nom'))
    code = models.CharField(max_length=255, unique=True, verbose_name=_('Code'))

    class Meta:
        verbose_name = _('Discipline')
        verbose_name_plural = _('Disciplines')

    def __str__(self):
        return self.name


class ThesisRepository(models.Model):
    code = models.CharField(max_length=10, unique=True, verbose_name=_('Code'))
    name = models.CharField(max_length=200, verbose_name=_('Nom'))
    # Most of the time, same as "name", but not always...
    solr_name = models.CharField(
        max_length=200,
        db_index=True,
        verbose_name=_('Nom dans Solr'),
        help_text=_('Saisir la valeur du champs Editeur de Solr'),
    )
    logo = models.ImageField(verbose_name=_('Logo'), blank=True)

    class Meta:
        verbose_name = _("Dépôt institutionnel")
        verbose_name_plural = _("Dépôts institutionnels")

    def __str__(self):
        return self.code


class Language(models.Model):
    code = models.CharField(max_length=2, unique=True, verbose_name=_('Code'))
    name = models.CharField(max_length=20, unique=True, verbose_name=_('Nom'))

    def __str__(self):
        return self.name
