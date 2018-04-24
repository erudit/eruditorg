from collections import OrderedDict

from django.db.models import Q
from django.http import Http404
from django.shortcuts import get_object_or_404
from django.utils.functional import cached_property
from django.utils.translation import ugettext_lazy as _
from django.views.generic import DetailView
from django.views.generic import ListView
from django.views.generic import TemplateView
from erudit.models import Collection
from erudit.models import Thesis
from erudit.solr.models import Generic

from apps.public.thesis.legacy import format_thesis_collection_code
from core.thesis.shortcuts import get_thesis_collections
from core.thesis.shortcuts import get_thesis_counts_per_author_first_letter
from core.thesis.shortcuts import get_thesis_counts_per_publication_year

from apps.public.viewmixins import FallbackAbsoluteUrlViewMixin, FallbackObjectViewMixin


class ThesisHomeView(FallbackAbsoluteUrlViewMixin, TemplateView):
    """ Displays the home page of thesis repositories. """
    template_name = 'public/thesis/home.html'
    fallback_url = "/these/"

    def get_context_data(self, **kwargs):
        context = super(ThesisHomeView, self).get_context_data(**kwargs)

        # Total number of theses for all collections
        context['total_count'] = Thesis.objects.count()

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


class ThesisCollectionHomeView(FallbackObjectViewMixin, DetailView):
    """ Displays the home page of a collection repository. """
    context_object_name = 'collection'
    model = Collection
    slug_url_kwarg = 'collection_code'
    slug_field = 'code'
    template_name = 'public/thesis/collection_home.html'

    fallback_url_format = '/these/liste.html'

    def get_fallback_querystring_dict(self):
        querystring_dict = super().get_fallback_querystring_dict()
        querystring_dict['src'] = format_thesis_collection_code(self.get_object().code)
        return querystring_dict

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
        ('author_asc', _('Auteur (A–Z)')),
        ('author_desc', _('Auteur (Z–A)')),
        ('date_asc', _("Date de publication (croissant)")),
        ('date_desc', _("Date de publication (décroissant)")),
        ('title_asc', _('Titre (A–Z)')),
        ('title_desc', _('Titre (Z–A)')),
    ))
    collection_code_url_kwarg = 'collection_code'
    context_object_name = 'theses'
    model = Thesis
    paginate_by = 50

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
        return get_object_or_404(Collection, code=self.kwargs.get(self.collection_code_url_kwarg))

    def get_context_data(self, **kwargs):
        context = super(BaseThesisListView, self).get_context_data(**kwargs)
        context['collection'] = self.collection
        context['available_tris'] = self.available_tris
        context['sort_by'] = self.get_sort_by()

        # Inserts the total number of theses for a given collection
        context['thesis_count'] = Thesis.objects.filter(collection=self.collection).count()

        # Inserts randomly selected theses into the context ("At a glance" section).
        context['random_theses'] = self.get_queryset().order_by('?')[:3]

        return context

    def get_queryset(self):
        qs = super(BaseThesisListView, self).get_queryset()
        qs = qs.select_related('collection', 'author').prefetch_related('keywords') \
            .filter(collection=self.collection)
        return self.apply_sorting(qs)

    def get_sort_by(self):
        sort_by = self.request.GET.get('sort_by', 'author_asc')
        sort_by = sort_by if sort_by in self.available_tris else 'author_asc'
        return sort_by

    @cached_property
    def collection(self):
        return self.get_collection()


class ThesisPublicationYearListView(FallbackObjectViewMixin, BaseThesisListView):
    """ Displays theses for a specific year. """
    template_name = 'public/thesis/collection_list_per_year.html'
    year_url_kwarg = 'publication_year'

    fallback_url_format = '/these/liste.html'

    def get_fallback_querystring_dict(self):
        querystring_dict = super().get_fallback_querystring_dict()
        querystring_dict['src'] = format_thesis_collection_code(self.get_collection().code)
        return querystring_dict

    def get_fallback_url_format_kwargs(self):
        kwargs = {}
        kwargs['code'] = format_thesis_collection_code(self.get_collection().code)
        return kwargs

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


class ThesisPublicationAuthorNameListView(FallbackObjectViewMixin, BaseThesisListView):
    """ Displays theses for a specific year. """
    template_name = 'public/thesis/collection_list_per_author_name.html'
    letter_url_kwarg = 'author_letter'
    fallback_url_format = '/these/liste.html'

    def get_fallback_querystring_dict(self):
        querystring_dict = super().get_fallback_querystring_dict()
        querystring_dict['src'] = format_thesis_collection_code(self.get_collection().code)
        querystring_dict['lettre'] = self.kwargs.get(self.letter_url_kwarg).upper()
        return querystring_dict

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


class BaseThesisCitationView(TemplateView):
    def get_context_data(self, **kwargs):
        result = super().get_context_data(**kwargs)
        try:
            result['thesis'] = Generic.from_solr_id(self.kwargs['solr_id'])
        except ValueError:
            raise Http404()
        return result


class ThesisEnwCitationView(BaseThesisCitationView):
    """ Returns the enw file of a specific thesis. """
    content_type = 'application/x-endnote-refer'
    template_name = 'public/thesis/citation/thesis.enw'


class ThesisRisCitationView(BaseThesisCitationView):
    """ Returns the ris file of a specific thesis. """
    content_type = 'application/x-research-info-systems'
    template_name = 'public/thesis/citation/thesis.ris'


class ThesisBibCitationView(BaseThesisCitationView):
    """ Returns the bib file of a specific thesis. """
    content_type = 'application/x-bibtex'
    template_name = 'public/thesis/citation/thesis.bib'
