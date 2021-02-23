from collections import namedtuple

from django.conf import settings
from django.core.cache import cache
from django.utils.text import slugify
import pysolr

from erudit.utils import pairify


def get_client():
    return pysolr.Solr(settings.SOLR_ROOT, timeout=settings.SOLR_TIMEOUT)


def get_thesis_count():
    client = get_client()
    query = "Corpus_fac:Thèses"
    args = {
        "q": query,
        "rows": "0",
        "facet.limit": "0",
    }
    solr_results = client.search(**args)
    return solr_results.hits


RepositorySummary = namedtuple("RepositorySummary", "count solr_dicts by_year by_author")


def get_repository_summary(repository_name):
    cache_key = "get_repository_summary-{}".format(slugify(repository_name))
    cached_result = cache.get(cache_key)
    if cached_result is not None:
        return cached_result
    client = get_client()
    query = 'Corpus_fac:Thèses Editeur:"{}"'.format(repository_name)
    args = {
        "q": query,
        "rows": "3",
        "sort": "DateAjoutErudit desc",
        "facet.field": ["AnneePublication", "AuteurNP_fac"],
        "facet.limit": "99999",  # all authors
    }
    solr_results = client.search(**args)
    result = RepositorySummary(
        solr_results.hits,
        list(solr_results.docs),
        list(pairify(solr_results.facets["facet_fields"]["AnneePublication"])),
        list(pairify(solr_results.facets["facet_fields"]["AuteurNP_fac"])),
    )
    cache.set(cache_key, result)
    return result


Theses = namedtuple("Theses", "count solr_dicts")


def get_theses(repository_name, rows=50, page=1, sort=None, year=None, author_letter=None):
    if sort is None:
        sort = ["DateAjoutErudit desc"]
    client = get_client()
    query = 'Corpus_fac:Thèses Editeur:"{}"'.format(repository_name)
    if year:
        query += " AnneePublication:{}".format(year)
    if author_letter:
        query += " Auteur_tri:{}*".format(author_letter)
    start = (page - 1) * rows
    args = {
        "q": query,
        "rows": str(rows),
        "start": start,
        "sort": sort,
        "facet.limit": "0",
    }
    solr_results = client.search(**args)
    result = Theses(
        solr_results.hits,
        list(solr_results.docs),
    )
    return result
