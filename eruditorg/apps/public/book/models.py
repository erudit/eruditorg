from django.contrib import admin
from django.db import models
from django.utils.translation import gettext as _

class BookCollection(models.Model):

    """ A collection of conference proceedings volumes or books,
    grouped under a theme or an organisation """

    name = models.CharField(
        max_length=200,
        verbose_name=_('Titre de collection')
    )
    logo = models.ImageField(
        blank=True,
        null=True,
        verbose_name=_('Logo de collection'),
    )
    description = models.TextField(
        blank=True,
        null=True,
        max_length=1500,
        verbose_name=_('Description de la collection'),
    )

    class Meta:
        verbose_name = _('Collection d’actes ou de livres')
        verbose_name_plural = _('Collections d’actes ou de livres')

    def __str__(self):
        return self.name


class Book(models.Model):

    """ A single volume of conference proceedings or
    a single book """

    TYPE_CHOICES = (
        ('li', _('Livre')),
        ('co', _('Actes')),
    )

    title = models.CharField(
        max_length=400,
        verbose_name=_('Titre'),
    )
    subtitle = models.CharField(
        blank=True,
        null=True,
        max_length=200,
        verbose_name=_('Sous-titre'),
    )
    year = models.PositiveIntegerField(
        blank=True,
        null=True,
        verbose_name=_('Année de publication'),
    )
    cover = models.ImageField(
        blank=True,
        null=True,
        verbose_name=_('Couverture'),
        upload_to=('book_cover')
    )
    publisher = models.CharField(
        blank=True,
        null=True,
        max_length=200,
        verbose_name=_('Éditeur'),
    )
    publisher_url = models.URLField(
        blank=True,
        null=True,
        max_length=200,
        verbose_name=_('Site web de l’éditeur'),
    )
    type = models.CharField(
        max_length=2,
        choices=TYPE_CHOICES,
        default='li',
    )
    isbn = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        verbose_name=_('ISBN'),
    )
    digital_isbn = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        verbose_name=_('ISBN numérique'),
    )
    authors = models.CharField(
        blank=True,
        null=True,
        max_length=200,
        verbose_name=_('Auteurs'),
    )

    contributors = models.CharField(
        blank=True,
        null=True,
        max_length=200,
        verbose_name=_('Contributeurs'),
    )

    contribution = models.BooleanField(
        verbose_name=_('Contribution des auteurs de type direction ?'),
        help_text=_('La liste des auteurs sera précédée de \
        la mention «&nbsp;Sous la direction de…&nbsp;».'),
        default=False,
    )
    collection = models.ForeignKey(
        BookCollection,
        blank=True,
        null=True,
        related_name='books',
    )
    copyright = models.CharField(
        blank=True,
        null=True,
        max_length=200,
        verbose_name=_('Mention du droit d’auteur'),
    )

    class Meta:
        verbose_name = _('Livre')
        verbose_name_plural = _('Livres')

    def __str__(self):
        return self.title
