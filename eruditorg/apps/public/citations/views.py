# -*- coding: utf-8 -*-

import collections

from django.contrib.contenttypes.models import ContentType
from django.http import Http404
from django.shortcuts import get_object_or_404
from django.utils.translation import ugettext
from django.utils.translation import ugettext_lazy as _
from django.views.generic import ListView
from django.views.generic import TemplateView
from django.views.generic import View

from erudit.models import Article
from erudit.models import EruditDocument
from erudit.models import Thesis

from base.http import JsonAckResponse
from base.http import JsonErrorResponse
from core.metrics.viewmixins import MetricCaptureMixin


class SavedCitationListView(ListView):
    """ Show the list of saved citations associated with a specific user. """
    available_tris = collections.OrderedDict((
        ('author_asc', _('Auteur (A–Z)')),
        ('author_desc', _('Auteur (Z–A)')),
        ('year_asc', _('Année (croissant)')),
        ('year_desc', _('Année (décroissant)')),
        ('title_asc', _('Titre (A–Z)')),
        ('title_desc', _('Titre (Z–A)')),
    ))
    context_object_name = 'documents'
    model = EruditDocument
    paginate_by = 20
    template_name = 'public/citations/list.html'

    def apply_sorting(self, objects_list):
        sort_by = self.get_sort_by()
        if sort_by == 'author_asc' or sort_by == 'author_desc':
            reverse = sort_by == 'author_desc'
            author_list = []
            for doc in objects_list:
                if isinstance(doc, Thesis):
                    author_list.append((doc.author.lastname or doc.author.firstname, doc))
                elif isinstance(doc, Article):
                    authors = doc.erudit_object.get_authors(formatted=False)
                    authors = [None] if not authors else authors
                    author_list.extend(
                        (((a.lastname or a.firstname) if a else '', doc) for a in authors))
            author_list = sorted(author_list, key=lambda d: d[0], reverse=reverse)
            new_objects_list = []
            new_objects_list.extend(
                doc[1] for doc in author_list if doc[1] not in set(new_objects_list))
            objects_list = new_objects_list
        elif sort_by == 'year_asc':
            objects_list = sorted(objects_list, key=lambda d: d.publication_year)
        elif sort_by == 'year_desc':
            objects_list = sorted(objects_list, key=lambda d: d.publication_year, reverse=True)
        elif sort_by == 'title_desc':
            objects_list = sorted(objects_list, key=lambda d: d.title, reverse=True)
        else:  # title_asc or other values...
            objects_list = sorted(objects_list, key=lambda d: d.title)
        return objects_list

    def get_context_data(self, **kwargs):
        context = super(SavedCitationListView, self).get_context_data(**kwargs)
        context['available_tris'] = self.available_tris
        context['sort_by'] = self.get_sort_by()
        context['article_ct'] = ContentType.objects.get_for_model(Article)
        context['thesis_ct'] = ContentType.objects.get_for_model(Thesis)

        # Computes the number of scientific articles, theses, ...
        context['scientific_articles_count'] = self.article_qs \
            .filter(issue__journal__type__code='S').count()
        context['cultural_articles_count'] = self.article_qs \
            .filter(issue__journal__type__code='C').count()
        context['theses_count'] = self.thesis_qs.count()

        return context

    def get_queryset(self):
        qs = super(SavedCitationListView, self).get_queryset()
        qs = qs.filter(id__in=list(self.request.saved_citations))

        # Stores some querysets associated with each type of document for further use.
        article_ids = qs.instance_of(Article).values_list('id', flat=True)
        thesis_ids = qs.instance_of(Thesis).values_list('id', flat=True)
        self.article_qs = Article.objects.filter(id__in=article_ids) \
            .select_related('issue', 'issue__journal', 'issue__journal__type')
        self.thesis_qs = Thesis.objects.filter(id__in=thesis_ids) \
            .select_related('collection', 'author')

        articles = list(self.article_qs)
        [setattr(a, 'publication_year', a.issue.year) for a in articles]
        theses = list(self.thesis_qs)

        objects_list = articles + theses
        return self.apply_sorting(objects_list)

    def get_sort_by(self):
        sort_by = self.request.GET.get('sort_by', 'title_asc')
        sort_by = sort_by if sort_by in self.available_tris else 'title_asc'
        return sort_by


class SavedCitationAddView(MetricCaptureMixin, View):
    """ Add an Érudit document to the list of documents associated to the current user. """
    http_method_names = ['post', ]
    tracking_metric_name = 'erudit__citation__add'

    def post(self, request, document_id):
        document = get_object_or_404(EruditDocument, pk=document_id)
        request.saved_citations.add(document)
        request.saved_citations.save()
        return JsonAckResponse(saved_document_id=document.id)


class SavedCitationRemoveView(MetricCaptureMixin, View):
    """ Remove an Érudit document from the list of documents associated to the current user. """
    http_method_names = ['post', ]
    tracking_metric_name = 'erudit__citation__remove'

    def post(self, request, document_id):
        document = get_object_or_404(EruditDocument, pk=document_id)
        try:
            request.saved_citations.remove(document)
            request.saved_citations.save()
        except KeyError:
            return JsonErrorResponse(ugettext("Ce document n'est pas présent dans les notices"))
        return JsonAckResponse(removed_document_id=document.id)


class SavedCitationBatchRemoveView(MetricCaptureMixin, View):
    """ Remove multiple Érudit documents from a list of documents. """
    http_method_names = ['post', ]
    tracking_metric_name = 'erudit__citation__remove'

    def post(self, request):
        document_ids = request.POST.getlist('document_ids', [])
        try:
            assert document_ids
            document_ids = list(map(int, document_ids))
        except (AssertionError, ValueError):
            raise Http404
        documents = EruditDocument.objects.filter(id__in=document_ids)
        removed_document_ids = []
        for d in documents:
            if d in request.saved_citations:
                request.saved_citations.remove(d)
                removed_document_ids.append(d.id)
        request.saved_citations.save()
        return JsonAckResponse(removed_document_ids=removed_document_ids)


class BaseEruditDocumentsCitationView(TemplateView):
    def get(self, request, *args, **kwargs):
        document_ids = request.GET.getlist('document_ids', [])
        try:
            assert document_ids
            document_ids = list(map(int, document_ids))
        except (AssertionError, ValueError):
            raise Http404
        documents = EruditDocument.objects.filter(id__in=document_ids)
        context = self.get_context_data(documents=documents, **kwargs)
        return self.render_to_response(context)

    def get_context_data(self, **kwargs):
        context = super(BaseEruditDocumentsCitationView, self).get_context_data(**kwargs)
        context['article_ct'] = ContentType.objects.get_for_model(Article)
        context['thesis_ct'] = ContentType.objects.get_for_model(Thesis)
        return context


class EruditDocumentsEnwCitationView(BaseEruditDocumentsCitationView):
    """ Returns the enw file of a set of Érudit documents. """
    content_type = 'application/x-endnote-refer'
    template_name = 'public/citations/eruditdocuments.enw'


class EruditDocumentsRisCitationView(BaseEruditDocumentsCitationView):
    """ Returns the ris file of a set of Érudit documents. """
    content_type = 'application/x-research-info-systems'
    template_name = 'public/citations/eruditdocuments.ris'


class EruditDocumentsBibCitationView(BaseEruditDocumentsCitationView):
    """ Returns the bib file of a set of Érudit documents. """
    content_type = 'application/x-bibtex'
    template_name = 'public/citations/eruditdocuments.bib'
