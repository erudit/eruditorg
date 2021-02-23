from typing import Optional

from django.conf import settings
from django.db import models
from django.utils.text import slugify
from django.utils.translation import gettext as _

from core.email import Email
from .managers import BooksManager


class BookCollection(models.Model):

    """A collection of conference proceedings volumes or books,
    grouped under a theme or an organisation"""

    name = models.CharField(max_length=200, verbose_name=_("Titre de collection"))
    slug = models.SlugField(
        max_length=200,
        null=False,
        blank=False,
    )
    logo = models.ImageField(
        blank=True,
        null=True,
        verbose_name=_("Logo de collection"),
    )
    description = models.TextField(
        blank=True,
        null=True,
        max_length=1500,
        verbose_name=_("Description de la collection"),
    )
    path = models.CharField(
        max_length=200,
        verbose_name=_("répertoire"),
        null=True,
        blank=True,
    )

    class Meta:
        verbose_name = _("Collection d’actes ou de livres")
        verbose_name_plural = _("Collections d’actes ou de livres")

    def __str__(self):
        return self.name


class Book(models.Model):

    """A single volume of conference proceedings or
    a single book"""

    TYPE_CHOICES = (
        ("li", _("Livre")),
        ("ac", _("Actes")),
    )

    title = models.CharField(
        max_length=400,
        verbose_name=_("Titre"),
    )

    parent_book = models.ForeignKey("Book", null=True, blank=True, on_delete=models.CASCADE)

    slug = models.SlugField(
        max_length=200,
        null=False,
        blank=False,
    )
    subtitle = models.CharField(
        blank=True,
        null=True,
        max_length=200,
        verbose_name=_("Sous-titre"),
    )
    year = models.PositiveIntegerField(
        blank=True,
        null=True,
        verbose_name=_("Année de publication"),
    )
    cover = models.ImageField(
        blank=True, null=True, verbose_name=_("Couverture"), upload_to="book_cover"
    )
    publisher = models.CharField(
        blank=True,
        null=True,
        max_length=200,
        verbose_name=_("Éditeur"),
    )
    publisher_url = models.URLField(
        blank=True,
        null=True,
        max_length=200,
        verbose_name=_("Site web de l’éditeur"),
    )
    type = models.CharField(
        max_length=2,
        choices=TYPE_CHOICES,
        default="li",
    )
    isbn = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        verbose_name=_("ISBN"),
    )
    digital_isbn = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        verbose_name=_("ISBN numérique"),
    )
    authors = models.CharField(
        blank=True,
        null=True,
        max_length=200,
        verbose_name=_("Auteurs"),
    )

    contributors = models.CharField(
        blank=True,
        null=True,
        max_length=200,
        verbose_name=_("Contributeurs"),
    )

    contribution = models.BooleanField(
        verbose_name=_("Contribution des auteurs de type direction ?"),
        help_text=_(
            "La liste des auteurs sera précédée de \
        la mention «&nbsp;Sous la direction de…&nbsp;»."
        ),
        default=False,
    )
    collection = models.ForeignKey(
        BookCollection,
        blank=True,
        null=True,
        related_name="books",
        on_delete=models.CASCADE,
    )
    copyright = models.CharField(
        blank=True,
        null=True,
        max_length=200,
        verbose_name=_("Mention du droit d’auteur"),
    )
    path = models.CharField(
        max_length=200,
        verbose_name=_("Répertoire"),
        null=True,
        blank=True,
    )
    is_open_access = models.BooleanField(
        verbose_name=_("Disponible en libre accès ?"),
        default=False,
    )
    is_published = models.BooleanField(verbose_name=_("Est publié ?"), default=True)

    objects = BooksManager()

    class Meta:
        verbose_name = _("Livre")
        verbose_name_plural = _("Livres")

    def __str__(self):
        return self.title

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._original_is_published = self.is_published

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = short_slug(self.title, self.isbn or self.digital_isbn)
        if self._original_is_published != self.is_published:
            emails = settings.BOOKS_UPDATE_EMAILS
            if len(emails):
                email = Email(
                    emails,
                    html_template="emails/book/book_update_content.html",
                    subject_template="emails/book/book_update_subject.html",
                    extra_context={"book": self},
                    tag="www-livres",
                )
                email.send()
        return super().save(*args, **kwargs)


def short_slug(title: str, isbn: Optional[str]) -> str:
    s = slugify(title)
    parts = s.split("-")
    parts = [part for part in parts if part not in STOPWORDS]
    length = 0
    for i, part in enumerate(parts):
        length += len(part) + 1
        if length > 80:
            parts = parts[:i]
            break
    slug = "-".join(parts)
    if isbn:
        slug = "{}--{}".format(slug, isbn)
    return slug


STOPWORDS = {"le", "la", "un", "une", "de", "d", "du", "des", "et", "son", "sa", "ses"}
