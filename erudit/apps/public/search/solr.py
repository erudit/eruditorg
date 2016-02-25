import requests

from django.conf import settings
from django.utils.translation import ugettext_lazy as _

# Fields available for sorting
SORT_FIELDS = {
    "relevance": "score",
    "year": "AnneePublication",
    "author": "Auteur_tri",
    "title": "Titre_idx",
}

# Fields available for filtering
FILTER_FIELDS = {
    "years": {
        "field": "AnneePublication",
        "label": _("Années de publication")
    },
    "article_types": {
     "field": "TypeArticle_fac",
     "label": _("Types d'articles")
    },
    "languages": {
        "field": "Langue",
        "label": _("Langues")
    },
    "collections": {
     "field": "TitreCollection_fac",
     "label": _("Collections")
    },
    "authors": {
        "field": "Auteur_tri",
        "label": _("Auteurs")
    },
    "funds": {
        "field": "Fonds_fac",
        "label": _("Fonds")
    },
    "publication_types": {
        "field": "Corpus_fac",
        "label": _("Types de publication")
    },
}


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
        self.sort_fields = SORT_FIELDS
        self.filter_fields = FILTER_FIELDS

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

    def clean_data(self, raw_data):
        cleaned_data = {
            "results_count": 0,
            "doc_ids": [],
            "filter_choices": {},
        }

        # Results count
        cleaned_data["results_count"] = raw_data["response"]["numFound"]

        # List of documents IDs
        for doc in raw_data["response"]["docs"]:
            doc_id = doc.get("ID", None)

            if doc_id:
                cleaned_data["doc_ids"].append(doc_id)

        # Possible filters
        # Loop through all filters we are interested in
        for django_field_name, field_details in self.filter_fields.items():
            try:
                # If filter found in solr data, try to format it in nicer dict
                filter_field_choices = \
                    raw_data["facet_counts"]["facet_fields"][field_details["field"]]
                filter_field_choices_dict = {
                    filter_field_choices[i]:
                        filter_field_choices[i+1] for i in range(0, len(filter_field_choices), 2)
                }

                # Add to dictionnary of filters
                cleaned_data["filter_choices"][django_field_name] = {
                    "label": field_details["label"],
                    "values": filter_field_choices_dict,
                }
            except:
                pass

        return cleaned_data

    def simple_search(self, search_term, sort="relevance", sort_order="asc",
                      limit_filter_fields=FILTER_FIELDS, start_at=0, results_per_query=10):
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
        params["facet"] = "true"
        facet_fields = []
        for limit_filter_field in limit_filter_fields:
            try:
                facet_fields.append(self.filter_fields[limit_filter_field]["field"])
            except:
                pass
        params["facet.field"] = facet_fields

        return self.clean_data(raw_data=self.search(params=params))
