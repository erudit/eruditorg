from collections import defaultdict, OrderedDict
from operator import itemgetter

from django.conf import settings
from django.core.cache import cache
from django.utils.text import slugify
import pysolr

from erudit.solr.models import SolrDocument


def get_client():
    return pysolr.Solr(settings.SOLR_ROOT, timeout=settings.SOLR_TIMEOUT)


def _get_first_letter(name):
    if not name:
        return ""
    name = slugify(name)
    if not name:
        return ""
    return name[0].upper()


def get_journal_authors_article_types(journal_code):
    client = get_client()
    query = "RevueAbr:{}".format(journal_code)
    args = {
        "q": query,
        "rows": "0",
        "facet.field": "TypeArticle_fac",
    }
    solr_results = client.search(**args)
    facets = solr_results.facets["facet_fields"]["TypeArticle_fac"]
    # See comment for same line in get_journal_authors_letters()
    article_types = facets[::2]
    return set(article_types)


def get_journal_authors_letters(journal_code, article_type, normalized=True):
    # To get a list of available letters for a particular journal in the fastest way possible,
    # we use face results so that we don't have to iterate through mathcing articles, but matching
    # authors.
    cache_key = "get_journal_authors_letters-{}-{}-{}".format(
        journal_code, slugify(article_type), normalized
    )
    cached_result = cache.get(cache_key)
    if cached_result is not None:
        return cached_result
    client = get_client()
    query = "RevueAbr:{}".format(journal_code)
    if article_type:
        query += ' TypeArticle_fac:"{}"'.format(article_type)
    args = {
        "q": query,
        "rows": "0",
        "facet.field": "AuteurNP_fac",
        "facet.limit": "99999",  # all authors
    }
    solr_results = client.search(**args)
    facets = solr_results.facets["facet_fields"]["AuteurNP_fac"]
    # facets is a list of alternating name and number ['foo', 42, 'bar', 12]
    # You know that very *very* rarely used "step" field in python's list slicing? we're going to
    # actually use it!
    author_names = facets[::2]
    result = (name.strip() for name in author_names)
    result = (name for name in result if name)
    if normalized:
        result = {_get_first_letter(name) for name in result}
    else:
        result = {name[0] for name in result}
    cache.set(cache_key, result)
    return result


def get_journal_authors_dict(journal_code, first_letter, article_type):
    cache_key = "get_journal_authors_dict-{}-{}-{}".format(
        journal_code, first_letter, slugify(article_type)
    )
    cached_result = cache.get(cache_key)
    if cached_result is not None:
        return cached_result

    # Before we query, we need to go fetch all "related letters", that is, all letters that
    # normalize to `first_letter`. If we don't do that, we won't get author names starting with an
    # accent.
    all_letters = get_journal_authors_letters(journal_code, article_type, normalized=False)
    relevant_letters = {
        letter for letter in all_letters if _get_first_letter(letter) == first_letter
    }
    if not relevant_letters:
        return OrderedDict()
    client = get_client()
    authorname_queries = " OR ".join("{}*".format(letter) for letter in relevant_letters)
    query = "RevueAbr:{} AuteurNP_fac:({})".format(journal_code, authorname_queries)
    fl = [
        "ID",
        "AuteurNP_fac",
        "Annee",
        "URLDocument",
        "Titre_fr",
        "Titre_en",
        "Titre_es",
        "Titre_defaut",
        "TitreRefBiblio_aff",
    ]
    if article_type:
        query += ' TypeArticle_fac:"{}"'.format(article_type)
    args = {
        "q": query,
        "fl": ",".join(fl),
        "rows": "99999",
        "facet.limit": "0",
    }
    solr_results = client.search(**args)
    result = defaultdict(list)
    for solr_data in solr_results.docs:
        article = SolrDocument(solr_data)
        authors = article.authors_list
        article_dict = {
            "id": article.localidentifier,
            "year": article.year or "",
            "url": article.url,
            "title": article.title,
        }
        for author in authors:
            if author[:1] in relevant_letters:
                contributors = list(authors)
                contributors.remove(author)
                article_dict["author"] = author
                # Slugify the dict keys to avoid duplicate author entries.
                result[slugify(author)].append(dict(article_dict, contributors=contributors))
    for articles in result.values():
        articles.sort(key=itemgetter("year"), reverse=True)
    result = OrderedDict((k, v) for (k, v) in sorted(result.items()))
    cache.set(cache_key, result)
    return result
