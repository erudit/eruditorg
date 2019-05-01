import copy
import datetime as dt
import dateutil.relativedelta as dr
from hashlib import md5
from functools import wraps
import structlog
import re

from lxml import etree as et

from django.core.cache import caches
from django.conf import settings
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.urls import reverse
from django.db import models
from django.db.models import Q, Case, When
from django.utils.functional import cached_property
from django.utils.translation import get_language
from django.utils.translation import gettext_lazy as _, pgettext
from django.utils.text import slugify
from eruditarticle.objects import EruditArticle
from eruditarticle.objects import EruditJournal
from eruditarticle.objects import EruditPublication
from eulfedora.util import RequestFailed
from PIL import Image
from requests.exceptions import ConnectionError
from urllib.parse import urlparse

from ..abstract_models import FedoraDated
from ..conf import settings as erudit_settings
from ..fedora.modelmixins import FedoraMixin
from ..fedora.objects import ArticleDigitalObject
from ..fedora.objects import JournalDigitalObject
from ..fedora.objects import PublicationDigitalObject
from ..fedora.cache import get_cached_datastream_content
from ..fedora.cache import cache_fedora_result
from ..fedora.utils import localidentifier_from_pid


from ..managers import InternalIssueManager
from ..managers import InternalJournalManager
from ..managers import LegacyJournalManager
from ..managers import UpcomingJournalManager
from ..managers import ManagedJournalManager
from ..utils import get_sort_key_func, strip_stopwords_prefix, catch_and_log

from .core import Collection, Publisher, Language

cache = caches['fedora']
logger = structlog.get_logger(__name__)


class JournalType(models.Model):
    """ The type of a Journal instance. """

    name = models.CharField(max_length=255, verbose_name=_('Nom'))

    CODE_CULTURAL, CODE_SCIENTIFIC = 'C', 'S'
    CODE_CHOICES = (
        (CODE_CULTURAL, _('Culturel')),
        (CODE_SCIENTIFIC, _('Savant')),
    )
    code = models.SlugField(verbose_name=_('Code'), max_length=2, choices=CODE_CHOICES, unique=True)

    def embargo_duration(self, unit='months'):
        embargo_duration_in_months = erudit_settings.SCIENTIFIC_JOURNAL_EMBARGO_IN_MONTHS \
            if self.code == 'S' \
            else erudit_settings.CULTURAL_JOURNAL_EMBARGO_IN_MONTHS

        if unit == 'months':
            return embargo_duration_in_months
        if unit == 'days':
            duration = dt.date.today() - (
                dt.date.today() - dr.relativedelta(months=embargo_duration_in_months)
            )
            return duration.days

    class Meta:
        verbose_name = _('Type de revue')
        verbose_name_plural = _('Types de revue')
        ordering = ['name', ]

    def __str__(self):
        return self.name


