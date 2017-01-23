# -*- coding: utf-8 -*-

import copy
import datetime as dt
from functools import reduce

from django.conf import settings
from django.contrib.auth.models import User
from django.db import models
from django.utils.functional import cached_property
from django.utils.translation import get_language
from django.utils.translation import gettext as _
from django.utils.text import slugify
from eruditarticle.objects import EruditArticle
from eruditarticle.objects import EruditJournal
from eruditarticle.objects import EruditPublication
from eulfedora.util import RequestFailed
from PIL import Image
from polymorphic.manager import PolymorphicManager
from requests.exceptions import ConnectionError

from ..abstract_models import FedoraDated
from ..abstract_models import OAIDated
from ..conf import settings as erudit_settings
from ..fedora.modelmixins import FedoraMixin
from ..fedora.objects import ArticleDigitalObject
from ..fedora.objects import JournalDigitalObject
from ..fedora.objects import PublicationDigitalObject
from ..fedora.shortcuts import get_cached_datastream_content
from ..managers import InternalArticleManager
from ..managers import InternalIssueManager
from ..managers import InternalJournalManager
from ..managers import LegacyJournalManager
from ..managers import UpcomingJournalManager

from .core import Collection
from .core import Copyright
from .core import EruditDocument
from .core import Publisher


class JournalType(models.Model):
    """ The type of a Journal instance. """

    name = models.CharField(max_length=255, verbose_name=_('Nom'))

    CODE_CULTURAL, CODE_SCIENTIFIC = 'C', 'S'
    CODE_CHOICES = (
        (CODE_CULTURAL, _('Culturel')),
        (CODE_SCIENTIFIC, _('Savant')),
    )
    code = models.SlugField(verbose_name=_('Code'), max_length=2, choices=CODE_CHOICES, unique=True)

    def embargo_duration(self, unit='years'):
        embargo_duration_in_years = erudit_settings.SCIENTIFIC_JOURNAL_EMBARGO_IN_YEARS \
            if self.code == 'S' \
            else erudit_settings.CULTURAL_JOURNAL_EMBARGO_IN_YEARS

        if unit == 'years':
            return embargo_duration_in_years
        if unit == 'days':
            return embargo_duration_in_years * 365

    class Meta:
        verbose_name = _('Type de revue')
        verbose_name_plural = _('Types de revue')
        ordering = ['name', ]

    def __str__(self):
        return self.name


