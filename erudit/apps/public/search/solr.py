import requests

from django.conf import settings

# Search fields
SEARCH_FIELDS = {
    "all": "TexteComplet",
    "meta": "Metadonnees",
    "full_text": "TexteIntegral",
    "title_abstract_keywords": "TitreResumeMots",
    "title": "Titre_idx",
    "author": "Auteur_idx",
    "author_affiliation": "Affiliation_idx",
    "journal_title": "TitreCollection_idx",
    "bibliography": "RefBiblio_idx",
    "title_reviewd": "TitreRefBiblio_idx",
    "issn": "ISSN",
    "isbn": "ISBN",
}

EXTRA_SEARCH_FIELDS = {
    "years": "AnneePublication",
    "date_added": "DateAjoutIndex",
    "funds": "Fonds_fac",
    "publication_types": "Corpus_fac",
}

# Fields available for sorting
SORT_FIELDS = {
    "relevance": "score",
    "year": "AnneePublication",
    "author": "Auteur_tri",
    "title": "Titre_idx",
}

# Fields available for filtering
FILTER_FIELDS = {
    "years": "AnneePublication",
    "article_types": "TypeArticle_fac",
    "languages": "Langue",
    "collections": "TitreCollection_fac",
    "authors": "Auteur_tri",
    "funds": "Fonds_fac",
    "publication_types": "Corpus_fac",
}


