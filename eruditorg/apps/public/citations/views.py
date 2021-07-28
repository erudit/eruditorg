import collections

from django.http import Http404
from django.utils.translation import gettext
from django.utils.translation import gettext_lazy as _
from django.views.generic import ListView
from django.views.generic import TemplateView
from django.views.generic import View
from django.shortcuts import redirect, reverse

from base.http import JsonAckResponse
from base.http import JsonErrorResponse
from erudit.solr.models import SolrDocument
from erudit.utils import locale_aware_sort


class SavedCitationListView(ListView):
    """ Show the list of saved citations associated with a specific user. """

    available_tris = collections.OrderedDict(
        (
            ("author_asc", _("Auteur (A–Z)")),
            ("author_desc", _("Auteur (Z–A)")),
            ("year_asc", _("Année (croissant)")),
            ("year_desc", _("Année (décroissant)")),
            ("title_asc", _("Titre (A–Z)")),
            ("title_desc", _("Titre (Z–A)")),
        )
    )
    context_object_name = "documents"
    paginate_by = 20
    template_name = "public/citations/list.html"

    def apply_sorting(self, objects_list):
        sortby, asc = self.get_sort_by().split("_")
        reverse = asc == "desc"
        attrname = {
            "author": "authors_display",
            "year": "publication_year",
            "title": "title",
        }.get(sortby, "title")

        # fallback sort
        objects_list = sorted(objects_list, key=lambda d: d.localidentifier)

        def key(doc):
            return str(getattr(doc, attrname, "")) or ""

        result = locale_aware_sort(objects_list, keyfunc=key)
        if reverse:
            result = list(reversed(result))
        return result

    def get(self, request, *args, **kwargs):
        # If the request query string page number is greater than the number of available
        # pages, redirect to the SavedCitationListView of the last available page
        num_pages = self.get_paginator(self.get_queryset(), self.paginate_by).num_pages
        query_params = self.request.GET.copy()
        query_string_page_number = query_params.get("page")

        # Check if trying to access a page number higher then the available
        try:
            if int(query_string_page_number) > num_pages:
                # Assign last available page
                query_params["page"] = num_pages
                return redirect(
                    "{}?{}".format(
                        reverse("public:citations:list"),
                        query_params.urlencode(),
                    )
                )
        except (TypeError, ValueError):
            pass

        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(SavedCitationListView, self).get_context_data(**kwargs)
        context["available_tris"] = self.available_tris
        context["sort_by"] = self.get_sort_by()

        # Get a list of all documents, not just the ones on the current page.
        object_list = context["paginator"].object_list
        counts = collections.Counter(d.corpus for d in object_list)
        context["scientific_articles_count"] = counts.get("Article", 0)
        context["cultural_articles_count"] = counts.get("Culturel", 0)
        context["theses_count"] = counts.get("Thèses", 0)
        context["total_citations_count"] = len(object_list)
        context["document_ids_not_on_page"] = [
            doc.solr_id for doc in object_list if doc not in context["page_obj"].object_list
        ]

        return context

    def get_queryset(self):
        solr_ids = self.request.saved_citations
        documents = []
        for solr_id in solr_ids:
            try:
                documents.append(SolrDocument.from_solr_id(solr_id))
            except ValueError:
                pass

        return self.apply_sorting(documents)

    def get_sort_by(self):
        sort_by = self.request.GET.get("sort_by", "title_asc")
        sort_by = sort_by if sort_by in self.available_tris else "title_asc"
        return sort_by


class SavedCitationAddView(View):
    """ Add an Érudit document to the list of documents associated to the current user. """

    http_method_names = [
        "post",
    ]

    def post(self, request):
        solr_id = request.POST.get("document_id", "")
        request.saved_citations.add(solr_id)
        request.saved_citations.save()
        return JsonAckResponse(saved_document_id=solr_id)


class SavedCitationRemoveView(View):
    """ Remove an Érudit document from the list of documents associated to the current user. """

    http_method_names = [
        "post",
    ]

    def post(self, request):
        solr_id = request.POST.get("document_id", "")
        try:
            request.saved_citations.remove(solr_id)
            request.saved_citations.save()
        except KeyError:
            return JsonErrorResponse(gettext("Ce document n'est pas présent dans les notices"))
        return JsonAckResponse(removed_document_id=solr_id)


class SavedCitationBatchRemoveView(View):
    """ Remove multiple Érudit documents from a list of documents. """

    http_method_names = [
        "post",
    ]

    def post(self, request):
        solr_ids = request.POST.getlist("document_ids", [])
        removed_document_ids = []
        for solr_id in solr_ids:
            if solr_id in request.saved_citations:
                request.saved_citations.remove(solr_id)
                removed_document_ids.append(solr_id)
        if not removed_document_ids:
            raise Http404()
        request.saved_citations.save()
        return JsonAckResponse(removed_document_ids=removed_document_ids)


class BaseEruditDocumentsCitationView(TemplateView):
    def get(self, request, *args, **kwargs):
        solr_ids = request.GET.getlist("document_ids", [])
        if not solr_ids:
            raise Http404()
        try:
            documents = [SolrDocument.from_solr_id(x) for x in solr_ids]
        except ValueError:
            raise Http404()
        context = self.get_context_data(documents=documents, **kwargs)
        return self.render_to_response(context)


class EruditDocumentsEnwCitationView(BaseEruditDocumentsCitationView):
    """ Returns the enw file of a set of Érudit documents. """

    content_type = "application/x-endnote-refer"
    template_name = "public/citations/eruditdocuments.enw"


class EruditDocumentsRisCitationView(BaseEruditDocumentsCitationView):
    """ Returns the ris file of a set of Érudit documents. """

    content_type = "application/x-research-info-systems"
    template_name = "public/citations/eruditdocuments.ris"


class EruditDocumentsBibCitationView(BaseEruditDocumentsCitationView):
    """ Returns the bib file of a set of Érudit documents. """

    content_type = "application/x-bibtex"
    template_name = "public/citations/eruditdocuments.bib"
