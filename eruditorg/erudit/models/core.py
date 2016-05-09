from datetime import datetime as dt
from functools import reduce

from django.db import models
from django.contrib.auth.models import User
from django.utils import formats
from django.utils.translation import gettext as _
from django.utils.text import slugify
from django.core.urlresolvers import reverse as reverse_url
from eruditarticle.objects import EruditJournal
from eruditarticle.objects import EruditPublication, EruditArticle

from ..fedora.conf import settings as fedora_settings
from ..fedora.modelmixins import FedoraMixin
from ..fedora.objects import JournalDigitalObject, ArticleDigitalObject
from ..fedora.objects import PublicationDigitalObject
from ..managers import JournalUpcomingManager


# choices

YEARS = tuple((n, n) for n in range(1900, dt.now().year + 6))


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

    badge = models.ImageField(
        verbose_name=_('Badge'),
        blank=True, null=True,
        upload_to='organisation_badges',
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
    """ A collection of Journals

    Set of :py:class:`Journals <erudit.models.core.Journal>` for which a partner
    provides digital publishing services """

    name = models.CharField(max_length=200)
    """ The name of the collection """

    code = models.CharField(max_length=10, unique=True)
    """ The code of the collection. It should be unique. """

    localidentifier = models.CharField(max_length=10, blank=True, null=True)
    """ The localidentifier of the collection. There should be a correspondence between the
    code of the collection and the ``Fonds_fac`` field in Solr. """


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
        max_length=50, unique=True, verbose_name=_('Identifiant Fedora'))
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

    address = models.TextField(null=True, blank=True, verbose_name=_('Adresse'))
    """ Address of the journal """

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

    def get_full_identifier(self):
        return "{}:{}.{}".format(
            fedora_settings.PIDSPACE,
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
        return self.issues.filter(date_published__isnull=False)

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
        return slugify(self.sortable_name[0]).upper()

    @property
    def sortable_name(self):
        """ Returns its name without some characters in order to ease sort operations.

        This value should not be used to display the name of the Journal instance!
        """
        replacements = ('La ', 'Le ', 'L\'', '[', ']', )
        return reduce(lambda a, kv: a.replace(*kv), ((r, '') for r in replacements), self.name)

    def get_absolute_url(self):
        return reverse_url(
            "public:journal:journal-detail",
            args=[self.code]
        )

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

    # identification
    journal = models.ForeignKey(
        'Journal',
        related_name='issues',
        verbose_name=_("Revue"),
    )

    title = models.CharField(
        max_length=255,
        null=True, blank=True,
    )
    """ The title of the issue """

    year = models.IntegerField(
        choices=YEARS,
        null=True, blank=True,
        verbose_name=_("Année"),
    )
    volume = models.CharField(
        max_length=255,
        null=True, blank=True,
        verbose_name=_("Volume"),
    )
    number = models.CharField(
        max_length=255,
        null=True, blank=True,
        verbose_name=_("Numéro"),
    )
    special_issue = models.BooleanField(
        default=False,
        verbose_name=_("Numéro spécial"),
        help_text=_("Cocher s'il s'agit d'un numéro spécial."),
    )

    date_produced = models.DateField(
        null=True, blank=True,
        verbose_name=_("Date de production"),
    )
    date_published = models.DateField(
        null=True, blank=True,
        verbose_name=_("Date de publication"),
    )

    open_access = models.NullBooleanField(
        default=None,
        verbose_name=_("Accès libre"),
        help_text=_("Cocher si ce numéro est en accès libre"),
    )

    localidentifier = models.CharField(
        max_length=50,
        unique=True,
        verbose_name=_("Identifiant Fedora")
    )
    """ The ``Fedora`` identifier of an issue """

    # status { in_production, published }ull=True, blank=True,

    @property
    def volume_title(self):
        """ Returns a title for the current issue using its volume and its number. """
        if self.volume and self.number and self.date_published:
            return _(
                'Volume {volume}, numéro {number}, {publication_date}'.format(
                    volume=self.volume, number=self.number,
                    publication_date=formats.date_format(self.date_published, 'YEAR_MONTH_FORMAT')))
        elif self.volume and self.date_published:
            return _(
                'Volume {volume}, {publication_date}'.format(
                    volume=self.volume,
                    publication_date=formats.date_format(self.date_published, 'YEAR_MONTH_FORMAT')))
        elif self.number and self.date_published:
            return _(
                'Numéro {number}, {publication_date}'.format(
                    number=self.number,
                    publication_date=formats.date_format(self.date_published, 'YEAR_MONTH_FORMAT')))

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

    def get_absolute_url(self):
        return reverse_url(
            "public:journal:issue-detail",
            args=[self.journal.code, self.localidentifier]
        )

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


class EruditDocument(models.Model):

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

    # An article can have many authors
    authors = models.ManyToManyField('Author', verbose_name=_('Auteurs'))

    surtitle = models.CharField(
        max_length=600,
        null=True, blank=True,
    )

    title = models.CharField(
        max_length=600,
        null=True, blank=True,
    )
    """ The title of the issue """

    processing = models.CharField(
        max_length=1,
        choices=(
            ('C', _('Complet')),
            ('M', _('Minimal')),
        )
    )
    """ Type of processing of the article """

    # identification
    issue = models.ForeignKey(
        'Issue',
        related_name='articles',
        verbose_name=_("Numéro"),
    )

    def get_fedora_model(self):
        return ArticleDigitalObject

    def get_erudit_class(self):
        return EruditArticle

    def get_full_identifier(self):
        return "{}.{}".format(
            self.issue.get_full_identifier(),
            self.localidentifier
        )

    def get_absolute_url(self):
        return reverse_url(
            "public:journal:article-detail",
            args=[
                self.issue.journal.code,
                self.issue.localidentifier,
                self.localidentifier
            ]
        )

    @property
    def open_access(self):
        """ Returns a boolean indicating if the article is in open access. """
        return self.issue.open_access or (
            self.issue.open_access is None and self.issue.journal.open_access)

    class Meta:
        verbose_name = _("Article")
        verbose_name_plural = _("Articles")


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
