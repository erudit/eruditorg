# -*- coding: utf-8 -*-

import copy
import datetime as dt
from functools import reduce

from django.conf import settings
from django.contrib.auth.models import User
from django.db import models
from django.utils.functional import cached_property
from django.utils.translation import gettext as _
from django.utils.text import slugify
from eruditarticle.objects import EruditArticle
from eruditarticle.objects import EruditJournal
from eruditarticle.objects import EruditPublication
from eulfedora.util import RequestFailed
from PIL import Image
from polymorphic.models import PolymorphicModel
from requests.exceptions import ConnectionError
from taggit.managers import TaggableManager

from ..conf import settings as erudit_settings
from ..fedora.modelmixins import FedoraMixin
from ..fedora.objects import JournalDigitalObject, ArticleDigitalObject
from ..fedora.objects import PublicationDigitalObject
from ..fedora.shortcuts import get_cached_datastream_content
from ..managers import JournalUpcomingManager
from ..modelfields import SizeConstrainedImageField


# choices

YEARS = tuple((n, n) for n in range(1900, dt.datetime.now().year + 6))


# abstracts


class FedoraDated(models.Model):
    """ Provides a creation date and an update date for Fedora-related models.

    Note that these fields do not used the auto_now_add/auto_now attributes. So these values should
    be set manually.
    """
    fedora_created = models.DateTimeField(
        verbose_name=_('Date de création sur Fedora'),
        blank=True,
        null=True
    )

    fedora_updated = models.DateTimeField(
        verbose_name=_('Date de modification sur Fedora'),
        blank=True,
        null=True
    )

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
    """Personne"""

    lastname = models.CharField(
        max_length=50,
        null=True, blank=True,
        verbose_name=_("Nom"),
    )

    firstname = models.CharField(
        max_length=50,
        null=True, blank=True,
        verbose_name=_("Prénom"),
    )

    email = models.EmailField(
        null=True, blank=True,
        verbose_name=_("Courriel"),
    )

    organisation = models.ForeignKey(
        "Organisation",
        null=True, blank=True,
        verbose_name=_("Organisation"),
    )

    def __str__(self):
        return "{:s} {:s}".format(
            self.firstname,
            self.lastname.upper(),
        )

    class Meta:
        abstract = True


# core

class Organisation(models.Model):
    """Organisation"""

    name = models.CharField(
        max_length=120,
        verbose_name=_("Nom")
    )

    street = models.CharField(
        max_length=200,
        null=True, blank=True,
        verbose_name=_("Adresse")
    )

    postal_code = models.CharField(
        max_length=50,
        null=True, blank=True,
        verbose_name=_("Code postal")
    )

    city = models.CharField(
        max_length=50,
        null=True, blank=True,
        verbose_name=_("Ville")
    )

    province = models.CharField(
        max_length=50,
        null=True, blank=True,
        verbose_name=_("Province")
    )

    country = models.CharField(
        max_length=50,
        null=True, blank=True,
        verbose_name=_("Pays")
    )

    badge = SizeConstrainedImageField(
        verbose_name=_('Badge'),
        blank=True, null=True,
        upload_to='organisation_badges',
        width=140, height=140,
    )

    members = models.ManyToManyField(
        User,
        related_name='organisations',
        verbose_name=_('Membres'),
    )

    def __str__(self):
        return "{:s}".format(
            self.name,
        )

    class Meta:
        verbose_name = _("Organisation")
        verbose_name_plural = _("Organisations")
        ordering = ['name', ]


class Library(models.Model):
    """Bibliothèque"""

    name = models.CharField(
        max_length=255,
        verbose_name=_("Nom"),
    )

    def __str__(self):
        return "{:s}".format(
            self.name,
        )

    class Meta:
        verbose_name = _("Bibliothèque")
        verbose_name_plural = _("Bibliothèques")
        ordering = ['name', ]