class Journal(FedoraMixin, FedoraDated, OAIDated):
    """ The main Journal model.

    A journal is a collection of issues. It should be associated with a collection: Érudit, Persée,
    etc. This model supports Fedora-based journals through the use of the ``localidentifier`` field.
    Journals that are not provided by Fedora should not use this field.
    """

    collection = models.ForeignKey(Collection)
    """ The :py:class`collection <erudit.models.core.Collection>` of which this
    ``Journal`` is part"""

    type = models.ForeignKey(JournalType, null=True, blank=True, verbose_name=_('Type'))
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

    localidentifier = models.CharField(
        max_length=100, unique=True, blank=True, null=True, verbose_name=_('Identifiant Fedora'))
    """ Fedora commons identifier. Used to implement the
    :py:class:`FedoraMixin <erudit.fedora.modelmixins.FedoraMixin>` model mixin. """

    publishers = models.ManyToManyField(
        Publisher, related_name='journals', blank=True, verbose_name=_('Éditeurs'))
    """ The publishers of the journal """

    paper = models.NullBooleanField(
        default=None, verbose_name=_('Papier'),
        help_text=_('Est publiée également en version papier?'))
    """ Defines whether this Journal is printed in paper or not """

    open_access = models.BooleanField(
        default=False, verbose_name=_('Libre accès'),
        help_text=_("Cette revue est en accès libre?"))
    """ Defines whether the journal can be accessed by anyone """

    issues_per_year = models.IntegerField(
        null=True, blank=True, verbose_name=_('Numéros par année'))
    """ Defines the number of issues per year """

    first_publication_year = models.PositiveIntegerField(
        verbose_name=_('Première année de publication'), blank=True, null=True)
    """ The first year when an issue of this journal has been published. """

    last_publication_year = models.PositiveIntegerField(
        verbose_name=_('Dernière année de publication'), blank=True, null=True)
    """ The last year when an issue of this journal has been published. """

    external_url = models.URLField(null=True, blank=True, verbose_name=_('URL'))
    """ External URL of the home page of the Journal """

    redirect_to_external_url = models.BooleanField(
        default=False,
        verbose_name=_("Rediriger vers l'URL externe"),
        help_text=_("Cocher si les numéros de cette revue ne sont pas hébergés sur la plateforme Érudit")  # noqa
    )

    # Status of the journal
    active = models.BooleanField(
        default=True, verbose_name=_('Actif'),
        help_text=_("Une revue inactive n'édite plus de numéros"))
    """ Whether the Journal is active or not. An inactive journal is
    a journal that still publish issues """

    # The field defines the users who can interact this object (coupled with permissions)
    members = models.ManyToManyField(
        User,
        blank=True,
        related_name='journals',
        verbose_name=_('Membres')
    )
    """ Users that are part of this journal's organization """

    upcoming = models.BooleanField(default=False, verbose_name=_('Prochainement disponible'))
    """ Defines whether the journal will be available soon or not. """

    disciplines = models.ManyToManyField('Discipline', related_name='journals')
    """ The disciplines associated with the journal. """

    next_journal = models.ForeignKey(
        'Journal', verbose_name=_('Revue suivante'), blank=True, null=True, related_name='+')
    """ The journal that follows the current journal if any. """

    previous_journal = models.ForeignKey(
        'Journal', verbose_name=_('Revue précédente'), blank=True, null=True, related_name='+')
    """ The journal that precedes the current journal if any. """

    website_url = models.URLField(verbose_name=_('Site web'), blank=True, null=True)
    """ The website URL of the journal if any. """

    objects = models.Manager()
    internal_objects = InternalJournalManager()
    legacy_objects = LegacyJournalManager()
    upcoming_objects = UpcomingJournalManager()

    class Meta:
        verbose_name = _('Revue')
        verbose_name_plural = _('Revues')
        ordering = ['name']

    def __str__(self):
        return '{:s} [{:s}]'.format(self.name, self.code)

    # Fedora-related methods and properties
    # --
    @property
    def provided_by_fedora(self):
        # We assume that the journals provided by a Fedora endpoint have a localidentifier.
        if self.redirect_to_external_url:
            return False

        if self.localidentifier and self.collection.localidentifier:
            return True
        return False

    def get_full_identifier(self):
        if self.provided_by_fedora:
            return "{}:{}.{}".format(
                erudit_settings.FEDORA_PIDSPACE,
                self.collection.localidentifier,
                self.localidentifier
            )
        return None

    def get_fedora_model(self):
        return JournalDigitalObject

    def get_erudit_class(self):
        return EruditJournal

    # Journal-related methods and properties
    # --

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

    @property
    def publication_period(self):
        """ Returns the publication period of the journal. """
        if self.first_publication_year and self.last_publication_year:
            return '{first} - {last}'.format(
                first=self.first_publication_year, last=self.last_publication_year)

    @property
    def embargo_in_years(self):
        return self.type.embargo_duration() if self.type else \
            erudit_settings.DEFAULT_JOURNAL_EMBARGO_IN_YEARS

    # Issues-related methods and properties
    # --

    @property
    def published_issues(self):
        """ Return the published issues of this Journal. """
        return self.issues.filter(is_published=True)

    @property
    def published_open_access_issues(self):
        """ Return the published open access issues of this Journal. """
        current_year = dt.datetime.now().year
        filter_kwargs = {
            'year__lte': current_year if self.open_access
            else self.last_publication_year - self.embargo_in_years}
        return self.issues.filter(**filter_kwargs)

    @property
    def first_issue(self):
        """ Return the first published issue of this Journal. """
        return self.published_issues.order_by('date_published').first()

    @property
    def last_issue(self):
        """ Return the last published Issue of this Journal. """
        return self.published_issues.order_by('-date_published').first()

    @property
    def published_open_access_issues_year_coverage(self):
        """ Return the year coverage of the open access issues of this Journal. """
        open_access_issues = self.published_open_access_issues.order_by('-year')
        return None if not open_access_issues.exists() else {
            'from': open_access_issues.last().year,
            'to': open_access_issues.first().year,
        }

    def get_directors(self):
        """ The directors of a journal are the directors of the last issue """
        if self.last_issue:
            return self.last_issue.get_directors()

    def get_editors(self):
        """ The editors of a journal are the editors of the last issue """
        if self.last_issue:
            return self.last_issue.get_editors()

    def is_scientific(self):
        """ Helper method that returns True if this journal is a scientific journal """
        return self.type.code == JournalType.CODE_SCIENTIFIC

    def is_cultural(self):
        """ Helper method that returns True if this journal is a scientific journal """
        return self.type.code == JournalType.CODE_CULTURAL

    editors = cached_property(get_editors)
    directors = cached_property(get_directors)


