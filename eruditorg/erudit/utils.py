import locale
import re


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
        locale.setlocale(locale.LC_COLLATE, localename)
    sort_key_func = get_sort_key_func(localename[:2])
    if keyfunc is not None:
        key = lambda x: sort_key_func(keyfunc(x))  # noqa
    else:
        key = sort_key_func
    result = sorted(elems, key=key)
    if oldlocale:
        locale.setlocale(locale.LC_COLLATE, oldlocale)
    return result