class Collection(models.Model):
    """ A collection of journales or theses.

    Set of :py:class:`Journals <erudit.models.core.Journal>` for which a partner
    provides digital publishing services """

    name = models.CharField(max_length=200)
    """ The name of the collection """

    code = models.CharField(max_length=10, unique=True)
    """ The code of the collection. It should be unique. """

    localidentifier = models.CharField(max_length=10, blank=True, null=True)
    """ The localidentifier of the collection. There should be a correspondence between the
    code of the collection and the ``Fonds_fac`` field in Solr. """

    logo = models.ImageField(verbose_name=_('Logo'), blank=True, null=True)
    """ The logo that can be associated with a specific collection. """

    class Meta:
        verbose_name = _('Collection')
        verbose_name_plural = _('Collections')


class Discipline(models.Model):
    """ Discipline """
    name = models.CharField(max_length=255, verbose_name=_('Nom'))
    code = models.CharField(max_length=255, unique=True, verbose_name=_('Code'))

    class Meta:
        verbose_name = _('Discipline')
        verbose_name_plural = _('Disciplines')

    def __str__(self):
        return self.name


class Journal(FedoraMixin, FedoraDated):
    """ The main Journal model.

    A journal is a collection of issues. It should be associated with a collection: Érudit, Persée,
    etc. This model supports Fedora-based journals through the use of the ``localidentifier`` field.
    Journals that are not provided by Fedora should use this field.
    """

    collection = models.ForeignKey('Collection')
    """ The :py:class`collection <erudit.models.core.Collection>` of which this
    ``Journal`` is part"""

    type = models.ForeignKey('JournalType', null=True, blank=True, verbose_name=_('Type'))
    """ The type of the journal """

    name = models.CharField(max_length=255, verbose_name=_('Nom'), help_text=_('Nom officiel'))
    """ The ``name`` of the journal """

    code = models.SlugField(
        max_length=255, unique=True, verbose_name=_('Code'),
        help_text=_('Identifiant unique (utilisé dans URL Érudit)'))
    """ The shortname of the journal """

    issn_print = models.CharField(
        max_length=255, null=True, blank=True, verbose_name=_('ISSN imprimé'))
    """ The print ISSN of the journal """

    issn_web = models.CharField(max_length=255, null=True, blank=True, verbose_name=_('ISSN web'))
    """ The web ISSN of the journal """

    subtitle = models.CharField(max_length=255, null=True, blank=True)
    """ The subtitle of the journal """

    formerly = models.ForeignKey(
        'Journal', null=True, blank=True, verbose_name=_('Anciennement'),
        help_text=_("Choisir l'ancienne instance de la revue"))
    """ The former version of the journal """

    localidentifier = models.CharField(
        max_length=50, unique=True, blank=True, null=True, verbose_name=_('Identifiant Fedora'))
    """ Fedora commons identifier. Used to implement the
    :py:class:`FedoraMixin <erudit.fedora.modelmixins.FedoraMixin>` model mixin. """

    publishers = models.ManyToManyField(
        'Publisher', related_name='journals', verbose_name=_('Éditeurs'))
    """ The publishers of the journal """

    paper = models.NullBooleanField(
        default=None, verbose_name=_('Papier'),
        help_text=_('Est publiée également en version papier?'),
    )
    """ Defines whether this Journal is printed in paper or not """

    open_access = models.NullBooleanField(
        default=None, verbose_name=_('Libre accès'), help_text=_("Cette revue est en accès libre?"))
    """ Defines whether the journal can be accessed by anyone """

    issues_per_year = models.IntegerField(
        null=True, blank=True, verbose_name=_('Numéros par année'))
    """ Defines the number of issues per year """

    url = models.URLField(null=True, blank=True, verbose_name=_('URL'))
    """ URL of the home page of the Journal """

    # Status of the journal
    active = models.BooleanField(
        default=True, verbose_name=_('Actif'),
        help_text=_("Une revue inactive n'édite plus de numéros"),
    )
    """ Whether the Journal is active or not. An inactive journal is
    a journal that still publish issues """

    # The field defines the users who can interact this object (coupled with permissions)
    members = models.ManyToManyField(User, related_name='journals', verbose_name=_('Membres'))
    """ Users that are part of this journal's organization """

    upcoming = models.BooleanField(default=False, verbose_name=_('Prochainement disponible'))
    """ Defines whether the journal will be available soon or not. """

    disciplines = models.ManyToManyField(Discipline, related_name='journals')
    """ The disciplines associated with the journal. """

    objects = models.Manager()
    upcoming_objects = JournalUpcomingManager()

    # Fedora-related methods
    # --

    @property
    def provided_by_fedora(self):
        # We assume that the journals provided by a Fedora endpoint have a localidentifier.
        return self.localidentifier is not None

    def get_full_identifier(self):
        return "{}:{}.{}".format(
            erudit_settings.FEDORA_PIDSPACE,
            self.collection.localidentifier,
            self.localidentifier
        )

    def get_fedora_model(self):
        return JournalDigitalObject

    def get_erudit_class(self):
        return EruditJournal

    # issues

    @property
    def published_issues(self):
        return self.issues.filter(date_published__lte=dt.datetime.now().date())

    @property
    def first_issue(self):
        """ Return the first published issue of this Journal """
        return self.published_issues.order_by('date_published').first()

    @property
    def last_issue(self):
        """ Return the last published Issue of this Journal """
        return self.published_issues.order_by('-date_published').first()

    @property
    def last_oa_issue(self):
        """ Return the last published Issue of this Journal that is available in open access """
        return self.published_issues.filter(open_access=True) \
            .order_by('-date_published').first()

    @property
    def letter_prefix(self):
        """ Returns its name first letter """
        sortable_name = self.sortable_name
        return slugify(sortable_name[0]).upper() if sortable_name else None

    @property
    def sortable_name(self):
        """ Returns its name without some characters in order to ease sort operations.

        This value should not be used to display the name of the Journal instance!
        """
        replacements = ('La ', 'Le ', 'L\'', '[', ']', )
        return slugify(
            reduce(lambda a, kv: a.replace(*kv), ((r, '') for r in replacements), self.name))

    # contract
    def has_active_contract(self):
        pass

    def __str__(self):
        return "{:s} [{:s}]".format(
            self.name,
            self.code,
        )

    class Meta:
        verbose_name = _("Revue")
        verbose_name_plural = _("Revues")
        ordering = ['name']


