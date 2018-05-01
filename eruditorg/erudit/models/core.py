from django.contrib.auth.models import User
from django.db import models
from django.utils.translation import gettext as _
from polymorphic.models import PolymorphicModel
from taggit.managers import TaggableManager
from taggit.models import GenericTaggedItemBase
from taggit.models import TagBase

from ..managers.core import LegacyOrganisationManager
from ..modelfields import SizeConstrainedImageField


class Organisation(models.Model):
    """ A single organisation. """
    name = models.CharField(max_length=300, verbose_name=_('Nom'))

    street = models.CharField(max_length=200, null=True, blank=True, verbose_name=_('Adresse'))
    postal_code = models.CharField(
        max_length=50, null=True, blank=True, verbose_name=_('Code postal'))
    city = models.CharField(max_length=50, null=True, blank=True, verbose_name=_('Ville'))
    province = models.CharField(max_length=50, null=True, blank=True, verbose_name=_('Province'))
    country = models.CharField(max_length=50, null=True, blank=True, verbose_name=_('Pays'))

    badge = SizeConstrainedImageField(
        verbose_name=_('Badge'), blank=True, null=True, upload_to='organisation_badges', width=140,
        height=140)

    members = models.ManyToManyField(User, related_name='organisations', verbose_name=_('Membres'))

    objects = models.Manager()
    legacy_objects = LegacyOrganisationManager()

    class Meta:
        verbose_name = _('Organisation')
        verbose_name_plural = _('Organisations')
        ordering = ['name', ]

    def __str__(self):
        return self.name


class LegacyOrganisationProfile(models.Model):
    """ Profile of the organisation in the legacy ``restriction`` database. """

    organisation = models.OneToOneField('erudit.Organisation')
    account_id = models.CharField(max_length=10, verbose_name=_('Identifiant'))
    sushi_requester_id = models.CharField(
        max_length=10,
        verbose_name=_('Identifiant SUSHI'),
        blank=True,
        null=True
    )

    class Meta:
        verbose_name = _("Compatibilité avec la base de données restriction")

    def __str__(self):
        return "{} / {}".format(self.organisation.name, self.account_id)


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


class Publisher(models.Model):
    """ A simple publisher. """
    name = models.CharField(max_length=255, verbose_name=_('Nom'))

    class Meta:
        verbose_name = _('Éditeur')
        verbose_name_plural = _('Éditeurs')
        ordering = ['name', ]

    def __str__(self):
        return self.name


class Copyright(models.Model):
    """ A simple copyright. """
    text = models.CharField(max_length=600, verbose_name=_('Texte du copyright'))
    url = models.URLField(verbose_name=_('URL du copyright'), blank=True, null=True)

    class Meta:
        verbose_name = _("Droit d'auteur")
        verbose_name_plural = _("Droits d'auteurs")


class KeywordTag(TagBase):
    """ A keyword tag that can be used to add tags to a model. """
    language = models.CharField(max_length=10, verbose_name=_('Code langue'), blank=True, null=True)
    """ The language code associated with the keyword """

    class Meta:
        verbose_name = _('Mot-clé')
        verbose_name_plural = _('Mots-clés')


class KeywordTaggedWhatever(GenericTaggedItemBase):
    tag = models.ForeignKey(KeywordTag, related_name='%(app_label)s_%(class)s_items')


class ThesisProvider(models.Model):
    code = models.CharField(max_length=10, unique=True, verbose_name=_('Code'))
    name = models.CharField(max_length=200, verbose_name=_('Nom'))
    # Most of the time, same as "name", but not always...
    solr_name = models.CharField(max_length=200, db_index=True, verbose_name=_('Nom dans Solr'))
    logo = models.ImageField(verbose_name=_('Logo'), blank=True)

    class Meta:
        verbose_name = _("Éditeur de thèses")
        verbose_name_plural = _("Éditeurs de thèses")

    def __str__(self):
        return self.code


class EruditDocument(PolymorphicModel):
    """ An Érudit document.

    It can be an article, a thesis... This is a polymorphic model.
    """
    localidentifier = models.CharField(
        max_length=100, unique=True, verbose_name=_('Identifiant unique'), db_index=True,
        help_text=_('Identifiant Fedora du document'),
    )
    """ The unique identifier of an Érudit document. """

    keywords = TaggableManager(blank=True, through=KeywordTaggedWhatever)
    """ An Érudit document can be associated with multiple keywords. """

    class Meta:
        verbose_name = _('Document Érudit')
        verbose_name_plural = _('Documents Érudit')
