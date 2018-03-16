from functools import reduce

from django.core.paginator import InvalidPage
from django.core.paginator import Paginator
from django.utils.six.moves.urllib import parse as urlparse

from .conf import settings as search_settings

# Most of this is copy/paste from django-rest-framework. We don't need half of this logic but we
# needed to be able to strip DRF out of our code safely.
# TODO: remove that stuff and properly piggyback on the fact that we *already* have paginated
#       results from solr.


def replace_query_param(url, key, val):
    """
    Given a URL and a key/val pair, set or replace an item in the query
    parameters of the URL, and return the new URL.
    """
    (scheme, netloc, path, query, fragment) = urlparse.urlsplit(url)
    query_dict = urlparse.parse_qs(query)
    query_dict[key] = [val]
    query = urlparse.urlencode(sorted(list(query_dict.items())), doseq=True)
    return urlparse.urlunsplit((scheme, netloc, path, query, fragment))


def remove_query_param(url, key):
    """
    Given a URL and a key/val pair, remove an item in the query
    parameters of the URL, and return the new URL.
    """
    (scheme, netloc, path, query, fragment) = urlparse.urlsplit(url)
    query_dict = urlparse.parse_qs(query)
    query_dict.pop(key, None)
    query = urlparse.urlencode(sorted(list(query_dict.items())), doseq=True)
    return urlparse.urlunsplit((scheme, netloc, path, query, fragment))


def _positive_int(integer_string, strict=False, cutoff=None):
    ret = int(integer_string)
    if ret < 0 or (ret == 0 and strict):
        raise ValueError()
    if cutoff:
        ret = min(ret, cutoff)
    return ret


class EruditDocumentPagination:
    page_size = search_settings.DEFAULT_PAGE_SIZE
    page_size_query_param = 'page_size'
    page_query_param = 'page'
    last_page_strings = ('last',)
    max_page_size = 50

    in_database_corpus = ('Article', 'Culturel', 'Thèses')

    def get_page_size(self, request):
        if self.page_size_query_param:
            try:
                return _positive_int(
                    request.query_params[self.page_size_query_param],
                    strict=True,
                    cutoff=self.max_page_size
                )
            except (KeyError, ValueError):
                pass

        return self.page_size

    def get_paginated_info(self):
        return {
            'count': self.page.paginator.count,
            'num_pages': self.page.paginator.num_pages,
            'current_page': self.page.number,
            'next_page': self.page.next_page_number() if self.page.has_next() else None,
            'previous_page': (
                self.page.previous_page_number()if self.page.has_previous() else None),
            'page_size': self.page.paginator.per_page,
            'links': {
                'next': self.get_next_link(),
                'previous': self.get_previous_link(),
            },
        }

    def paginate(self, docs_count, documents, request):
        """
        This is the default implementation of the PageNumberPagination.paginate_queryset method ;
        the only exception: the pagination is performed on a dummy list of the same length as the
        number of results returned by the search engine in use. But the EruditDocument instances
        corresponding to the documents associated with the current page are returned. Note
        that these documents have already been paginated by the search engine.
        """
        page_size = self.get_page_size(request)
        if not page_size:  # pragma: no cover
            return None

        paginator = Paginator(range(docs_count), page_size)
        page_number = request.query_params.get(self.page_query_param, 1)
        if page_number in self.last_page_strings:  # pragma: no cover
            page_number = paginator.num_pages

        try:
            self.page = paginator.page(page_number)
        except InvalidPage:
            # invalid page? let's show first page.
            self.page = paginator.page(1)

        self.request = request

        # This is a specific case in order to remove some sub-strings from the localidentifiers
        # at hand. This is a bit ugly but we are limited here by the predefined Solr document IDs.
        # For example the IDs are prefixed by "unb:" for UNB articles... But UNB localidentifiers
        # should not be stored with "unb:" into the database.
        drop_keywords = ['unb:', ]
        for document in documents:
            document['ID'] = reduce(lambda s, k: s.replace(k, ''), drop_keywords, document['ID'])

        return documents

    def get_next_link(self):
        if not self.page.has_next():
            return None
        url = self.request.build_absolute_uri()
        page_number = self.page.next_page_number()
        return replace_query_param(url, self.page_query_param, page_number)

    def get_previous_link(self):
        if not self.page.has_previous():
            return None
        url = self.request.build_absolute_uri()
        page_number = self.page.previous_page_number()
        if page_number == 1:
            return remove_query_param(url, self.page_query_param)
        return replace_query_param(url, self.page_query_param, page_number)