class Journal(FedoraMixin, FedoraDated):
    """ The main Journal model.

    A journal is a collection of issues. It should be associated with a collection: Érudit, Persée,
    etc. This model supports Fedora-based journals through the use of the ``localidentifier`` field.
    Journals that are not provided by Fedora should not use this field.
    """

    collection = models.ForeignKey(Collection, on_delete=models.CASCADE)
    """ The :py:class`collection <erudit.models.core.Collection>` of which this
    ``Journal`` is part"""

    type = models.ForeignKey(
        JournalType, null=False, blank=False, verbose_name=_('Type'),
        # 2 = Scientific
        default=2, on_delete=models.CASCADE
    )
    """ The type of the journal """

    name = models.CharField(max_length=255, verbose_name=_('Nom'), help_text=_('Nom officiel'))
    """ The ``name`` of the journal """

    code = models.SlugField(
        max_length=255, unique=True, verbose_name=_('Code'),
        help_text=_('Identifiant unique (utilisé dans URL Érudit)'))
    """ The shortname of the journal """

    issn_print = models.CharField(
        max_length=255, null=True, blank=True, verbose_name=_('ISSN imprimé'))
    """ .. warning:: Not imported.

    The print ISSN of the journal """

    issn_web = models.CharField(max_length=255, null=True, blank=True, verbose_name=_('ISSN web'))
    """ .. warning:: Not imported.

    The web ISSN of the journal """

    subtitle = models.CharField(max_length=255, null=True, blank=True)
    """ .. warning:: Not imported

    The subtitle of the journal """

    localidentifier = models.CharField(
        max_length=100, unique=True, blank=True, null=True, verbose_name=_('Identifiant Fedora'))
    """ Fedora commons identifier. Used to implement the
    :py:class:`FedoraMixin <erudit.fedora.modelmixins.FedoraMixin>` model mixin. """

    publishers = models.ManyToManyField(
        Publisher, related_name='journals', blank=True, verbose_name=_('Éditeurs'))
    """ .. warning:: Not imported.

        The publishers stored in this field are only displayed on the PDF cover page.
        Everywhere else, the publishers are fetched from the ``erudit_object``.

    The publishers of the journal """

    paper = models.NullBooleanField(
        default=None, verbose_name=_('Papier'),
        help_text=_('Est publiée également en version papier?'))
    """ .. warning:: Not imported.

    Defines whether this Journal is printed in paper or not """

    open_access = models.BooleanField(
        default=False, verbose_name=_('Libre accès'),
        help_text=_("Cette revue est en accès libre?"))
    """ Defines whether the journal can be accessed by anyone """

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
    """ Redirects to the external URL of the Journal """

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

    is_new = models.BooleanField(
        default=False,
        verbose_name=_("Est une nouveauté"),
        help_text=_("Cocher si cette revue est nouvelle sur la plateforme d'Érudit.")
    )

    disciplines = models.ManyToManyField('Discipline', related_name='journals')
    """ The disciplines associated with the journal. """

    next_journal = models.ForeignKey(
        'Journal', verbose_name=_('Revue suivante'), blank=True, null=True, related_name='+',
        on_delete=models.CASCADE
    )
    """ The journal that follows the current journal if any. """

    previous_journal = models.ForeignKey(
        'Journal', verbose_name=_('Revue précédente'), blank=True, null=True, related_name='+',
        on_delete=models.CASCADE
    )
    """ The journal that precedes the current journal if any. """

    objects = models.Manager()
    internal_objects = InternalJournalManager()
    legacy_objects = LegacyJournalManager()
    upcoming_objects = UpcomingJournalManager()
    managed_objects = ManagedJournalManager()

    class Meta:
        verbose_name = _('Revue')
        verbose_name_plural = _('Revues')
        ordering = ['name']

    def __str__(self):
        return '{:s} [{:s}]'.format(self.name, self.code)

    def get_full_identifier(self):
        if not self.localidentifier or not self.collection.localidentifier:
            return None

        return "{}:{}.{}".format(
            erudit_settings.FEDORA_PIDSPACE,
            self.collection.localidentifier,
            self.localidentifier
        )

    def get_fedora_model(self):
        return JournalDigitalObject

    def get_erudit_class(self):
        return EruditJournal

    @cache_fedora_result
    @catch_and_log
    def get_titles(self):
        last_issue = self.last_issue
        if not self.is_in_fedora or not last_issue:
            titles = {'main': self.name}
        else:

            titles = last_issue.erudit_object.get_journal_title()
        return titles

    # Journal-related methods and properties
    # --

    @property
    def letter_prefix(self):
        """ Returns its name first letter """
        return slugify(strip_stopwords_prefix(self.name))[:1].upper()

    @property
    def sortable_name(self):
        """ Returns its name without some characters in order to ease sort operations.

        This value should not be used to display the name of the Journal instance!
        """
        return get_sort_key_func()(self.name)

    @property
    def publication_period(self):
        """ Returns the publication period of the journal. """
        if self.first_publication_year and self.last_publication_year:
            return '{first} - {last}'.format(
                first=self.first_publication_year, last=self.last_publication_year)

    @property
    def embargo_in_months(self):
        return self.type.embargo_duration() if self.type else \
            erudit_settings.DEFAULT_JOURNAL_EMBARGO_IN_MONTHS

    @property
    def date_embargo_begins(self):
        """Return the embargo begining date if apply """
        if self.open_access or not self.active or not self.collection.is_main_collection:
            return None
        else:
            return dt.date.today() - dr.relativedelta(months=self.embargo_in_months)

    @property
    def days_not_available_from_today(self):
        return (dt.date.today() - self.date_embargo_begins).days if self.date_embargo_begins \
            else None

    @property
    def legacy_code(self):
        """ Returns the code used to identify the journal in our "legacy" systems.
        """
        if self.code == 'cd1':
            return 'cd'
        elif self.is_scientific():
            return self.code
        elif self.is_cultural():
            return self.localidentifier

    @property
    def solr_code(self):
        result = self.legacy_code
        if result == 'cd1':  # exception: Cahier de droit's ID in solr is "cd", not "cd1"
            result = 'cd'
        return result

    # Issues-related methods and properties
    # --

    # PERFORMANCE WARNING: this query is somewhat expensive, call responsibly. We can't cache this
    # property because the result is a queryset, not actual results.
    @property
    @catch_and_log
    def published_issues(self):
        """ Return the published issues of this Journal. """
        qs = self.issues.filter(is_published=True)
        if self.is_in_fedora:
            # Properly ordering issues is not our job. It's the responsibility of the creator of
            # the fedora object. Subtle things can affect ordering and we need to dumbly use this
            # order.
            pids = self.erudit_object.get_published_issues_pids()
            localidentifiers = [localidentifier_from_pid(pid) for pid in pids]
            # https://stackoverflow.com/a/37648265
            whens = [When(localidentifier=lid, then=i) for i, lid in enumerate(localidentifiers)]
            # Those When() below are for situations where there's fedora issues mixed with
            # non-fedora issues. We want non-fedora issues to come first because it's likely
            # a special case for RECMA (see eruditorg#1651). It's not supposed to happen
            # otherwise
            whens.append(When(localidentifier__isnull=True, then=-1))
            whens.append(When(localidentifier='', then=-1))
            qs = qs.order_by(Case(*whens, default=9999), '-date_published')
        return qs

    @property
    def published_open_access_issues(self):
        """ Return the published open access issues of this Journal. """
        if self.date_embargo_begins:
            return self.published_issues.filter(
                Q(date_published__lt=self.date_embargo_begins) | Q(force_free_access=True)
            ).order_by('date_published')
        else:
            return self.published_issues.order_by('date_published')

    @cached_property
    def first_issue(self):
        if self.is_in_fedora:
            pids = self.erudit_object.get_published_issues_pids()
            if pids:
                return Issue.from_fedora_pid(pids[-1])
            else:
                return None
        else:
            return self.published_issues.order_by('date_published').first()

    # We cache this because published_issues is expensive and this is called often when generating
    # the journal detail view.
    @cached_property
    def last_issue(self):
        if self.is_in_fedora:
            journal_pid = self.pid
            pids = self.erudit_object.get_published_issues_pids()
            # Fedora holds pids for all issues of the journal even when it has been renamed. When
            # we query for last_issue for a renamed journal, we want it to return the last_issue
            # of the journal *before* the rename, hence, the pid prefix filter below.
            pids = [pid for pid in pids if pid.startswith(journal_pid)]
            if pids:
                return Issue.from_fedora_pid(pids[0])
            else:
                return None
        else:
            return self.published_issues.order_by('-date_published').first()

    def is_scientific(self):
        """ Helper method that returns True if this journal is a scientific journal """
        return self.type.code == JournalType.CODE_SCIENTIFIC

    def is_cultural(self):
        """ Helper method that returns True if this journal is a scientific journal """
        return self.type.code == JournalType.CODE_CULTURAL


