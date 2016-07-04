# -*- coding: utf-8 -*-

from django.db.models import Count
from django.db.models.functions import Substr
from django.db.models.functions import Upper

from erudit.models import Collection
from erudit.models import Thesis


def get_thesis_collections():
    """ Fetches and returns the collections associated with theses. """
    collection_ids = Thesis.objects.values_list('collection_id', flat=True)
    return Collection.objects.filter(id__in=collection_ids)


def get_thesis_counts_per_publication_year(queryset):
    """ Given a Thesis queryset returns a list of thesis counts per publication year.

    The returned aggregations are ordered by publication year (descending).
    """
    return queryset \
        .values('publication_year').annotate(total=Count('publication_year')) \
        .order_by('-publication_year')


def get_thesis_counts_per_author_first_letter(queryset):
    """ Given a Thesis queryset returns a list of thesis counts per author first letter.

    The returned aggregations are ordered by letter.
    """
    return queryset \
        .annotate(author_firstletter=Upper(Substr('author__lastname', 1, 1))) \
        .values('author_firstletter').annotate(total=Count('author_firstletter')) \
        .order_by('author_firstletter')
