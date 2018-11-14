import locale
import logging
import re
from itertools import islice
from functools import wraps
from django.db import models


logger = logging.getLogger(__name__)

# Mind your order! Longer stopwords should come first to avoid shorter ones applying first.
# (example: "Les" has to come before "Le").
FR_STOPWORDS = [r"les\s", r"le\s", r"la\s", r"l'", r"l’"]
RE_FR_STOPPREFIXES = re.compile(r'^({})'.format('|'.join(FR_STOPWORDS)), re.IGNORECASE)


def strip_stopwords_prefix(name, lang='fr'):
    if lang == 'fr':
        name = RE_FR_STOPPREFIXES.sub('', name)
    return name


def get_sort_key_func(lang='fr'):
    """ Returns a sort key func appropriate for sorting names in eruditorg.

    WARNING: this sorting is locale-aware. Before calling this, make sure that you set the proper
    locale. You can also sort your list through locale_aware_sort() which does this.
    """
    def get_sort_key(name):
        name = strip_stopwords_prefix(name, lang)
        return locale.strxfrm(name.strip())

    return get_sort_key


def locale_aware_sort(elems, keyfunc=None, localename='fr_CA.UTF-8'):
    """ Sorts elems with get_sort_key() under the localename context.

    keyfunc should return the "raw" value to sort. get_sort_key() will be applied to that raw
    value before sorting.
    """
    oldlocale = locale.getlocale(locale.LC_COLLATE)
    if oldlocale == localename:
        oldlocale = None
    else:
        try:
            locale.setlocale(locale.LC_COLLATE, localename)
        except locale.Error:
            # Will not sort properly, but let's not crash for that...
            logger.warning("Unable to set locale %s", localename)
            oldlocale = None

    sort_key_func = get_sort_key_func(localename[:2])
    if keyfunc is not None:
        key = lambda x: sort_key_func(keyfunc(x))  # noqa
    else:
        key = sort_key_func
    result = sorted(elems, key=key)
    if oldlocale:
        locale.setlocale(locale.LC_COLLATE, oldlocale)
    return result


def pairify(iterable):
    """ Pair every two items of a list into a tuple.

    Useful for solr facets.

    Example: pairify(['foo', 1, 'bar', 2]) -> [('foo', 1), ('bar', 2)]
    """
    return zip(islice(iterable, None, None, 2), islice(iterable, 1, None, 2))


class PaginatedAlready:
    """ Mocks django's Paginator object to wrap items that are *already* paginated.

    You will usually want to use this in templates to re-use a standard paginated template
    without needing to modify it.
    """
    def __init__(self, paginate_by, total_count, page_number):
        self.paginate_by = paginate_by
        self.total_count = total_count
        self.number = int(page_number)

    @property
    def num_pages(self):
        if not self.paginate_by:
            return 1
        result, modulo = divmod(self.total_count, self.paginate_by)
        if modulo:
            result += 1
        return result

    @property
    def has_previous(self):
        return self.number > 1

    @property
    def has_next(self):
        return self.number < self.num_pages

    @property
    def previous_page_number(self):
        if self.has_previous:
            return self.number - 1

    @property
    def next_page_number(self):
        if self.has_next:
            return self.number + 1


def catch_and_log(func):

    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception:
            logger.exception("Exception raised in a @catch_and_log function %s", func.__name__)
            return None

    return wrapper


def qs_cache_key(qs: models.QuerySet) -> str:
    """ Build a cache key using the primary key of all the objects in the queryset

    The cache key will change whenever the queryset changes. This is useful in the case where
    you want to burst the cache whenever the children of an object changes.

    :param qs: ``QuerySet`` with which the cache key will be built.
    :returns: the cache key

    """
    if qs.count() == 0:
        return ""
    return ",".join([str(o.id) for o in qs.all()])
