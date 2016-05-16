# -*- coding: utf-8 -*-

from django.utils.translation import ugettext_lazy as _

from .conf import settings as search_settings
from .forms import ADVANCED_SEARCH_FIELDS
from .forms import SearchForm


def get_search_elements(request):
        """ Returns the search query elements in a readable way.

        This should be used to express a query using the following format:

            (Titre, résumé, mots-clés : pedagogi*) ET (Titre, résumé, mots-clés : drama*) [...]

        """
        params = request.GET.copy()
        fields_correspondence = dict(ADVANCED_SEARCH_FIELDS)
        operator_correspondence = {
            'AND': _('ET'),
            'OR': _('OU'),
            'NOT': _('NON'),
        }

        search_elements = []

        # Query terms

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

        q1_term = params.get('basic_search_term', '*')
        q1_field = params.get('basic_search_field', 'all')
        q1_operator = params.get('basic_search_operator', None)
        q1_operator = 'NOT' if q1_operator is not None else None
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

        # Other fields

        dummy_form = SearchForm()
        for k, v in params.items():
            if not k.startswith('advanced_search_') and not k.startswith('basic_search_') \
                    and not k.startswith('pub_year') and k in dummy_form.fields and v:
                f = dummy_form.fields[k].label
                t = params.getlist(k)
                t = t[0] if len(t) == 1 else str(t)
                search_elements.append({
                    'term': t, 'field': f, 'operator': o_,
                    'str': ' {op} ({field} : {term})'.format(op=o, field=f, term=t)})

        return search_elements
