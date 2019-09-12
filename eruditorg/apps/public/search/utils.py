from django.utils.translation import ugettext_lazy as _
from django.utils.six.moves.urllib import parse as urlparse

from .conf import settings as search_settings
from .forms import ADVANCED_SEARCH_FIELDS
from .forms import SearchForm


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


def positive_int(integer_string, strict=False, cutoff=None):
    ret = int(integer_string)
    if ret < 0 or (ret == 0 and strict):
        raise ValueError()
    if cutoff:
        ret = min(ret, cutoff)
    return ret


def GET_as_dict(GET, multi_params=None):
    multi_params = multi_params or []
    return {
        k: GET.getlist(k) if k in multi_params else GET.get(k)
        for k in GET}


def get_search_elements(queryparams, form=None):
    """ Returns the search query elements in a readable way.

    This should be used to express a query using the following format:

        (Titre, résumé, mots-clés : pedagogi*) ET (Titre, résumé, mots-clés : drama*) [...]

    """
    params = queryparams.copy()
    fields_correspondence = dict(ADVANCED_SEARCH_FIELDS)
    operator_correspondence = {
        'AND': _('ET'),
        'OR': _('OU'),
        'NOT': _('SAUF'),
    }
    if not form:
        form = SearchForm()

    search_elements = []

    def elements(t, f, o):
        f = fields_correspondence.get(f, f)
        o_, o = o, operator_correspondence.get(o, o)
        return {
            'term': t,
            'field': f,
            'operator': o_,
            'str': ('({field} : {term})'.format(field=f, term=t) if o is None
                    else ' {op} ({field} : {term})'.format(op=o, field=f, term=t)),
        }

    # Query terms
    q1_term = params.get('basic_search_term', '*')
    q1_field = params.get('basic_search_field', 'all')
    q1_operator = None
    search_elements.append(elements(q1_term, q1_field, q1_operator))

    for i in range(search_settings.MAX_ADVANCED_PARAMETERS):
        q_term = params.get('advanced_search_term{}'.format(i + 1), None)
        q_field = params.get('advanced_search_field{}'.format(i + 1), 'all')
        q_operator = params.get('advanced_search_operator{}'.format(i + 1), None)
        if q_term and q_operator in operator_correspondence:
            search_elements.append(elements(q_term, q_field, q_operator))

    o_, o = 'AND', operator_correspondence['AND']

    # Publication range
    pub_year_start = params.get('pub_year_start', None)
    pub_year_end = params.get('pub_year_end', None)
    if pub_year_start and pub_year_end:
        search_elements.append({
            'term': [pub_year_start, pub_year_end, ], 'field': 'pub_year', 'operator': o_,
            'str': _(' {op} (Publié entre {start} et {end})').format(
                op=o, start=pub_year_start, end=pub_year_end), })
    elif pub_year_start:
        search_elements.append({
            'term': pub_year_start, 'field': 'pub_year_start', 'operator': o_,
            'str': _(' {op} (Publié depuis {start})').format(op=o, start=pub_year_start), })
    elif pub_year_end:
        search_elements.append({
            'term': pub_year_end, 'field': 'pub_year_end', 'operator': o_,
            'str': _(" {op} (Publié jusqu'à {end})").format(op=o, end=pub_year_end), })

    # Languages & journals
    # Those fields use codes and we need to find the corresponding labels from the field choices.
    code_to_label_fields = ['languages', 'journals']
    for field_name in code_to_label_fields:
        codes = params.getlist(field_name, None)
        if codes is None:
            continue
        labels = [l[1] for l in form.fields[field_name].choices if l[0] in codes]
        if not labels:
            continue
        search_elements.append({
            'term': str(labels),
            'field': form.fields[field_name].label,
            'operator': o_,
            'str': ' {op} ({field} : {term})'.format(
                op=o,
                field=form.fields[field_name].label,
                term=str(labels),
            ),
        })

    # Other fields
    for k, v in params.items():
        if not k.startswith('advanced_search_') and not k.startswith('basic_search_') \
                and not k.startswith('pub_year') and k not in code_to_label_fields \
                and k in form.fields and v:
            f = form.fields[k].label
            t = params.getlist(k)
            t = t[0] if len(t) == 1 else str(t)
            search_elements.append({
                'term': t, 'field': f, 'operator': o_,
                'str': ' {op} ({field} : {term})'.format(op=o, field=f, term=t)})

    return search_elements
