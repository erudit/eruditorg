# -*- coding: utf-8 -*-

"""
This module defines the main Search class allowing to perform searches
inside a Solr index.

This is based on the use of pysolr.
"""

from .query import Query


class Search:
    """ Defines a convenient way to perform searches on a Solr index. """

    # This attribute can be used to map specific fiter names to more
    # complex expressions. It must be of the form:
    #
    # {
    #    'author': '(Auteur_tri:*{author}* OR Auteur_fac:*{author}*)',
    #    [...]
    # }
    filters_mapping = {}

    # This attribute can be used to specify the parameters passed to the
    # Solr repository when performing requests.
    #
    # Example:
    #
    # {
    #    'rows': 0,
    #    'facet': true,
    #    [...]
    # }
    extra_params = {}

    def __init__(self, solr_client):
        """Search request to Solr.

        :arg solr_client: `pysolr.Solr` instance to use
        """
        self.client = solr_client

    def filter(self, *args, **kwargs):
        """ Returns a Query instance for the considered parameters. """
        return Query(self).filter(*args, **kwargs)

    def get_results(self, **kwargs):
        """ Returns the results of the search. """
        return self.filter().get_results(**kwargs)

    results = property(get_results)