class Issue(FedoraMixin, FedoraDated, OAIDated):
    """ An issue of a journal. """

    journal = models.ForeignKey(Journal, related_name='issues', verbose_name=_('Revue'))
    """ The :py:class`journal <erudit.models.core.Journal>` of which this ``Issue`` is part """

    title = models.CharField(max_length=255, null=True, blank=True)
    """ The title of the issue """

    html_title = models.CharField(max_length=400, null=True, blank=True)
    """ The title of the issue in HTML """

    year = models.PositiveIntegerField(verbose_name=_('Année'))
    """ The publication year of the issue """

    publication_period = models.CharField(
        max_length=255, verbose_name=_('Période de publication'), null=True, blank=True)
    """ The publication period of the issue """

    volume = models.CharField(max_length=255, null=True, blank=True, verbose_name=_('Volume'))
    """ The volume of the issue """

    number = models.CharField(max_length=255, null=True, blank=True, verbose_name=_('Numéro'))
    """ The number of the issue """

    first_page = models.CharField(
        max_length=16, null=True, blank=True, verbose_name=_('Première page'))
    """ The first page of the issue """

    last_page = models.CharField(
        max_length=16, null=True, blank=True, verbose_name=_('Dernière page'))
    """ The last page of the issue """

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

    external_url = models.URLField(
        null=True, blank=True,
        verbose_name=_('URL Externe'), help_text=_("URL du site où les numéros sont hébergés"))
    """ External URL of the issue """

    is_published = models.BooleanField(default=False, verbose_name=_('Est publié'))
    """ Defines if an issue is published """

    copyrights = models.ManyToManyField(
        Copyright, related_name=_('issues'), verbose_name=_("Droits d'auteurs"))
    """ The copyrights of the issue """

    localidentifier = models.CharField(
        max_length=100, unique=True, blank=True, null=True, verbose_name=_('Identifiant Fedora'))
    """ The ``Fedora`` identifier of an issue """

    objects = models.Manager()
    internal_objects = InternalIssueManager()

    class Meta:
        verbose_name = _('Numéro')
        verbose_name_plural = _('Numéros')
        ordering = ['journal', 'year', 'volume', 'number', ]

    def __str__(self):
        if self.volume and self.number and self.year:
            return '{:s} {:s} {:s} {:s}'.format(
                self.journal.code, str(self.year), self.volume, self.number)
        return self.journal.code

    # Fedora-related methods and properties
    # --

    def get_fedora_model(self):
        return PublicationDigitalObject

    def get_erudit_class(self):
        return EruditPublication

    def get_full_identifier(self):
        if self.journal.provided_by_fedora and self.localidentifier:
            return '{}.{}'.format(
                self.journal.get_full_identifier(),
                self.localidentifier
            )
        return None

    def get_directors(self):
        return self.contributors.filter(is_director=True)

    def get_editors(self):
        return self.contributors.filter(is_editor=True)

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

    # Issue-related methods and properties
    # --

    @property
    def number_for_display(self):
        return self.number if self.number else _('hors série')

    @property
    def abbreviated_volume_title(self):
        """ Returns an abbreviated volume title """
        publication_period = self.publication_period if self.publication_period else str(self.year)
        number = self.number
        if self.volume and number:
            return _(
                'Vol. {volume}, n<sup>o</sup> {number}, {publication_date}'.format(
                    volume=self.volume, number=number, publication_date=publication_period.lower()))
        elif self.volume and not number:
            return _(
                'Vol. {volume}, {publication_date}'.format(
                    volume=self.volume, publication_date=publication_period.lower()))

        return _(
            'N<sup>o</sup> {number}, {publication_date}'.format(
                number=number, publication_date=publication_period.lower()))

    @property
    def volume_title(self):
        """ Returns a title for the current issue using its volume and its number. """
        publication_period = self.publication_period if self.publication_period else self.year
        number = self.number_for_display
        if self.volume and number:
            return _(
                'Volume {volume}, numéro {number}, {publication_date}'.format(
                    volume=self.volume, number=number, publication_date=publication_period))
        return _(
            'Numéro {number}, {publication_date}'.format(
                number=number, publication_date=publication_period))

    @property
    def volume_title_with_pages(self):
        """ Returns a title for the current issue using its volume, its number and its pages. """
        first_page = self.first_page
        last_page = self.last_page

        if first_page and last_page and (first_page != '0' and first_page != last_page):
            return _('{title}, p. {first_page}-{last_page}').format(
                title=self.volume_title, first_page=first_page, last_page=last_page)
        elif first_page and first_page != '0':
            return _('{title}, p. {first_page}').format(
                title=self.volume_title, first_page=first_page)
        return self.volume_title

    @cached_property
    def volume_slug(self):
        """ Returns a slug string containing the issue's publication year, volume and number. """
        volume = 'v' + self.volume if self.volume else None
        number = 'n' + self.number if self.number else None
        elements = [str(self.year), volume, number]
        return '-'.join([e for e in elements if e]).replace(" ", "-")

    @property
    def embargoed(self):
        """ Returns a boolean indicating if the issue has a movable limitation. """
        # FIXME avoid hardcoding the collection code
        if not self.journal.open_access and self.journal.collection.code == 'erudit':
            publication_year = self.year
            year_offset = self.journal.embargo_in_years
            return True if self.journal.last_publication_year < publication_year + year_offset \
                else False
        return False

    @property
    def name_with_themes(self):
        def _format_theme(theme):
            if theme.html_subname:
                return "{html_name}: {html_subname}".format(
                    html_name=theme.html_name,
                    html_subname=theme.html_subname
                )
            return theme.html_name
        themes = list(self.themes.all())
        if len(themes) > 1:
            first_theme = themes.pop(0)
            return "{first_theme} / {themes}".format(
                first_theme=_format_theme(first_theme),
                themes=",".join(_format_theme(theme) for theme in themes)
            )
        if len(themes) == 1:
            return _format_theme(themes.pop())
        return self.title


