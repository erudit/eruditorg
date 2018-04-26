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
    query = 'Corpus_fac:Thèses'
    args = {
        'q': query,
        'rows': '0',
        'facet.limit': '0',
    }
    solr_results = client.search(**args)
    return solr_results.hits


ProviderSummary = namedtuple('ProviderSummary', 'count solr_dicts by_year by_author')


def get_provider_summary(provider_name):
    cache_key = 'get_provider_summary-{}'.format(slugify(provider_name))
    cached_result = cache.get(cache_key)
    if cached_result is not None:
        return cached_result
    client = get_client()
    query = 'Corpus_fac:Thèses Editeur:"{}"'.format(provider_name)
    args = {
        'q': query,
        'rows': '3',
        'sort': 'DateAjoutErudit desc',
        'facet.field': ['AnneePublication', 'AuteurNP_fac'],
        'facet.limit': '99999',  # all authors
    }
    solr_results = client.search(**args)
    result = ProviderSummary(
        solr_results.hits,
        list(solr_results.docs),
        list(pairify(solr_results.facets['facet_fields']['AnneePublication'])),
        list(pairify(solr_results.facets['facet_fields']['AuteurNP_fac'])),
    )
    cache.set(cache_key, result)
    return result


Theses = namedtuple('Theses', 'count solr_dicts')


def get_theses(provider_name, rows=50, page=1, sort=None, year=None, author_letter=None):
    if sort is None:
        sort = ['DateAjoutErudit desc']
    client = get_client()
    query = 'Corpus_fac:Thèses Editeur:"{}"'.format(provider_name)
    if year:
        query += ' AnneePublication:{}'.format(year)
    if author_letter:
        query += ' Auteur_tri:{}*'.format(author_letter)
    start = (page - 1) * rows
    args = {
        'q': query,
        'rows': str(rows),
        'start': start,
        'sort': sort,
        'facet.limit': '0',
    }
    solr_results = client.search(**args)
    result = Theses(
        solr_results.hits,
        list(solr_results.docs),
    )
    return result
