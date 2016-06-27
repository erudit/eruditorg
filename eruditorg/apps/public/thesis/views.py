# -*- coding: utf-8 -*-

from collections import OrderedDict

from django.db.models import Count
from django.db.models.functions import Substr
from django.db.models.functions import Upper
from django.views.generic import DetailView
from django.views.generic import TemplateView
from erudit.models import Collection
from erudit.models import Thesis

from core.thesis.shortcuts import get_thesis_collections


class ThesisHomeView(TemplateView):
    """
    Displays the home page of thesis repositories.
    """
    template_name = 'public/thesis/home.html'

    def get_context_data(self, **kwargs):
        context = super(ThesisHomeView, self).get_context_data(**kwargs)

        # Fetches the collections associated with theses.
        collections = get_thesis_collections().order_by('name')
        collections_dict = OrderedDict()
        for collection in collections:
            collections_dict[collection.id] = {
                'collection': collection,
                'thesis_count': Thesis.objects.filter(collection=collection).count(),
                'recent_theses': list(
                    Thesis.objects.filter(collection=collection)
                    .order_by('-publication_year', '-oai_datestamp')[:3])
            }
        context['collections_dict'] = collections_dict

        return context


class ThesisCollectionHomeView(DetailView):
    """
    Displays the home page of a collection repository.
    """
    context_object_name = 'collection'
    model = Collection
    template_name = 'public/thesis/collection_home.html'

    def get_context_data(self, **kwargs):
        context = super(ThesisCollectionHomeView, self).get_context_data(**kwargs)
        collection = self.object

        # Inserts recent theses into the context.
        context['recent_theses'] = list(
            Thesis.objects.select_related('author').filter(collection=collection)
            .order_by('-publication_year', '-oai_datestamp')[:3])

        # Inserts the number of theses associated with this collection into the context.
        context['thesis_count'] = Thesis.objects.filter(collection=collection).count()

        # Inserts the thesis groups into the context.
        context['thesis_groups'] = self.get_thesis_groups()

        return context

    def get_queryset(self):
        return get_thesis_collections()

    def get_thesis_groups(self):
        collection = self.object
        theses = Thesis.objects.select_related('author').filter(collection=collection)
        publication_year_group = theses.values('publication_year') \
            .annotate(total=Count('publication_year')).order_by('-publication_year')
        author_name_group = theses \
            .annotate(author_firstletter=Upper(Substr('author__lastname', 1, 1))) \
            .values('author_firstletter').annotate(total=Count('author_firstletter')) \
            .order_by('author_firstletter')
        return {'by_publication_year': publication_year_group, 'by_author_name': author_name_group}