class IssueContributor(models.Model):
    """ A contributor of an issue """

    issue = models.ForeignKey(Issue, related_name='contributors', verbose_name=_('Numéro'))

    firstname = models.CharField(max_length=255, verbose_name=_('Prénom du contributeur'))
    """ Firstname of the contributor """

    lastname = models.CharField(max_length=255, null=True, verbose_name=_('Nom du contributeur'))
    """ Lastname of the contributor """

    role_name = models.CharField(max_length=255, null=True, verbose_name=_('Rôle du contributeur'))
    """ Name of the role of the contributor """

    is_director = models.NullBooleanField(verbose_name=_('Est un directeur'), null=True)
    """ Determines if the person contributes as a director """

    is_editor = models.NullBooleanField(verbose_name=_('Est un rédacteur'), null=True)
    """ Determines if the person contributes as an editor """

    def format_name(self):
        formatted_name = self.firstname

        if self.lastname:
            formatted_name = "{formatted_name} {lastname}".format(
                formatted_name=formatted_name,
                lastname=self.lastname
            )

        if self.role_name:
            formatted_name = "{formatted_name} ({role_name})".format(
                formatted_name=formatted_name,
                role_name=self.role_name
            )

        return formatted_name


class IssueTheme(models.Model):
    """ A theme that is associated with an issue. """

    issue = models.ForeignKey(Issue, related_name='themes', verbose_name=_('Numéro'))
    identifier = models.SlugField(
        max_length=50, verbose_name=_('Identifiant du thème'), blank=True, null=True)
    name = models.CharField(max_length=255, verbose_name=_('Nom du thème'))
    subname = models.CharField(
        max_length=255, verbose_name=_('Sous-thème'), blank=True, null=True)
    html_name = models.CharField(
        max_length=400, verbose_name=_('Nom du thème (HTML)'), blank=True, null=True)
    html_subname = models.CharField(
        max_length=400, verbose_name=_('Sous-thème (HTML)'), blank=True, null=True)
    paral = models.BooleanField(default=False, verbose_name=_('Thème parallèle'))

    class Meta:
        verbose_name = _("Thème d'un numéro")
        verbose_name_plural = _("Thèmes de numéros")

    def __str__(self):
        return self.name


