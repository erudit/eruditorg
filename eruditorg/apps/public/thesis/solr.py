from django.conf import settings
from django.core.cache import cache
from django.utils.text import slugify
import pysolr


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


def get_provider_summary(provider_name):
    cache_key = 'get_thesis_summary-{}'.format(slugify(provider_name))
    cached_result = cache.get(cache_key)
    if cached_result is not None:
        return cached_result
    client = get_client()
    query = 'Corpus_fac:Thèses Editeur:"{}"'.format(provider_name)
    args = {
        'q': query,
        'rows': '3',
        'sort': 'DateAjoutErudit desc',
        'facet.limit': '0',
    }
    solr_results = client.search(**args)
    result = (solr_results.hits, list(solr_results.docs))
    cache.set(cache_key, result)
    return result