class Issue(FedoraMixin, FedoraDated):
    """ An issue of a journal. """

    journal = models.ForeignKey(Journal, related_name='issues', verbose_name=_('Revue'),
                                on_delete=models.CASCADE)
    """ The :py:class`journal <erudit.models.core.Journal>` of which this ``Issue`` is part """

    _title = models.CharField(max_length=255, null=True, blank=True)
    """ .. note::

        Will be removed in favor of a property that queries Fedora once we confirm that
        no calls to the database are needed.

    The title of the issue"""

    @property
    def title(self):
        if self.is_in_fedora:
            return self.erudit_object.theme
        logger.warn("Issue not in Fedora", localidentifier=self.localidentifier)
        return self._title

    @title.setter
    def title(self, value):
        self._title = value

    _html_title = models.CharField(max_length=400, null=True, blank=True)
    """ .. note::

        Will be removed in favor of a property that queries Fedora once we confirm that
        no calls to the database are needed.

    The title of the issue in HTML """

    @property
    def html_title(self):
        if self.is_in_fedora:
            return self.erudit_object.html_theme
        logger.warn("Issue not in Fedora", localidentifier=self.localidentifier)
        return self._title

    @html_title.setter
    def html_title(self, value):
        self._html_title = value

    year = models.PositiveIntegerField(verbose_name=_('Année'))
    """ The publication year of the issue """

    publication_period = models.CharField(
        max_length=255, verbose_name=_('Période de publication'), null=True, blank=True)
    """ .. deprecated:: 2.5.26

        Will be removed in next version.

    The publication period of the issue """

    volume = models.CharField(max_length=255, null=True, blank=True, verbose_name=_('Volume'))
    """ The volume of the issue """

    number = models.CharField(max_length=255, null=True, blank=True, verbose_name=_('Numéro'))
    """ The number of the issue """

    _first_page = models.CharField(
        max_length=16, null=True, blank=True, verbose_name=_('Première page'))
    """ .. deprecated:: 2.5.26

        Will be removed in next version.

    The first page of the issue """

    @property
    def first_page(self):
        if self.is_in_fedora:
            return self.erudit_object.first_page
        logger.warn("Issue not in Fedora", localidentifier=self.localidentifier)

    @first_page.setter
    def first_page(self, value):
        self._first_page = value

    # deprecated: will be removed shortly
    _last_page = models.CharField(
        max_length=16, null=True, blank=True, verbose_name=_('Dernière page'))
    """ .. deprecated:: 2.5.26

        Will be removed in next version.

    The last page of the issue """

    @property
    def last_page(self):
        if self.is_in_fedora:
            return self.erudit_object.last_page
        logger.warn("Issue not in Fedora", localidentifier=self.localidentifier)

    @last_page.setter
    def last_page(self, value):
        self._last_page = value

    date_published = models.DateField(verbose_name=_('Date de publication'))
    """ The publication date of the issue """

    external_url = models.URLField(
        null=True, blank=True,
        verbose_name=_('URL Externe'), help_text=_("URL du site où les numéros sont hébergés"))
    """ The external URL where the ``Issue`` is hosted. """

    is_published = models.BooleanField(default=False, verbose_name=_('Est publié'))
    """ Defines if an issue is published """

    def is_published_in_fedora(self):
        """ Query Fedora to get the publication status of this ``Issue``

        A ``Issue`` object is considered to be published if it's in the ``publications``
        datastream of its ``Journal``.

        .. warning:: This method is costly as it performs two lookups in Fedora to return its
          results

        :return: ``True`` if the ``Issue`` is published in Fedora
        """
        if not self.is_in_fedora:
            return False

        fedora_journal = self.journal.fedora_object
        publications_tree = et.fromstring(fedora_journal.publications.content.serialize())
        xml_issue_nodes = publications_tree.findall('.//numero')

        for issue_node in xml_issue_nodes:
            if self.localidentifier in issue_node.get('pid'):
                return True
        return False

    localidentifier = models.CharField(
        max_length=100, unique=True, blank=True, null=True, verbose_name=_('Identifiant Fedora'))
    """ The ``Fedora`` identifier of an issue """

    force_free_access = models.BooleanField(
        default=False, verbose_name=_('Contraindre en libre accès')
    )
    """ Defines if the issue has to be in open access despite everything """

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

    def __repr__(self):
        return "<Issue {} {}>".format(self.journal.code, self.pk)

    # Fedora-related methods and properties
    # --

    def get_fedora_model(self):
        return PublicationDigitalObject

    def get_erudit_class(self):
        return EruditPublication

    def get_full_identifier(self):
        if not self.localidentifier or not self.journal.get_full_identifier():
            return None

        return '{}.{}'.format(
            self.journal.get_full_identifier(),
            self.localidentifier
        )

    @staticmethod
    def from_fedora_ids(journal_code, localidentifier):
        """ Returns an Issue from the DB if it exists or an ephemeral if it doesn't

        If the ID doesn't exist either in the DB or in Fedora, raise DoesNotExist.
        """
        if not localidentifier:
            raise Issue.DoesNotExist()
        try:
            return Issue.objects.get(localidentifier=localidentifier)
        except Issue.DoesNotExist:
            try:
                journal = Journal.legacy_objects.get_by_id(journal_code)
            except Journal.DoesNotExist:
                raise Issue.DoesNotExist()
            else:
                issue = Issue()
                issue.journal = journal
                issue.localidentifier = localidentifier
                if issue.is_in_fedora:
                    issue.sync_with_erudit_object()
                    return issue
                else:
                    raise Issue.DoesNotExist()

    @staticmethod
    def from_fedora_pid(pid):
        _, journalid, issueid = pid.split('.')
        return Issue.from_fedora_ids(journalid, issueid)

    def sync_with_erudit_object(self, erudit_object=None):
        """ Copy ``erudit_object``'s values in appropriate fields in ``self``.

        :param erudit_object: A ``EruditPublication``.
        """
        if erudit_object is None:
            erudit_object = self.erudit_object

        # TODO: this "or" below was hotfixed without test because the proper
        # tools to test this (domchange at the publication level) are in the
        # de-article branch. Test null publication_year properly after merge.
        self.year = erudit_object.publication_year or dt.date.today().year
        self.publication_period = erudit_object.publication_period
        self.volume = erudit_object.volume
        self.number = erudit_object.number
        self.first_page = erudit_object.first_page
        self.last_page = erudit_object.last_page
        self.title = erudit_object.theme
        self.html_title = erudit_object.html_theme
        pubdate = erudit_object.publication_date
        if pubdate:
            self.date_published = dt.datetime.strptime(pubdate, '%Y-%m-%d').date()
        else:
            self.date_published = dt.datetime(int(self.year), 1, 1)
        self.date_produced = erudit_object.production_date \
            or erudit_object.publication_date
        try:
            first_article = next(self.get_articles_from_fedora())
        except StopIteration:
            pass
        else:
            if first_article.erudit_object.is_of_type_roc:
                self.force_free_access = True

    def get_articles_from_fedora(self):
        # this is a bit of copy/paste from import_journals_from_fedora but I couldn't find an
        # elegant way to generalize that code. This mechanism will probably change soon anyway.

        content = get_cached_datastream_content(self.fedora_object, 'summary')
        summary_tree = content.node
        xml_article_nodes = summary_tree.findall('.//article')
        for article_node in xml_article_nodes:
            try:
                yield Article.from_issue_and_localidentifier(self, article_node.get('idproprio'))
            except Article.DoesNotExist:
                pass

    @cached_property
    def has_coverpage(self):
        """ Returns a boolean indicating if the considered issue has a coverpage. """
        if self.fedora_object is None:
            return False
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

    @property
    def prepublication_ticket(self):
        return md5(self.localidentifier.encode('utf-8')).hexdigest()

    def is_prepublication_ticket_valid(self, request_ticket):
        """ Returns True if the issue's prepulication ticket is valid, False otherwise.

        In Tournesol, if the prepublication ticket begins with a '0', it gets stripped before it
        gets stored in the database. While we wait for this bug to get fixed in Tournesol, we should
        support tickets with a stripped leading '0'.

        See https://gitlab.erudit.org/erudit/production/tournesol/Tournesol/issues/35 """
        if request_ticket is None:
            return False
        regex = re.compile('^0?(.*)$')
        issue_ticket = re.match(regex, self.prepublication_ticket)
        request_ticket = re.match(regex, request_ticket)
        return issue_ticket.group(1) == request_ticket.group(1)

    # Issue-related methods and properties
    # --

    @cached_property
    def is_external(self):
        """
        Returns ``True`` if the issue is external. An issue is considered to be external if one
        of the two following conditions are met:

        1. The issue has an external URL
        2. The first publication allowed article has an absolute URL for its PDF or HTML

        :returns: ``True`` if the issue is external"""
        if bool(self.external_url):
            return True
        try:
            first_article = next(
                article for article in self.get_articles_from_fedora()
                if article.publication_allowed
            )
        except StopIteration:
            pass
        else:
            summary_node = first_article.get_summary_node()
            if summary_node is not None:
                urlpdf = summary_node.find('urlpdf')
                urlhtml = summary_node.find('urlhtml')
                external_pdf = urlpdf is not None and urlpdf.text \
                    and bool(urlparse(urlpdf.text).netloc)
                external_html = urlhtml is not None and urlhtml.text \
                    and bool(urlparse(urlhtml.text).netloc)
                return external_pdf or external_html
            else:
                logger.warn("Article not in issue summary", localidentifier=self.localidentifier)
        return False

    @property
    @catch_and_log
    def number_for_display(self):
        if self.number:
            return self.number
        if self.is_in_fedora:
            publication_type = self.erudit_object.get_publication_type()
            if publication_type == 'hs':
                return _('hors-série')
            if publication_type == 'index':
                return _('index')
            if publication_type == 'supp':
                return _('suppl.')
        return None

    @cached_property
    @catch_and_log
    def abbreviated_volume_title(self):
        """ For more information please refer to :meth:`~.volume_title`

        :returns: the abbreviated volume numbering information
        """
        if self.is_in_fedora:
            return self.erudit_object.get_volume_numbering(
                abbreviated=True,
                formatted=True
            )

        logger.warn("Issue not in fedora", localidentifier=self.localidentifier)

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

    @cached_property
    @catch_and_log
    def volume_title(self):
        """ Returns a title for the current issue using its volume and its number.

        If the object is present in Fedora commons, do not perform any formatting
        and let ``liberuditarticle`` format the volume_title. Otherwise, use the
        information at hand and format the volume numbering information of the issue.
        """

        if self.is_in_fedora:
            return self.erudit_object.get_volume_numbering(formatted=True)

        logger.warn("Issue not in fedora", localidentifier=self.localidentifier)

        publication_period = self.publication_period if self.publication_period else self.year

        number = self.number_for_display
        if self.volume and number:
            return _(
                'Volume {volume}, numéro {number}, {publication_date}'.format(
                    volume=self.volume, number=number, publication_date=publication_period))
        elif self.volume and not number:
            return _(
                'Volume {volume}, {publication_date}'.format(
                    volume=self.volume, publication_date=publication_period
                )
            )
        return _(
            'Numéro {number}, {publication_date}'.format(
                number=number, publication_date=publication_period))

    @property
    def volume_title_with_pages(self):
        """ Returns a title for the current issue using its volume, its number and its pages. """
        if self.is_in_fedora:
            first_page = self.erudit_object.first_page
            last_page = self.erudit_object.last_page
        else:
            logger.warn("Issue not in fedora", localidentifier=self.localidentifier)
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
        """ Returns a boolean indicating if the issue is embargoed. """

        if not self.is_published:
            # Technically, we're not "embargoed", we're not published at all! If we're asking
            # whether an unpublished issue is embargoed, something wen't wrong. Let's go with the
            # safe answer here: embargo the issue.
            return True
        if self.force_free_access:
            return False
        journal = self.journal
        threshold = journal.date_embargo_begins
        if threshold is None:
            # the journal doesn't embargo its issues
            return False
        elif self.date_published < threshold:
            # we should normally be out of embargo, *but*, we have an exception for the last issue
            # of a journal. A journal that is not in open access always has its last issue
            # embargoed.
            # On top of this, another exception: we don't apply the exception if the journal has
            # a "next_journal" because that means that the journal hasn't stopped publishing, it
            # merely changed its name. We don't want the last issue of the old journal to be stuck
            # in embargo forever.
            if journal.next_journal is None and self == journal.last_issue:
                return True
            else:
                return False
        else:
            return True

    @property
    @catch_and_log
    def name_with_themes(self):
        if not self.is_in_fedora:
            return None

        def _format_theme(theme):
            if theme.get('html_subname'):
                return "{html_name}: {html_subname}".format(
                    html_name=theme['html_name'],
                    html_subname=theme['html_subname']
                )
            return theme['html_name']

        themes = list(self.erudit_object.themes.values())
        if len(themes) > 1:
            first_theme = themes.pop(0)
            return "{first_theme} / {themes}".format(
                first_theme=_format_theme(first_theme),
                themes=",".join(_format_theme(theme) for theme in themes)
            )
        if len(themes) == 1:
            return _format_theme(themes.pop())
        return self.title

    @property
    @catch_and_log
    def copyrights(self):
        return self.erudit_object.get_copyrights(get_language(), html=True)

    @property
    @catch_and_log
    def licenses(self):
        return self.erudit_object.get_droitsauteur(links_only=True)

    def _should_use_cache(self):
        if self.is_published:
            return True
        return False


