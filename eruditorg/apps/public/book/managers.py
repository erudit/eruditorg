from django.db import models
from django.db.models import Q


class BookQuerySet(models.QuerySet):
    def published(self):
        """ Only check the top level status of the book to determine if it is published """
        return self.filter(
            Q(parent_book=None, is_published=True) | Q(parent_book__is_published=True)
        )

    def top_level(self):
        return self.filter(parent_book=None)


class BooksManager(models.Manager):
    def get_queryset(self):
        return BookQuerySet(self.model, using=self._db)