JOURNAL_TYPE_CODE_CHOICES = [
    ('C', _('Culturel')),
    ('S', _('Savant')),
]


class JournalType(models.Model):
    """ The type of the Journal """
    name = models.CharField(
        max_length=255,
        verbose_name=_('Nom'),
        blank=True, null=True,
    )

    code = models.SlugField(
        verbose_name=_('Code'),
        max_length=2,
        choices=JOURNAL_TYPE_CODE_CHOICES,
        unique=True,
    )

    def __str__(self):
        return "{:s}".format(
            self.name,
        )

    class Meta:
        verbose_name = _("Type de revue")
        verbose_name_plural = _("Types de revue")
        ordering = ['name', ]


class Issue(FedoraMixin, FedoraDated):
    """ An issue of a journal"""
    journal = models.ForeignKey('Journal', related_name='issues', verbose_name=_('Revue'))
    """ The :py:class`journal <erudit.models.core.Journal>` of which this ``Issue`` is part """

    title = models.CharField(max_length=255, null=True, blank=True)
    """ The title of the issue """

    year = models.IntegerField(choices=YEARS, null=True, blank=True, verbose_name=_('Année'))
    """ The publication year of the issue """

    volume = models.CharField(max_length=255, null=True, blank=True, verbose_name=_('Volume'))
    """ The volume of the issue """

    number = models.CharField(max_length=255, null=True, blank=True, verbose_name=_('Numéro'))
    """ The number of the issue """

    special_issue = models.BooleanField(
        default=False, verbose_name=_('Numéro spécial'),
        help_text=_("Cocher s'il s'agit d'un numéro spécial."))
    """ Indicates if the issue is a special issue """

    thematic_issue = models.BooleanField(default=False, verbose_name=_('Numéro thématique'))
    """ Indicates if the issue is a thematic issue """

    date_produced = models.DateField(null=True, blank=True, verbose_name=_('Date de production'))
    """ The production date of the issue """

    date_published = models.DateField(verbose_name=_('Date de publication'))
    """ The publication date of the issue """

    open_access = models.NullBooleanField(
        default=None, verbose_name=_('Accès libre'),
        help_text=_("Cocher si ce numéro est en accès libre"))
    """ Indicates whether the issue is in open access """

    localidentifier = models.CharField(
        max_length=50, unique=True, verbose_name=_('Identifiant Fedora'))
    """ The ``Fedora`` identifier of an issue """

    # status { in_production, published }ull=True, blank=True,

    @property
    def volume_title(self):
        """ Returns a title for the current issue using its volume and its number. """
        erudit_object = self.erudit_object
        publication_period = erudit_object.publication_period if erudit_object else self.year
        if self.volume and self.number:
            return _(
                'Volume {volume}, numéro {number}, {publication_date}'.format(
                    volume=self.volume, number=self.number, publication_date=publication_period))
        elif self.volume:
            return _(
                'Volume {volume}, {publication_date}'.format(
                    volume=self.volume, publication_date=publication_period))
        elif self.number:
            return _(
                'Numéro {number}, {publication_date}'.format(
                    number=self.number, publication_date=publication_period))
        return publication_period

    @property
    def has_movable_limitation(self):
        """ Returns a boolean indicating if the issue has a movable limitation. """
        open_access = self.open_access or (self.open_access is None and self.journal.open_access)
        if not open_access:
            publication_year = self.date_published.year
            current_year = dt.datetime.now().year
            year_offset = 4 if self.journal.type and self.journal.type.code == 'S' else 2
            return True if publication_year <= current_year <= publication_year + year_offset \
                else False
        return False

    # Fedora-related methods
    # --

    def get_fedora_model(self):
        return PublicationDigitalObject

    def get_erudit_class(self):
        return EruditPublication

    def get_full_identifier(self):
        return "{}.{}".format(
            self.journal.get_full_identifier(),
            self.localidentifier
        )

    @cached_property
    def has_coverpage(self):
        """ Returns a boolean indicating if the considered issue has a coverpage. """
        try:
            content = get_cached_datastream_content(self.fedora_object, 'coverpage')
        except (RequestFailed, ConnectionError):  # pragma: no cover
            if settings.DEBUG:
                return False
            raise

        if not content:
            return False

        # Checks the content of the image in order to detect if it contains only one single color.
        im = Image.open(copy.copy(content))
        extrema = im.convert('L').getextrema()
        empty_coverpage = (extrema == (0, 0)) or (extrema == (255, 255))
        im.close()

        return not empty_coverpage

    def __str__(self):
        if self.volume and self.number and self.year:
            return "{:s} {:s} {:s} {:s}".format(
                self.journal.code, str(self.year),
                self.volume, self.number)
        return self.journal.code

    class Meta:
        verbose_name = _("Numéro")
        verbose_name_plural = _("Numéros")
        ordering = ['journal', 'year', 'volume', 'number', ]