def fedora_only(method):

    @wraps(method)
    def wrapper(self, *args, **kwargs):
        if not self.is_in_fedora:
            return None
        return method(self, *args, **kwargs)

    return wrapper


# This is a read-only Hybrid Article proxy. It is instantiated through a localidentifier and proxies
# information from either fedora, solr or both.
#
# Whenever we ask for an information about an article, we check if fedora (erudit_object) is loaded.
# If it's not, we check if our solr_object has the information we need. If erudit_object is loaded,
# we always fetch from it first and fall back to solr_object if erudit_object doesn't have what we
# need.
#
# The goal here is to open the door to relying on solr more and more and avoiding fedora XML
# loading. But as of now, In most cases, your Article is already going to come with a fedora object
# pre-loaded. The only case where Article isn't initialized with fedora pre-loaded is
# "from_solr_object()". But this is used in search results and search results use some fedora-only
# attributes. So we pretty much always load fedora.
#
# But slowly, we'll get there.

class Article(FedoraMixin):
    class DoesNotExist(ObjectDoesNotExist):
        pass

    ARTICLE_DEFAULT, ARTICLE_REPORT, ARTICLE_OTHER, ARTICLE_NOTE = (
        'article', 'compterendu', 'autre', 'note'
    )
    TYPE_DISPLAY = {
        ARTICLE_DEFAULT: _('Article'),
        ARTICLE_REPORT: _('Compte rendu'),
        ARTICLE_NOTE: pgettext("Article Note", "Note"),
        ARTICLE_OTHER: _('Autre'),
    }
    PROCESSING_FULL = 'C'
    PROCESSING_MINIMAL = 'M'

    def __init__(self, issue, localidentifier, solr_object=None):
        super().__init__()
        self.issue = issue
        self.localidentifier = localidentifier
        self._solr_object = solr_object

    def __str__(self):
        if self.title:
            return self.title
        return _('Aucun titre')

    def __repr__(self):
        return "<Article: {}>".format(self.pid)

    def __eq__(self, other):
        return self.localidentifier is not None and self.localidentifier == other.localidentifier

    def __getattr__(self, name):
        if name.startswith('_') or name in {'erudit_object', 'solr_object'}:
            # Something's wrong, avoid infinite recursion
            raise AttributeError()
        if self.fedora_is_loaded():
            # if fedora is already loaded, always check in there first.
            try:
                return getattr(self.erudit_object, name)
            except AttributeError:
                pass
        try:
            # If fedora isn't loaded or if it doesn't have out attr, check in solr.
            return getattr(self.solr_object, name)
        except AttributeError:
            # If solr doesn't have our attr, load fedora and check again
            return getattr(self.erudit_object, name)

    # Fedora-related methods and properties
    # --

    def get_fedora_model(self):
        return ArticleDigitalObject

    def get_erudit_class(self):
        return EruditArticle

    def get_full_identifier(self):
        if not self.localidentifier or not self.issue.get_full_identifier():
            return None

        return '{}.{}'.format(
            self.issue.get_full_identifier(),
            self.localidentifier
        )

    def get_summary_node(self):
        summary_tree = self.issue.fedora_object.summary.content.node
        xpath = './/article[@idproprio="{}"]'.format(self.localidentifier)
        return summary_tree.find(xpath)

    @staticmethod
    def from_issue_and_localidentifier(issue, localidentifier):
        article = Article(issue, localidentifier)
        if not article.is_in_fedora:
            raise Article.DoesNotExist()
        return article

    @staticmethod
    def from_fedora_ids(journal_code: str, issue_localidentifier: str, localidentifier: str):
        try:
            issue = Issue.from_fedora_ids(journal_code, issue_localidentifier)
        except Issue.DoesNotExist:
            raise Article.DoesNotExist()
        else:
            return Article.from_issue_and_localidentifier(issue, localidentifier)

    def _should_use_cache(self):
        if self.issue.is_published:
            return True
        return False

    # Solr-related methods and properties
    # --

    @property
    def solr_object(self):
        from ..solr.models import SolrDocument
        if self._solr_object is None:
            self._solr_object = SolrDocument.from_solr_id(self.solr_id)
        return self._solr_object

    @staticmethod
    def from_solr_object(solr_object):
        solr_data = solr_object.solr_data
        try:
            issue = Issue.from_fedora_ids(solr_data.get('RevueID'), solr_data.get('NumeroID'))
        except Issue.DoesNotExist:
            raise Article.DoesNotExist()
        article = Article(issue, solr_object.localidentifier, solr_object=solr_object)
        return article

    @property
    def solr_id(self):
        collection_code = self.issue.journal.collection.code
        if collection_code == 'erudit':
            # For the Érudit collection, we use the articleès fedora id directly
            return self.localidentifier
        elif collection_code == 'unb':
            return 'unb:{}'.format(self.localidentifier)
        elif collection_code == 'persee':
            # For Persée too, we directly use localidentifier
            return self.localidentifier
        else:
            raise ValueError("Can't search this type of article in Solr")

    # URLs
    # --

    def get_absolute_url(self):
        return self.url

    @property
    def url(self):
        """ The url of the article

        If the article is external, the url that has been indexed in Solr will be returned.
        Otherwise, the url of the article on the erudit platform will be returned.

        """
        if self.is_external:
            return self.solr_object.url
        else:
            return reverse(
                'public:journal:article_detail', args=(
                    self.issue.journal.code, self.issue.volume_slug, self.issue.localidentifier,
                    self.localidentifier)
            )

    @property
    def journal_url(self):
        journal = self.issue.journal
        if journal.external_url:
            return journal.external_url
        return reverse('public:journal:journal_detail', args=(journal.code, ))

    @property
    def issue_url(self):
        issue = self.issue
        if issue.external_url:
            return issue.external_url
        return reverse('public:journal:issue_detail', args=(
            issue.journal.code,
            issue.volume_slug,
            issue.localidentifier,
        ))

    @property
    @cache_fedora_result
    @fedora_only
    def pdf_url(self):
        if not self.publication_allowed:
            return None
        if self.issue.external_url:
            # special case. if our issue has an external_url, regardless of whether we have a
            # fedora object, we *don't* have a PDF url. See the RECMA situation at #1651
            return None
        if self.fedora_object and self.fedora_object.pdf.exists:
            return reverse('public:journal:article_raw_pdf', kwargs={
                'journal_code': self.issue.journal.code,
                'issue_slug': self.issue.volume_slug,
                'issue_localid': self.issue.localidentifier,
                'localid': self.localidentifier,
            })
        summary_node = self.get_summary_node()
        if summary_node is not None:
            urlpdf = summary_node.find('urlpdf')
            if urlpdf is not None and urlpdf.text:
                # If we have a external pdf url, then it's always the proper one to return.
                return urlpdf.text
        return None

    def cite_url(self, type):
        return reverse('public:journal:article_citation_{}'.format(type), kwargs={
            'journal_code': self.issue.journal.code,
            'issue_slug': self.issue.volume_slug,
            'issue_localid': self.issue.localidentifier,
            'localid': self.localidentifier,
        })

    def cite_enw_url(self):
        return self.cite_url('enw')

    def cite_bib_url(self):
        return self.cite_url('bib')

    def cite_ris_url(self):
        return self.cite_url('ris')

    # Proxies to erudit_object
    @property
    def authors(self):
        return self.erudit_object.get_authors()

    def get_formatted_authors(self, style=None, suffixes=True):
        return self.erudit_object.get_authors(formatted=True, style=style, suffixes=suffixes)

    def get_formatted_authors_mla(self):
        return self.get_formatted_authors(style='mla')

    def get_formatted_authors_apa(self):
        return self.get_formatted_authors(style='apa')

    def get_formatted_authors_chicago(self):
        return self.get_formatted_authors(style='chicago')

    def get_formatted_authors_without_suffixes(self):
        return self.erudit_object.get_authors(formatted=True, suffixes=False)

    @property
    @catch_and_log
    def title(self):
        if self.fedora_is_loaded():
            return self.erudit_object.get_title(formatted=True, html=False)
        else:
            return self.solr_object.title

    def can_cite(self):
        # We cannot cite articles we don't have in fedora. ref #1491
        return self.is_in_fedora

    @property
    @catch_and_log
    def html_title(self):
        return self.erudit_object.get_title(formatted=True, html=True)

    def _abstract_by_lang(self, abstracts):
        """ Returns an abstract that can be used with the current language. """
        lang = get_language()
        _abstracts = list(filter(lambda r: r['lang'] == lang, abstracts))
        _abstract_lang = _abstracts[0]['content'] if len(_abstracts) else None
        _abstract = abstracts[0]['content'] if len(abstracts) else None
        return _abstract_lang or _abstract

    @property
    @catch_and_log
    @fedora_only
    def abstracts(self):
        return self.erudit_object.abstracts

    @property
    @catch_and_log
    @fedora_only
    def abstract(self):
        """ Returns an abstract that can be used with the current language. """
        return self._abstract_by_lang(self.abstracts)

    @property
    @catch_and_log
    @fedora_only
    def html_abstracts(self):
        return self.erudit_object.get_abstracts(html=True)

    @property
    @catch_and_log
    @fedora_only
    def html_abstract(self):
        """ Returns an HTML abstract that can be used with the current language. """
        return self._abstract_by_lang(self.html_abstracts)

    @property
    @catch_and_log
    def section_title_1(self):
        section_titles = self.erudit_object.get_section_titles(level=1)
        return section_titles['main'] if section_titles else None

    @property
    @catch_and_log
    def section_title_1_paral(self):
        section_titles = self.erudit_object.get_section_titles(level=1)
        return section_titles['paral'].values() if section_titles else None

    @property
    @catch_and_log
    def section_title_2(self):
        section_titles = self.erudit_object.get_section_titles(level=2)
        return section_titles['main'] if section_titles else None

    @property
    @catch_and_log
    def section_title_2_paral(self):
        if self.is_in_fedora:
            section_titles = self.erudit_object.get_section_titles(level=2)
            return section_titles['paral'].values() if section_titles else None
        else:
            title = next(filter(lambda s: s.level == 2 and s.paral, self._section_titles), None)
            return title.title if title else []

    @property
    @catch_and_log
    def section_title_3(self):
        section_titles = self.erudit_object.get_section_titles(level=3)
        return section_titles['main'] if section_titles else None

    @property
    @catch_and_log
    def section_title_3_paral(self):
        section_titles = self.erudit_object.get_section_titles(level=3)
        return section_titles['paral'].values()

    @property
    def has_pdf(self):
        return self.fedora_object.pdf.exists()

    @property
    @catch_and_log
    @fedora_only
    def processing(self):
        processing = self.erudit_object.processing
        processing_mapping = {
            'minimal': self.PROCESSING_MINIMAL,
            '': self.PROCESSING_MINIMAL,
            'complet': self.PROCESSING_FULL,
        }
        try:
            return processing_mapping[processing]
        except KeyError:
            raise ValueError(
                'Unable to determine the processing type of the article '
                'with PID {0}'.format(self.pid))

    @property
    @catch_and_log
    def copyrights(self):
        return self.erudit_object.get_droitsauteur()

    @property
    @catch_and_log
    def keywords(self):
        if self.is_in_fedora:
            return self.erudit_object.get_keywords()
        else:
            return {}

    @property
    def keywords_display(self):
        lang = get_language()
        for keywords_lang, keywords in self.keywords.items():
            if keywords_lang == lang:
                return ','.join(keywords)

    @property
    @catch_and_log
    def html_body(self):
        return self.erudit_object.get_html_body()

    @cached_property
    @catch_and_log
    def publication_allowed(self):
        summary_node = self.get_summary_node()
        if summary_node is None:
            return None
        node = summary_node.find('accessible')
        return node is None or node.text != 'non'

    @cached_property
    @catch_and_log
    def doi(self):
        return self.erudit_object.doi

    @property
    def authors_display(self):
        return self.get_formatted_authors()

    # Convenience proxies to issue and journal
    # -
    def prepublication_ticket(self):
        return self.issue.prepublication_ticket

    @property
    def is_external(self):
        """ :returns: ``True`` if the article's parent issue is external """
        return self.issue.is_external

    @property
    def open_access(self):
        """ Returns a boolean indicating if the article is in open access. """
        return self.issue.journal.open_access

    @property
    def embargoed(self):
        return self.issue.embargoed

    @property
    def collection_display(self):
        return self.issue.journal.collection.name

    @property
    def series_display(self):
        return self.issue.journal.name

    @property
    def journal_type(self):
        return self.issue.journal.type.code

    @property
    def publication_year(self):
        return self.issue.year

    @property
    def issue_title(self):
        return self.issue.name_with_themes

    @property
    def issue_number(self):
        return self.issue.number_for_display

    @property
    def issue_volume(self):
        return self.issue.volume

    @property
    def issue_published(self):
        return self.issue.publication_period or self.issue.year

    @property
    def publisher_name(self):
        publisher = self.issue.journal.publishers.first()
        if publisher:
            return publisher.name
        else:
            return ''

    # Other
    # -
    @property
    def type(self):
        return self.article_type

    @property
    def type_display(self):
        return self.TYPE_DISPLAY.get(self.type, self.type)