class Solr(object):
    """Connects to Solr

    - search: looks for search term with simple sorting options
    - advanced_seaerch: Advanced search
    """

    def __init__(self, base_url=settings.SOLR_ROOT):
        super(Solr, self).__init__()
        self.base_url = base_url
        self.result_format_paramt = "json"
        self.search_index = "TexteComplet"
        self.search_fields = SEARCH_FIELDS
        self.extra_search_fields = EXTRA_SEARCH_FIELDS
        self.filter_fields = FILTER_FIELDS
        self.sort_fields = SORT_FIELDS

    def call_api(self, params):
        """Does actual search on Solr based on params received from higher up functions"""
        search_url = "{base_url}select".format(base_url=self.base_url)

        # Actual call to Solr
        response = requests.get(search_url, params=params)

        # If error, return empty results
        if not (response.status_code == requests.codes.ok):
            return response.url, {}

        else:
            try:
                return response.url, response.json()
            except:
                return None, {}

    def format_solr_date(self, date_string):
        if "T" not in date_string.upper():
            return "{date_string}T23:59:59Z".format(date_string=date_string)
        else:
            return date_string

    def clean_data(self, raw_data):
        cleaned_data = {
            "results_count": 0,
            "doc_ids": [],
            "filter_choices": {},
        }

        # Results count
        try:
            cleaned_data["results_count"] = raw_data["response"]["numFound"]
        except:
            pass

        # List of documents IDs
        try:
            for doc in raw_data["response"]["docs"]:
                doc_id = doc.get("ID", None)

                if doc_id:
                    cleaned_data["doc_ids"].append(doc_id)
        except:
            pass

        # Possible filters
        # Loop through all filters we are interested in
        for django_field_name, solr_field_name in self.filter_fields.items():
            try:
                # If filter found in solr data, try to format it in nicer dict
                filter_field_choices = \
                    raw_data["facet_counts"]["facet_fields"][solr_field_name]
                filter_field_choices_dict = {
                    filter_field_choices[i]:
                        filter_field_choices[i+1] for i in range(0, len(filter_field_choices), 2)
                }

                # Add to dictionnary of filters
                cleaned_data["filter_choices"][django_field_name] = {
                    "values": filter_field_choices_dict,
                }
            except:
                pass

        return cleaned_data

    def bulid_filters_query(self, selected_filters):
        """Will return query filter in the form of:
        Langue:(fr) Annee(2010 OR 2011 OR 2012)
        """
        filters_query = []
        for filter_name, filter_values in selected_filters.items():
            solr_field_name = self.filter_fields[filter_name]
            # Wrap filters in quotes
            filter_values = [
                '"{filter_value}"'.format(filter_value=filter_value) for
                filter_value in filter_values
            ]
            filters_query.append("{field}:({values})".format(
                field=solr_field_name,
                values=' OR '.join(filter_values))
            )

        return " ".join(filters_query)

    def build_advanced_search_query(self, advanced_search):
        """Will build query for advanced search in the form of:
        (Titre_idx:"foo" OR Auteur_idx:"foo bar" AND - Titre_idx:"foo")
        """
        advanced_search_query = []
        for search_item in advanced_search:
            # If no search term specified, than not a search
            if search_item["search_term"]:
                # Only use operator if
                if advanced_search_query or (search_item["search_operator"] == "NOT"):
                    operator = search_item["search_operator"]
                else:
                    operator = ""

                advanced_search_query.append(
                    "{operator} {field}:{term}".format(
                        operator=operator,
                        field=self.search_fields[search_item["search_field"]],
                        # term='"{search_term}"'.format(
                        #     search_term=search_item["search_term"]
                        # ),
                        term=search_item["search_term"],
                    )
                )

        return "({query_string})".format(query_string=" ".join(advanced_search_query))

    def bulid_search_extras_query(self, search_extras):
        publication_date = search_extras.get("publication_date", {})
        available_since = search_extras.get("available_since", None)
        funds = search_extras.get("funds", None)
        pub_types = search_extras.get("pub_types", None)

        search_extras_query = []

        if publication_date:
            pub_year_start = publication_date.get("pub_year_start", "*")
            pub_year_end = publication_date.get("pub_year_end", "*")
            search_extras_query.append("{field}:[{pub_year_start} TO {pub_year_end}]".format(
                field=self.extra_search_fields["years"],
                pub_year_start=pub_year_start,
                pub_year_end=pub_year_end
            ))

        if available_since:
            search_extras_query.append("{field}:[{available_since} TO NOW]".format(
                field=self.extra_search_fields["date_added"],
                available_since=self.format_solr_date(date_string=available_since),
            ))

        if funds:
            search_extras_query.append("{field}:({funds})".format(
                field=self.extra_search_fields["funds"],
                funds=" OR ".join(funds),
            ))

        if pub_types:
            search_extras_query.append("{field}:({funds})".format(
                field=self.extra_search_fields["publication_types"],
                funds=" OR ".join(funds),
            ))

        return " ".join(search_extras_query)

    def search(self, search_term, sort="relevance", sort_order="asc",
               limit_filter_fields=FILTER_FIELDS, selected_filters={},
               advanced_search=[], search_extras={}, start_at=0, results_per_query=10):
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

        - limit_filter_fields: limited list of filter

        - selected_filters: selected filter for query

        - start_at: Used with pagination. Row number to start at

        - results_per_query: Used with pagination. Number of results per query to return
        """
        # Search format
        params = {
            "wt": self.result_format_paramt,
        }

        # String to search for
        params["q"] = "{search_index}:{search_term}".format(
            search_index=self.search_index,
            search_term=search_term
        )

        if selected_filters:
            params["q"] = "{base_search} {filters_query}".format(
                base_search=params["q"],
                filters_query=self.bulid_filters_query(selected_filters=selected_filters)
            )

        if advanced_search:
            params["q"] = "{base_search} {advanced_search_query}".format(
                base_search=params["q"],
                advanced_search_query=self.build_advanced_search_query(
                    advanced_search=advanced_search
                )
            )

        if search_extras:
            params["q"] = "{base_search} {search_extras_query}".format(
                base_search=params["q"],
                search_extras_query=self.bulid_search_extras_query(
                    search_extras=search_extras
                )
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

        query_url, raw_data = self.call_api(params=params)
        return self.clean_data(raw_data=raw_data)
