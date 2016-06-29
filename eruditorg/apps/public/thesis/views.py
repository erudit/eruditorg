# -*- coding: utf-8 -*-

from collections import OrderedDict

from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.utils.functional import cached_property
from django.utils.translation import ugettext_lazy as _
from django.views.generic import DetailView
from django.views.generic import ListView
from django.views.generic import TemplateView
from erudit.models import Collection
from erudit.models import Thesis

from core.thesis.shortcuts import get_thesis_collections
from core.thesis.shortcuts import get_thesis_counts_per_author_first_letter
from core.thesis.shortcuts import get_thesis_counts_per_publication_year


class ThesisHomeView(TemplateView):
    """ Displays the home page of thesis repositories. """
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
    """ Displays the home page of a collection repository. """
    context_object_name = 'collection'
    model = Collection
    pk_url_kwarg = 'collection_pk'
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
        publication_year_group = get_thesis_counts_per_publication_year(theses)
        author_name_group = get_thesis_counts_per_author_first_letter(theses)
        return {'by_publication_year': publication_year_group, 'by_author_name': author_name_group}


class BaseThesisListView(ListView):
    """ Base view for displaying a list of theses associated with a collection. """
    available_tris = OrderedDict((
        ('author_asc', _('Auteur (croissant)')),
        ('author_desc', _('Auteur (décroissant)')),
        ('date_asc', _("Date d'ajout (croissant)")),
        ('date_desc', _("Date d'ajout (décroissant)")),
        ('title_asc', _('Titre (croissant)')),
        ('title_desc', _('Titre (décroissant)')),
    ))
    collection_pk_url_kwarg = 'collection_pk'
    context_object_name = 'theses'
    model = Thesis
    paginate_by = 20

    def apply_sorting(self, qs):
        sort_by = self.get_sort_by()
        if sort_by == 'author_asc':
            qs = qs.order_by('author__lastname', 'author__firstname')
        elif sort_by == 'author_desc':
            qs = qs.order_by('-author__lastname', '-author__firstname')
        elif sort_by == 'date_asc':
            qs = qs.order_by('oai_datestamp')
        elif sort_by == 'date_desc':
            qs = qs.order_by('-oai_datestamp')
        elif sort_by == 'title_desc':
            qs = qs.order_by('-title')
        else:  # title_asc or other values...
            qs = qs.order_by('title')
        return qs

    def get_collection(self):
        return get_object_or_404(Collection, pk=self.kwargs.get(self.collection_pk_url_kwarg))

    def get_context_data(self, **kwargs):
        context = super(BaseThesisListView, self).get_context_data(**kwargs)
        context['collection'] = self.collection
        context['available_tris'] = self.available_tris
        context['sort_by'] = self.get_sort_by()

        # Inserts randomly selected theses into the context ("At a glance" section).
        context['random_theses'] = self.get_queryset().order_by('?')[:3]

        return context

    def get_queryset(self):
        qs = super(BaseThesisListView, self).get_queryset()
        qs = qs.select_related('collection', 'author').prefetch_related('keywords') \
            .filter(collection=self.collection)
        return self.apply_sorting(qs)

    def get_sort_by(self):
        sort_by = self.request.GET.get('sort_by', 'title_asc')
        sort_by = sort_by if sort_by in self.available_tris else 'title_asc'
        return sort_by

    @cached_property
    def collection(self):
        return self.get_collection()


class ThesisPublicationYearListView(BaseThesisListView):
    """ Displays theses for a specific year. """
    template_name = 'public/thesis/collection_list_per_year.html'
    year_url_kwarg = 'publication_year'

    def get_context_data(self, **kwargs):
        context = super(ThesisPublicationYearListView, self).get_context_data(**kwargs)
        context['publication_year'] = int(self.kwargs.get(self.year_url_kwarg))
        context['other_publication_years'] = get_thesis_counts_per_publication_year(
            Thesis.objects.filter(collection=self.collection))
        return context

    def get_queryset(self):
        qs = super(ThesisPublicationYearListView, self).get_queryset()
        year = self.kwargs.get(self.year_url_kwarg)
        return qs.filter(publication_year=year)


class ThesisPublicationAuthorNameListView(BaseThesisListView):
    """ Displays theses for a specific year. """
    template_name = 'public/thesis/collection_list_per_author_name.html'
    letter_url_kwarg = 'author_letter'

    def get_context_data(self, **kwargs):
        context = super(ThesisPublicationAuthorNameListView, self).get_context_data(**kwargs)
        context['author_letter'] = self.kwargs.get(self.letter_url_kwarg).upper()
        context['other_author_letters'] = get_thesis_counts_per_author_first_letter(
            Thesis.objects.filter(collection=self.collection))
        return context

    def get_queryset(self):
        qs = super(ThesisPublicationAuthorNameListView, self).get_queryset()
        letter = self.kwargs.get(self.letter_url_kwarg)
        return qs.filter(
            Q(author__lastname__startswith=letter.upper()) |
            Q(author__lastname__startswith=letter.lower()))