class Article(EruditDocument, FedoraMixin, FedoraDated, OAIDated):
    """ An article of an issue. """

    issue = models.ForeignKey('Issue', related_name='articles', verbose_name=_('Numéro'))
    """ The issue of the article """

    authors = models.ManyToManyField('Author', verbose_name=_('Auteurs'))
    """ An article can have many authors """

    publisher = models.ForeignKey(Publisher, verbose_name=_('Éditeur'), blank=True, null=True)
    """ The publisher of the article """

    doi = models.CharField(max_length=50, verbose_name=_('DOI'), blank=True, null=True)
    """ The DOI of the article """

    ordseq = models.PositiveIntegerField(verbose_name=_('Ordonnancement'))
    """ A value that can be used to sort articles """

    first_page = models.CharField(
        max_length=16, null=True, blank=True, verbose_name=_('Première page'))
    """ The first page of the article """

    last_page = models.CharField(
        max_length=16, null=True, blank=True, verbose_name=_('Dernière page'))
    """ The last page of the article """

    surtitle = models.CharField(max_length=600, null=True, blank=True)
    """ The surtitle of the article """

    html_title = models.CharField(max_length=800, null=True, blank=True)
    """ The title of the article (HTML) """

    language = models.CharField(max_length=10, verbose_name=_('Code langue'))
    """ The language code of the article """

    external_url = models.URLField(null=True, blank=True, verbose_name=_('URL'))
    """ External URL of the article """

    external_pdf_url = models.URLField(null=True, blank=True, verbose_name=_('URL PDF'))
    """ External URL of the PDF version of the article """

    ARTICLE_DEFAULT, ARTICLE_REPORT, ARTICLE_OTHER, ARTICLE_NOTE = (
        'article', 'compterendu', 'autre', 'note'
    )

    TYPE_CHOICES = (
        (ARTICLE_DEFAULT, _('Article')),
        (ARTICLE_REPORT, _('Compte rendu')),
        (ARTICLE_NOTE, _('Note')),
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

    copyrights = models.ManyToManyField(
        Copyright, related_name=_('articles'), verbose_name=_("Droits d'auteurs"))
    """ The copyrights of the article """

    objects = PolymorphicManager()
    internal_objects = InternalArticleManager()

    class Meta:
        verbose_name = _('Article')
        verbose_name_plural = _('Articles')

    @property
    def title(self):
        title = self.titles.filter(paral=False).first()
        return str(title) if title else None

    @cached_property
    def subtitle(self):
        title = self.subtitles.filter(paral=False).first()
        return str(title) if title else None

    def __str__(self):
        if self.title:
            return self.title
        return _('Aucun titre')

    # Fedora-related methods and properties
    # --

    def get_fedora_model(self):
        return ArticleDigitalObject

    def get_erudit_class(self):
        return EruditArticle

    def get_full_identifier(self):
        if self.issue.journal.provided_by_fedora:
            return '{}.{}'.format(
                self.issue.get_full_identifier(),
                self.localidentifier
            )
        return None

    # Article-related methods and properties
    # --

    @property
    def open_access(self):
        """ Returns a boolean indicating if the article is in open access. """
        return self.issue.journal.open_access

    @property
    def embargoed(self):
        return self.issue.embargoed

    @property
    def abstract(self):
        """ Returns an abstract that can be used with the current language. """
        abstracts = self.abstracts.values('text', 'language')
        lang = get_language()
        _abstracts = list(filter(lambda r: r['language'] == lang, abstracts))
        _abstract_lang = _abstracts[0]['text'] if len(_abstracts) else None
        _abstract = abstracts[0]['text'] if len(abstracts) else None
        return _abstract_lang or _abstract

    @property
    def section_title_1(self):
        title = next(filter(lambda s: s.level == 1 and not s.paral, self._section_titles), None)
        return title.title if title else None

    @property
    def section_title_1_paral(self):
        return [t.title for t in filter(lambda s: s.level == 1 and s.paral, self._section_titles)]

    @property
    def section_title_2(self):
        title = next(filter(lambda s: s.level == 2 and not s.paral, self._section_titles), None)
        return title.title if title else None

    @property
    def section_title_2_paral(self):
        return [t.title for t in filter(lambda s: s.level == 2 and s.paral, self._section_titles)]

    @property
    def section_title_3(self):
        title = next(filter(lambda s: s.level == 3 and not s.paral, self._section_titles), None)
        return title.title if title else None

    @property
    def section_title_3_paral(self):
        return [t.title for t in filter(lambda s: s.level == 3 and s.paral, self._section_titles)]

    @property
    def _section_titles(self):
        return list(self.section_titles.all())


class ArticleAbstract(models.Model):
    """ Represents an abstract associated with an article. """

    article = models.ForeignKey(Article, related_name='abstracts', verbose_name=_('Article'))
    text = models.TextField(verbose_name=_('Résumé'))
    language = models.CharField(max_length=10, verbose_name=_('Code langue'))

    class Meta:
        verbose_name = _("Résumé d'article")
        verbose_name_plural = _("Résumés d'articles")

    def __str__(self):
        return '{} / {}'.format(str(self.article), self.language)


class ArticleTitleMixin(models.Model):
    """ Represents the title of an article """

    title = models.CharField(max_length=600, verbose_name=_('Titre'), blank=True, null=True)
    language = models.CharField(max_length=10, blank=True, null=True, verbose_name=_('Code langue'))
    paral = models.BooleanField(default=False, verbose_name=_('Titre parallèle'))

    def __lt__(self, other):
        if isinstance(other, ArticleTitleMixin):
            return self.title < other.title
        elif isinstance(other, str):
            return self.title < other
        raise NotImplemented

    def __gt__(self, other):
        return not self < other

    def __str__(self):
        if self.title:
            return self.title
        return _('Aucun titre')

    class Meta:
        abstract = True


class ArticleTitle(ArticleTitleMixin):
    """ The title of an article """
    article = models.ForeignKey(Article, related_name='titles', verbose_name=_('Article'))

    class Meta:
        verbose_name = _("Titre d'article")
        verbose_name_plural = _("Titres d'articles")


class ArticleSubtitle(ArticleTitleMixin):
    """ The subtitle of an article """
    article = models.ForeignKey(Article, related_name='subtitles', verbose_name=_('Article'))

    class Meta:
        verbose_name = _("Sous-titre d'article")
        verbose_name_plural = _("Sous-titres d'articles")


class ArticleSectionTitle(models.Model):
    """ Represents a section title associated with an article. """

    article = models.ForeignKey(Article, related_name='section_titles', verbose_name=_('Article'))
    title = models.CharField(max_length=600, verbose_name=_('Titre'))
    level = models.PositiveIntegerField(verbose_name=_('Niveau du titre section'))
    paral = models.BooleanField(default=False, verbose_name=_('Titre parallèle'))

    class Meta:
        verbose_name = _("Titre de section d'article")
        verbose_name_plural = _("Titres de sections d'articles")

    def __str__(self):
        return self.title[:50]


class JournalInformation(models.Model):
    """ Stores the information related to a specific Journal instance. """

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