class EruditDocument(PolymorphicModel):

    localidentifier = models.CharField(
        max_length=50,
        unique=True,
        verbose_name=_("Identifiant Fedora"),
        db_index=True
    )
    """ The ``Fedora`` identifier of an article """

    class Meta:
        verbose_name = _("Document Érudit")
        verbose_name_plural = _("Documents Érudit")


class Article(EruditDocument, FedoraMixin, FedoraDated):
    issue = models.ForeignKey('Issue', related_name='articles', verbose_name=_('Numéro'))
    """ The issue of the article """

    authors = models.ManyToManyField('Author', verbose_name=_('Auteurs'))
    """ An article can have many authors """

    surtitle = models.CharField(max_length=600, null=True, blank=True)
    """ The surtitle of the article """

    title = models.CharField(max_length=600, null=True, blank=True)
    """ The title of the article """

    ARTICLE_DEFAULT, ARTICLE_REPORT, ARTICLE_OTHER = 'article', 'compterendu', 'autre'
    TYPE_CHOICES = (
        (ARTICLE_DEFAULT, _('Article')),
        (ARTICLE_REPORT, _('Compte-rendu')),
        (ARTICLE_OTHER, _('Autre')),
    )
    type = models.CharField(max_length=64, choices=TYPE_CHOICES, verbose_name=_('Type'))

    PROCESSING_FULL, PROCESSING_MINIMAL = 'C', 'M'
    PROCESSING_CHOICES = (
        (PROCESSING_FULL, _('Complet')),
        (PROCESSING_MINIMAL, _('Minimal')),
    )
    processing = models.CharField(max_length=1, choices=PROCESSING_CHOICES)
    """ Type of processing of the article """

    publication_allowed_by_authors = models.BooleanField(
        verbose_name=_("Publication autorisée par l'auteur"), default=True)
    """ Defines if the article can be published on the Érudit platform according to the authors """

    def get_fedora_model(self):
        return ArticleDigitalObject

    def get_erudit_class(self):
        return EruditArticle

    def get_full_identifier(self):
        return "{}.{}".format(
            self.issue.get_full_identifier(),
            self.localidentifier
        )

    @property
    def open_access(self):
        """ Returns a boolean indicating if the article is in open access. """
        return self.issue.open_access or (
            self.issue.open_access is None and self.issue.journal.open_access)

    @property
    def has_movable_limitation(self):
        return self.issue.has_movable_limitation

    class Meta:
        verbose_name = _("Article")
        verbose_name_plural = _("Articles")


