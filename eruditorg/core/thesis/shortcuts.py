# -*- coding: utf-8 -*-

from erudit.models import Collection
from erudit.models import Thesis


def get_thesis_collections():
    """ Fetches and returns the collections associated with theses. """
    collection_ids = Thesis.objects.values_list('collection_id', flat=True)
    return Collection.objects.filter(id__in=collection_ids)
