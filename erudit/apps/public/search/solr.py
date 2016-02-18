
import requests

from django.conf import settings


class Solr(object):
    """Connects to Solr

    - simple_search: looks for search term with simple sorting options
    - advanced_seaerch: Advanced search
    """

    def __init__(self, base_url=settings.SOLR_ROOT):
        super(Solr, self).__init__()
        self.base_url = base_url
        self.result_format_paramt = "json"
        self.simple_search_index = "TexteComplet"
        self.sort_fields = {
            "relevance": "score",
            "year": "AnneePublication",
            "author": "Auteur_tri",
            "title": "Titre_idx",
        }
        self.filter_fields = {
            "years": "AnneePublication",
            # "article_types": "Corpus_fac",
            "languages": "Langue",
            # "collections": "",
            "authors": "Auteur_tri",
            "funds": "Fonds_fac",
            "publication_types": "Corpus_fac",
        }

    def search(self, params):
        """Does actual search on Solr based on params received from higher up functions"""
        search_url = "{base_url}select".format(base_url=self.base_url)

        # Actual call to Solr
        response = requests.get(search_url, params=params)

        # If error, return empty results
        if not (response.status_code == requests.codes.ok):
            return {}

        else:
            try:
                return response.json()
            except:
                return {}

    def simple_search(self, search_term, sort="relevance", sort_order="asc",
                      start_at=0, results_per_query=10):
        """Simple search

        - search_term: search term to look for

        - sort:
            - "relevance": score
            - "year": AnneePublication
            - "author": Auteur_fac
            - "title": Titre_fr

        - sort_order:
            - asc
            - desc

        - start_at: Used with pagination. Row number to start at

        - results_per_query: Used with pagination. Number of results per query to return
        """
        # Search format
        params = {
            "wt": self.result_format_paramt,
        }

        # String to search for
        params["q"] = "{simple_search_index}:{search_term}".format(
            simple_search_index=self.simple_search_index, search_term=search_term
        )

        # Sort param
        if not (sort == "default"):
            # Match sort param to Solr field
            sort_field = self.sort_fields.get(sort, None)

            if sort_field:
                params["sort"] = "{sort_field} {sort_order}".format(
                    sort_field=sort_field, sort_order=sort_order
                )

        # Results per query
        params["rows"] = results_per_query

        # Start position (for pagination)
        params["start"] = start_at

        # Filter fields params
        params["filter.fields"] = (self.filter_fields.values())

        return self.search(params=params)