class Thesis(EruditDocument, OAIDated):
    """ Represents a single thesis. """
    collection = models.ForeignKey(Collection, verbose_name=_('Collection'))
    """ The collection associated with the considered thesis. """

    author = models.ForeignKey('Author', verbose_name=_('Auteur'))
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


class Author(Person):
    suffix = models.CharField(max_length=50, verbose_name=_('Suffixe'), blank=True, null=True)

    class Meta:
        verbose_name = _('Auteur')
        verbose_name_plural = _('Auteurs')

    def __str__(self):
        if self.suffix:
            return _('{suffix} {firstname} {lastname}').format(
                suffix=self.suffix, firstname=self.firstname, lastname=self.lastname)
        return super(Author, self).__str__()

    def articles_in_journal(self, journal):
        """ Returns the articles written by the author for a given journal. """
        return self.article_set.select_related('issue') \
            .filter(issue__journal_id=journal.id)


class Publisher(models.Model):
    """Éditeur"""

    name = models.CharField(
        max_length=255,
        verbose_name=_("Nom"),
    )

    def __str__(self):
        return "{:s}".format(
            self.name,
        )

    class Meta:
        verbose_name = _("Éditeur")
        verbose_name_plural = _("Éditeurs")
        ordering = ['name', ]


class JournalInformation(models.Model):
    """
    Stores the information related to a specific Journal instance.
    """
    journal = models.OneToOneField(
        Journal, verbose_name=_('Journal'), related_name='information')

    # Information fields
    about = models.TextField(verbose_name=_('Revue'), blank=True, null=True)
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


class Currency(models.Model):
    code = models.CharField(
        max_length=255,
    )
    name = models.CharField(
        max_length=255,
        verbose_name=_("Nom")
    )

    def __str__(self):
        return "{:s}".format(
            self.code,
        )

    class Meta:
        verbose_name = _("Devise")
        verbose_name_plural = _("Devises")
        ordering = [
            'code',
        ]
