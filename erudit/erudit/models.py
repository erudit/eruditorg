from datetime import datetime as dt

from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext as _

from django.contrib.admin.widgets import AdminDateWidget

# choices

YEARS = tuple((n, n) for n in range(1900, dt.now().year + 6))


# abstracts

class Person(models.Model):
    """Personne"""

    lastname = models.CharField(
        max_length=50,
        verbose_name=_("Nom")
    )

    firstname = models.CharField(
        max_length=50,
        verbose_name=_("Prénom")
    )

    email = models.EmailField(
        verbose_name=_("Courriel")
    )

    organisation = models.ForeignKey(
        "Organisation"
    )


class Organisation(models.Model):
    """Organisation"""

    name = models.CharField(
        max_length=120,
        verbose_name=_("Nom")
    )

    street = models.CharField(
        max_length=200,
        verbose_name=_("Adresse")
    )

    postal_code = models.CharField(
        max_length=50,
        verbose_name=_("Code postal")
    )

    city = models.CharField(
        max_length=50,
        verbose_name=_("Ville")
    )

    province = models.CharField(
        max_length=50,
        verbose_name=_("Province")
    )

    country = models.CharField(
        max_length=50,
        verbose_name=_("Pays")
    )


class Common(models.Model):
    """Common fields to each Model"""

    # system
    user_created = models.ForeignKey(
        User,
        related_name='+',
        verbose_name="Créé par",
    )
    date_created = models.DateField(
        auto_now_add=True,
        verbose_name="Créé le",
    )
    user_modified = models.ForeignKey(
        User,
        related_name='+',
        verbose_name="Modifié par",
    )

    date_modified = models.DateField(
        auto_now=True,
        verbose_name="Modifié le",
    )

    class Meta:
        abstract = True


class Named(models.Model):

    # identification
    name = models.CharField(
        max_length=255,
        verbose_name="Nom",
        help_text="Nom officiel",
    )

    display_name = models.CharField(
        max_length=255,
        null=True, blank=True,
        verbose_name="Nom d'affichage",
        help_text="Nom à utiliser dans tout affichage",
    )

    def __str__(self):
        return self.display_name or self.name

    class Meta:
        abstract = True


class Comment(models.Model):

    author = models.ForeignKey(
        User,
        related_name='+',
        verbose_name="Soumis par",
    )
    comment = models.TextField(
        verbose_name="Commentaire",
    )
    date = models.DateTimeField(
        auto_now=True,
        verbose_name="Soumis le",
    )

    class Meta:
        abstract = True
        verbose_name = "Commentaire"
        verbose_name_plural = "Commentaires"
        ordering = ['date']


class Library(models.Model):
    """Bibliothèque"""
    name = models.CharField(max_length=255)


class Journal(Common, Named):
    """Revue"""

    # identification
    code = models.CharField(
        max_length=255,
        help_text="Identifiant unique (utilisé dans URL Érudit)",
    )

    issn_print = models.CharField(
        max_length=255,
        null=True, blank=True,
        verbose_name="ISSN imprimé",
    )

    issn_web = models.CharField(
        max_length=255,
        null=True, blank=True,
        verbose_name="ISSN web",
    )

    formerly = models.ForeignKey(
        'Journal',
        null=True, blank=True,
        verbose_name="Anciennement",
        help_text="Choisir l'ancien nom de la revue",
    )

    publisher = models.ForeignKey(
        'Publisher',
        null=True,
        blank=True,
        related_name='journals',
        verbose_name="Éditeur",
    )

    type = models.ForeignKey(
        'JournalType',
        null=True,
        blank=True,
        verbose_name="Type",
    )

    paper = models.BooleanField(
        default=False,
        verbose_name="Papier",
        help_text="Est publiée également en version papier?",
    )

    open_access = models.BooleanField(
        default=True,
        verbose_name="Open access",
    )

    issues_per_year = models.IntegerField(
        null=True, blank=True,
        verbose_name="Numéros par année",
    )

    # coordinates
    url = models.URLField(
        null=True, blank=True,
        verbose_name="URL",
    )

    address = models.TextField(
        null=True, blank=True,
        verbose_name="Adresse",
    )

    # status
    active = models.BooleanField(
        default=True,
        verbose_name="Actif",
        help_text="Une revue inactive n'édite plus de numéros",
    )

    # issues
    def first_issue(self):
        pass

    def last_issue(self):
        pass

    def last_oa_issue(self):
        pass

    # contract
    def has_active_contract(self):
        pass

    class Meta:
        verbose_name = "Revue"
        verbose_name_plural = "Revues"
        ordering = ['name']


class JournalType(models.Model):
    """Type de revue
    ex.: Savante, Culturelle
    """
    name = models.CharField(max_length=255)


class Issue(models.Model):
    """Numéro"""

    # identification
    journal = models.ForeignKey('Journal', related_name='issues')
    year = models.IntegerField(choices=YEARS)
    volume = models.CharField(max_length=255)
    number = models.CharField(max_length=255)
    special_issue = models.BooleanField()

    date_produced = models.DateField()
    date_published = models.DateField()

    open_access = models.BooleanField()

    # status { in_production, published }


class Publisher(models.Model):
    """Éditeur"""
    name = models.CharField(max_length=255)

    members = models.ManyToManyField(
        User
    )

# comments

# class LibraryComment(Common, Comment):
#    library = models.ForeignKey('Library', related_name='comments')


class JournalComment(Comment):
    journal = models.ForeignKey('Journal', related_name='comments')

# class IssueComment(Common, Comment):
#    issue = models.ForeignKey('Issue', related_name='comments')

# class PublisherComment(Common, Comment):
#    publisher = models.ForeignKey('Publisher', related_name='comments')
