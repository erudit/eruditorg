# -*- coding: utf-8 -*-

"""
This module defines the main Query class. It is used by the solrq.Search class
to provide filtering capabilities on a Solr index.
"""


class Q(object):
    AND = 'AND'
    OR = 'OR'
    default = AND

    def __init__(self, **params):
        self.params = params.copy()
        self.operator = self.default
        self.operands = []
        self.negated = False

    def _combine(self, other, operator):
        if not isinstance(other, Q):
            raise TypeError(other)
        obj = type(self)()
        obj.operator = operator
        obj.operands.append(self if self.operands else self.params)
        obj.operands.append(other if other.operands else other.params)
        return obj

    def _negate(self):
        self.negated = not self.negated

    def __or__(self, other):
        return self._combine(other, self.OR)

    def __and__(self, other):
        return self._combine(other, self.AND)

    def __invert__(self):
        obj = type(self)()
        obj.operator = self.AND
        obj.operands.append(self if self.operands else self.params)
        obj._negate()
        return obj


class Query(object):
    """
    A Query object used to apply filters to a given Solr search.
    """
    filters_mapping = {}
    extra_params = {}

    def __init__(self, search, qs='*:*'):
        """ Search request to Solr.

        :arg search: `solrq.Search` instance to use
        :arg qs: a default Solr query string to use
        """
        self.search = search
        self._qs = qs

    def filter(self, *args, **kwargs):
        """ Prepares the querystring used to perform a query.

        This method returns a new instance of Query that allows
        to add another filters to the initial querystring.
        """
        qs = self._qs

        # Inserts Q params if applicable
        qarg_qs = None
        for qarg in args:
            subqs = self._get_q_querystring(qarg)
            qarg_qs = ' AND '.join([qarg_qs, subqs]) if qarg_qs else subqs
        qs = '({0}) AND ({1})'.format(qs, qarg_qs) if qarg_qs else qs

        # Inserts kwargs params
        kwargs_qs = self._get_querystring_from_dict(kwargs)
        qs = '({0}) AND ({1})'.format(qs, kwargs_qs) if kwargs_qs else qs

        return self.__class__(self.search, qs)

    def _get_q_querystring(self, q):
        subqs_list = []

        for qchild in q.operands:
            if isinstance(qchild, Q):
                subqs = self._get_q_querystring(qchild)
            else:
                subqs = self._get_querystring_from_dict(qchild)

            # Handles the case when the query is negated
            if q.negated:
                subqs = '*:* -{}'.format(subqs)

            if subqs is None:
                continue

            subqs = '({})'.format(subqs)
            subqs_list.append(subqs)

        if not len(subqs_list):
            return self._get_querystring_from_dict(q.params)

        return ' {} '.format(q.operator).join(subqs_list)

    def _get_querystring_from_dict(self, params_dict, base_qs=None):
        qs = base_qs
        # Inserts kwargs params
        for k, v in params_dict.items():
            if k in self.search.filters_mapping:
                subqs = self.search.filters_mapping[k].format(**{k: v})
            else:
                subqs = '{0}:{1}'.format(k, v)
            qs = ' AND '.join([qs, subqs]) if qs else subqs
        return qs

    def get_results(self):
        """ Triggers the search and returns the results. """
        return self.search.client.search(self._qs, **self.search.extra_params)

    results = property(get_results)