class JournalInformation(models.Model):
    """ Stores the information related to a specific Journal instance. """

    journal = models.OneToOneField(
        Journal, verbose_name=_('Journal'), related_name='information', on_delete=models.CASCADE)

    # Contact
    organisation_name = models.TextField(
        verbose_name=_("Prénom et nom OU nom de l’organisation"),
        blank=True)
    email = models.EmailField(
        verbose_name=_("Adresse courriel pour demandes générales"),
        blank=True)
    subscription_email = models.EmailField(
        verbose_name=_("Adresse courriel pour abonnements individuels"),
        blank=True)
    phone = models.TextField(verbose_name=_("Numéro de téléphone"), blank=True)

    frequency = models.IntegerField(
        verbose_name=_("Fréquence de publication (numéros par année)"), blank=True, null=True
    )

    languages = models.ManyToManyField(
        verbose_name=_('Langues de publication'), blank=True, to=Language
    )

    publishing_ethics = models.TextField(
        verbose_name=_("Politique anti-plagiat ou d’éthique"), null=True, blank=True
    )
    instruction_for_authors = models.TextField(
        verbose_name=_("Instructions pour les auteurs"), null=True, blank=True
    )
    peer_review_process = models.CharField(
        choices=(
            ('SB', _('Simple aveugle')),
            ('DB', _('Double aveugle')),
            ('OR', _('Ouverte')),
        ),
        max_length=2,
        verbose_name=_("Type de processus d’évaluation par les pairs"), null=True, blank=True
    )

    facebook_url = models.URLField(verbose_name=_("Facebook"), blank=True)
    facebook_enable_feed = models.BooleanField(
        verbose_name=_("Afficher votre fil d’activités Facebook ?"),
        default=False)
    twitter_url = models.URLField(verbose_name=_("Twitter"), blank=True)
    twitter_enable_feed = models.BooleanField(
        verbose_name=_("Afficher votre fil d’activités Twitter ?"),
        default=False)
    website_url = models.URLField(verbose_name=_("Site Web officiel"), blank=True)

    # Information fields
    about = models.TextField(verbose_name=_('Revue'), blank=True, null=True)
    editorial_policy = models.TextField(
        verbose_name=_('Politiques de la revue'), blank=True, null=True)
    editorial_leaders = models.ManyToManyField(
        to="Contributor"
    )
    subscriptions = models.TextField(verbose_name=_('Abonnements'), blank=True, null=True)
    team = models.TextField(verbose_name=_('Équipe'), blank=True, null=True)
    contact = models.TextField(verbose_name=_('Coordonnées'), blank=True, null=True)
    partners = models.TextField(verbose_name=_('Partenaires'), blank=True, null=True)

    def get_directors(self):
        return self.contributor_set.all().filter(type='D')

    def get_editors(self):
        return self.contributor_set.all().filter(type='R')

    class Meta:
        verbose_name = _('Information de revue')
        verbose_name_plural = _('Informations de revue')

    def __str__(self):
        return self.journal.name


class Contributor(models.Model):

    type = models.CharField(
        max_length=1, verbose_name=_("Type"),
        choices=(
            ('D', _("Direction")),
            ('R', _("Rédaction"))
        )
    )
    name = models.CharField(max_length=200, verbose_name=_("Prénom et nom"))
    journal_information = models.ForeignKey(JournalInformation, on_delete=models.CASCADE)
    role = models.CharField(max_length=200, verbose_name=_("Rôle"), null=True, blank=True)
