from core.solrq.query import Q

from . import solr_search
from .conf import settings as search_settings
from .utils import positive_int
from .pagination import get_pagination_info, ResultsStats


class SolrFilter:
    """Return filtered Solr documents

    This "filter" class can process many individual filters that should be translated to Solr
    parameters in order to query a Solr index of Érudit documents. This filter should only be used
    on API views associated with EruditDocument-related models.
    """

    OP_AND = "AND"
    OP_OR = "OR"
    OP_NOT = "NOT"
    operators = [
        OP_AND,
        OP_OR,
        OP_NOT,
    ]

    operators_correspondence = {
        " AND ": [
            " ET ",
        ],
        " OR ": [" OU "],
        " NOT ": [" SAUF "],
    }

    aggregation_correspondence = {
        "Annee": "year",
        "TypeArticle_fac": "article_type",
        "Langue": "language",
        "TitreCollection_fac": "collection",
        "Auteur_tri": "author",
        "Fonds_fac": "fund",
        "Corpus_fac": "publication_type",
    }

    def translate_boolean_operators(self, search_term):
        if not search_term:
            return search_term

        for operator, correspondences in self.operators_correspondence.items():
            for correspondence in correspondences:
                search_term = search_term.replace(correspondence, operator)
        return search_term

    def build_solr_filters(self, query_params=None):
        """ Return the filters to use to query the Solr index. """
        filters = {}
        query_params = query_params or {}

        # STEP 1: register main search filters
        # --

        # Simple search parameters
        basic_search_term = self.translate_boolean_operators(
            query_params.get("basic_search_term", "*")
        )
        basic_search_field = query_params.get("basic_search_field", "all")
        filters.update(
            {"q": {"term": basic_search_term, "field": basic_search_field, "operator": None}}
        )

        # Advanced search parameters
        advanced_q = []
        for i in range(search_settings.MAX_ADVANCED_PARAMETERS):
            search_term = self.translate_boolean_operators(
                query_params.get("advanced_search_term{}".format(i + 1), None)
            )
            search_field = query_params.get("advanced_search_field{}".format(i + 1), "all")
            search_operator = query_params.get("advanced_search_operator{}".format(i + 1), None)

            if search_term and search_operator in self.operators:
                advanced_q.append(
                    {
                        "term": search_term,
                        "field": search_field,
                        "operator": search_operator,
                    }
                )
        filters.update({"advanced_q": advanced_q})

        # STEP 2: register other search filters
        # --

        # Publication year filter
        pub_year_start = query_params.get("pub_year_start", None)
        pub_year_end = query_params.get("pub_year_end", None)
        if pub_year_start:
            filters.update({"pub_year_start": pub_year_start})
        if pub_year_end:
            filters.update({"pub_year_end": pub_year_end})

        # Languages filter
        languages = query_params.getlist("languages", [])
        if languages:
            filters.update({"languages": languages})

        # Funds filter
        funds = query_params.getlist("funds", [])
        if funds:
            filters.update({"funds": funds})

        # Publication types filter
        publication_types = query_params.getlist("publication_types", [])
        if publication_types:
            filters.update({"publication_types": publication_types})

        # Article types filter
        article_types = query_params.getlist("article_types", [])
        if article_types:
            filters.update({"article_types": article_types})

        # Disciplines filter
        disciplines = query_params.getlist("disciplines", [])
        if disciplines:
            filters.update({"disciplines": disciplines})

        # Journals aggregation-filter
        journals = query_params.getlist("journals", [])
        if journals:
            filters.update({"journals": journals})

        # Extra Q filter
        extra_q = query_params.get("filter_extra_q", None)
        if extra_q:
            filters.update({"extra_q": extra_q})

        # STEP 3: register filters that are related to aggregation results
        # --

        # Because of their nature these filters should be applied last.

        # Publication years aggregation-filter
        agg_pub_years = query_params.getlist("filter_years", [])
        if agg_pub_years:
            filters.update({"agg_pub_years": agg_pub_years})

        # Languages aggregation-filter
        agg_languages = query_params.getlist("filter_languages", [])
        if agg_languages:
            filters.update({"agg_languages": agg_languages})

        # Types of documents aggregation-filter
        agg_document_types = query_params.getlist("filter_article_types", [])
        if agg_document_types:
            filters.update({"agg_document_types": agg_document_types})

        # Collections/journals aggregation-filter
        agg_journals = query_params.getlist("filter_collections", [])
        if agg_journals:
            filters.update({"agg_journals": agg_journals})

        # Authors aggregation-filter
        agg_authors = query_params.getlist("filter_authors", [])
        if agg_authors:
            filters.update({"agg_authors": agg_authors})

        # Funds aggregation-filter
        agg_funds = query_params.getlist("filter_funds", [])
        if agg_funds:
            filters.update({"agg_funds": agg_funds})

        # Publication types aggregation-filter
        agg_publication_types = query_params.getlist("filter_publication_types", [])
        if agg_publication_types:
            filters.update({"agg_publication_types": agg_publication_types})

        return filters

    def apply_solr_filters(self, filters):
        """ Applies the solr filters and returns the list of results. """
        search = solr_search.get_search()

        # Main search filters
        qfield = filters["q"]["field"]
        qterm = filters["q"]["term"]
        qoperator = filters["q"]["operator"]
        advanced_q = filters.get("advanced_q", [])

        # Other search filters
        pub_year_start = filters.get("pub_year_start", None)
        pub_year_end = filters.get("pub_year_end", None)
        languages = filters.get("languages", [])
        funds = filters.get("funds", [])
        publication_types = filters.get("publication_types", [])
        article_types = filters.get("article_types", [])
        disciplines = filters.get("disciplines", [])
        journals = filters.get("journals", [])

        # Results filters
        extra_q = filters.get("extra_q", None)

        # Aggregation filters
        agg_pub_years = filters.get("agg_pub_years", [])
        agg_languages = filters.get("agg_languages", [])
        agg_document_types = filters.get("agg_document_types", [])
        agg_journals = filters.get("agg_journals", [])
        agg_authors = filters.get("agg_authors", [])
        agg_funds = filters.get("agg_funds", [])
        agg_publication_types = filters.get("agg_publication_types", [])

        # STEP 1: applies the main search filters
        # --

        # Main filters
        query = (
            Q(**{qfield: qterm})
            if qoperator is None or qoperator != self.OP_NOT
            else ~Q(**{qfield: qterm})
        )
        for qparams in advanced_q:
            term = qparams.get("term")
            field = qparams.get("field")
            operator = qparams.get("operator")
            if operator == self.OP_AND:
                query &= Q(**{field: term})
            elif operator == self.OP_OR:
                query |= Q(**{field: term})
            elif operator == self.OP_NOT:
                query &= ~Q(**{field: term})
        sqs = search.filter(query, safe=True)

        # STEP 2: applies the other search filters
        # --

        # Applies the publication year filters
        if pub_year_start or pub_year_end:
            ystart = pub_year_start if pub_year_start is not None else "*"
            yend = pub_year_end if pub_year_end is not None else "*"
            sqs = sqs.filter_query(
                Annee="[{start} TO {end}]".format(start=ystart, end=yend), safe=True
            )

        # Applies the languages filter
        if languages:
            sqs = self._filter_solr_multiple(sqs, "Langue", languages, safe=True)

        # Applies the funds filter
        if funds:
            sqs = self._filter_solr_multiple(sqs, "Fonds_fac", funds, safe=True)

        # Applies the publication types filter
        if publication_types:
            sqs = self._filter_solr_multiple(sqs, "Corpus_fac", publication_types, safe=True)

        # Applies the publication types filter
        if article_types:
            sqs = self._filter_solr_multiple(sqs, "TypeArticle_fac", article_types, safe=True)

        # Applies the disciplines filter
        if disciplines:
            sqs = self._filter_solr_multiple(sqs, "Discipline_fac", disciplines, safe=True)

        # Applies the journals filter
        if journals:
            sqs = self._filter_solr_multiple(sqs, "RevueAbr", journals, safe=True)

        # STEP 3: applies the results filters
        # --

        if extra_q:
            extra_q = '"{}"'.format(extra_q)
            sqs = sqs.filter_query(all=extra_q, safe=True)

        # STEP 4: applies the aggregation-related filters
        # --

        # Applies the publication year aggregation-filter
        if agg_pub_years:
            sqs = self._filter_solr_multiple(sqs, "Annee", agg_pub_years, safe=True)

        # Applies the languages aggregation-filter
        if agg_languages:
            sqs = self._filter_solr_multiple(sqs, "Langue", agg_languages, safe=True)

        # Applies the types of documents aggregation-filter
        if agg_document_types:
            sqs = self._filter_solr_multiple(sqs, "TypeArticle_fac", agg_document_types, safe=True)

        # Applies the journals aggregation-filter
        if agg_journals:
            sqs = self._filter_solr_multiple(sqs, "TitreCollection_fac", agg_journals, safe=True)

        # Applies the authors aggregation-filter
        if agg_authors:
            sqs = self._filter_solr_multiple(sqs, "Auteur_tri", agg_authors, safe=True)

        # Applies the funds aggregation-filter
        if agg_funds:
            sqs = self._filter_solr_multiple(sqs, "Fonds_fac", agg_funds, safe=True)

        # Applies the publication types aggregation-filter
        if agg_publication_types:
            sqs = self._filter_solr_multiple(sqs, "Corpus_fac", agg_publication_types, safe=True)

        return sqs

    def get_solr_sorting(self, request):
        """ Get the Solr sorting string. """
        sort = request.GET.get("sort_by", "relevance")
        if sort == "relevance":
            return "score desc"
        elif sort == "title_asc":
            return "Titre_tri asc"
        elif sort == "title_desc":
            return "Titre_tri desc"
        elif sort == "author_asc":
            return "Auteur_tri asc"
        elif sort == "author_desc":
            return "Auteur_tri desc"
        elif sort == "pubdate_asc":
            return "Annee_tri asc"
        elif sort == "pubdate_desc":
            return "Annee_tri desc"

    def filter(self, request):
        # First we have to retrieve all the considered Solr filters.
        filters = self.build_solr_filters(request.GET.copy())

        # Then apply the filters in order to get lazy query containing all the filters.
        solr_query = self.apply_solr_filters(filters)

        # Prepares the values used to paginate the results using Solr.
        page_size = request.GET.get("page_size", search_settings.DEFAULT_PAGE_SIZE)
        page = request.GET.get("page", 1)
        try:
            page_size = positive_int(page_size, cutoff=50)
            page = positive_int(page)
        except ValueError:  # pragma: no cover
            page = 1
            page_size = search_settings.DEFAULT_PAGE_SIZE

        start = (page - 1) * page_size

        # Trigger the execution of the query in order to get a list of results from the Solr index.
        results = solr_query.get_results(
            sort=self.get_solr_sorting(request), rows=page_size, start=start
        )

        stats = ResultsStats(results.hits, page, page_size)

        pagination_info = get_pagination_info(stats, request)

        # Prepares the dictionnary containing aggregation results.
        aggregations_dict = {}
        for facet, flist in results.facets.get("facet_fields", {}).items():
            fdict = {flist[i]: flist[i + 1] for i in range(0, len(flist), 2)}
            aggregations_dict.update({self.aggregation_correspondence[facet]: fdict})

        return pagination_info, results.docs, aggregations_dict

    def _filter_solr_multiple(self, sqs, field, values, safe=False):
        query = Q()
        for v in values:
            query |= Q(**{field: '"{}"'.format(v)})
        return sqs.filter_query(query, safe=safe)
