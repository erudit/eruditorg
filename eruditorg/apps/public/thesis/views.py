import re
from collections import OrderedDict, defaultdict

from django.conf import settings
from django.http import Http404
from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator
from django.utils.functional import cached_property
from django.utils.translation import gettext_lazy as _
from django.views.decorators.cache import cache_page
from django.views.generic import DetailView
from django.views.generic import ListView
from django.views.generic import TemplateView
from erudit.models import ThesisRepository
from erudit.solr.models import SolrDocument, Thesis
from erudit.utils import PaginatedAlready

from apps.public.thesis.legacy import format_thesis_collection_code

from apps.public.viewmixins import FallbackAbsoluteUrlViewMixin, FallbackObjectViewMixin
from . import solr


def year_counts(summary):
    for year, count in sorted(summary.by_year, reverse=True):
        if not year.isdigit():
            continue
        yield year, count


def first_letter_counts(summary):
    counts = defaultdict(int)

    for author, count in summary.by_author:
        m = re.search(r'\w', author)
        if m:
            counts[m.group(0).upper()] += count

    return sorted(counts.items())


@method_decorator(cache_page(settings.SHORT_TTL), name='dispatch')
class ThesisHomeView(FallbackAbsoluteUrlViewMixin, TemplateView):
    """ Displays the home page of thesis repositories. """
    template_name = 'public/thesis/home.html'
    fallback_url = "/these/"

    def get_context_data(self, **kwargs):
        context = super(ThesisHomeView, self).get_context_data(**kwargs)

        # Total number of theses for all collections
        context['total_count'] = solr.get_thesis_count()

        # Fetches the collections associated with theses.
        repositories = ThesisRepository.objects.all().order_by('name')
        repository_summaries = []
        for repository in repositories:
            theses = solr.get_theses(repository.solr_name, rows=3)
            recent_theses = list(map(Thesis, theses.solr_dicts))
            repository_summaries.append({
                'repository': repository,
                'thesis_count': theses.count,
                'recent_theses': recent_theses,
            })
        context['repository_summaries'] = repository_summaries

        return context


@method_decorator(cache_page(settings.SHORT_TTL), name='dispatch')
class ThesisCollectionHomeView(FallbackObjectViewMixin, DetailView):
    """ Displays the home page of a collection repository. """
    context_object_name = 'repository'
    model = ThesisRepository
    slug_url_kwarg = 'collection_code'
    slug_field = 'code'
    template_name = 'public/thesis/collection_home.html'

    fallback_url_format = '/these/liste.html'

    def get_fallback_querystring_dict(self):
        querystring_dict = super().get_fallback_querystring_dict()
        querystring_dict['src'] = format_thesis_collection_code(self.get_object().code)
        return querystring_dict

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        repository = self.object
        self.summary = solr.get_repository_summary(repository.solr_name)
        recent_theses = list(map(Thesis, self.summary.solr_dicts))

        # Inserts recent theses into the context.
        context['recent_theses'] = recent_theses

        # Inserts the number of theses associated with this collection into the context.
        context['thesis_count'] = self.summary.count

        return context

    def by_publication_year(self):
        return year_counts(self.summary)

    def by_author_first_letter(self):
        return first_letter_counts(self.summary)


class BaseThesisListView(ListView):
    """ Base view for displaying a list of theses associated with a collection. """
    available_tris = OrderedDict((
        ('author_asc', _('Auteur (A–Z)')),
        ('author_desc', _('Auteur (Z–A)')),
        ('date_asc', _("Date de publication (croissant)")),
        ('date_desc', _("Date de publication (décroissant)")),
    ))
    collection_code_url_kwarg = 'collection_code'
    context_object_name = 'theses'
    paginate_by = 50

    def get_solr_sort_arg(self):
        sort_by = self.get_sort_by()
        if sort_by == 'author_asc':
            return ['Auteur_tri asc']
        elif sort_by == 'author_desc':
            return ['Auteur_tri desc']
        elif sort_by == 'date_asc':
            return ['AnneePublication asc', 'DateAjoutErudit asc']
        elif sort_by == 'date_desc':
            return ['AnneePublication desc', 'DateAjoutErudit desc']

    def get_context_data(self, **kwargs):
        context = super(BaseThesisListView, self).get_context_data(**kwargs)
        context['repository'] = self.repository
        context['available_tris'] = self.available_tris
        context['sort_by'] = self.get_sort_by()
        context['thesis_count'] = self.summary.count
        context['sidebar_theses'] = list(map(Thesis, self.summary.solr_dicts))

        return context

    def get_queryset(self):
        return list(map(Thesis, self.theses.solr_dicts))

    def get_sort_by(self):
        sort_by = self.request.GET.get('sort_by', 'author_asc')
        sort_by = sort_by if sort_by in self.available_tris else 'author_asc'
        return sort_by

    def paginate_queryset(self, queryset, page_size):
        page = PaginatedAlready(self.paginate_by, self.theses.count, self.page_number)
        return (page, page, queryset, True)

    @property
    def page_number(self):
        page_kwarg = self.page_kwarg
        try:
            return int(self.kwargs.get(page_kwarg) or self.request.GET.get(page_kwarg) or 1)
        except ValueError:
            return 1

    @cached_property
    def repository(self):
        return get_object_or_404(
            ThesisRepository,
            code=self.kwargs.get(self.collection_code_url_kwarg))

    @cached_property
    def theses(self):
        return solr.get_theses(
            self.repository.solr_name, rows=self.paginate_by, page=self.page_number,
            sort=self.get_solr_sort_arg(), **self.get_extra_theses_kwargs())

    @cached_property
    def summary(self):
        return solr.get_repository_summary(self.repository.solr_name)


@method_decorator(cache_page(settings.SHORT_TTL), name='dispatch')
class ThesisPublicationYearListView(FallbackObjectViewMixin, BaseThesisListView):
    """ Displays theses for a specific year. """
    template_name = 'public/thesis/collection_list_per_year.html'
    year_url_kwarg = 'publication_year'
    fallback_url_format = '/these/liste.html'

    def get_fallback_querystring_dict(self):
        querystring_dict = super().get_fallback_querystring_dict()
        querystring_dict['src'] = format_thesis_collection_code(self.repository.code)
        return querystring_dict

    def get_fallback_url_format_kwargs(self):
        kwargs = {}
        kwargs['code'] = format_thesis_collection_code(self.repository.code)
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['publication_year'] = self.kwargs.get(self.year_url_kwarg)
        context['other_publication_years'] = list(year_counts(self.summary))
        return context

    def get_extra_theses_kwargs(self):
        return {'year': self.kwargs.get(self.year_url_kwarg)}


@method_decorator(cache_page(settings.SHORT_TTL), name='dispatch')
class ThesisPublicationAuthorNameListView(FallbackObjectViewMixin, BaseThesisListView):
    """ Displays theses for a specific year. """
    template_name = 'public/thesis/collection_list_per_author_name.html'
    letter_url_kwarg = 'author_letter'
    fallback_url_format = '/these/liste.html'

    def get_fallback_querystring_dict(self):
        querystring_dict = super().get_fallback_querystring_dict()
        querystring_dict['src'] = format_thesis_collection_code(self.repository.code)
        querystring_dict['lettre'] = self.kwargs.get(self.letter_url_kwarg).upper()
        return querystring_dict

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['author_letter'] = self.kwargs.get(self.letter_url_kwarg).upper()
        context['other_author_letters'] = first_letter_counts(self.summary)
        return context

    def get_extra_theses_kwargs(self):
        return {'author_letter': self.kwargs.get(self.letter_url_kwarg)}


class BaseThesisCitationView(TemplateView):
    def get_context_data(self, **kwargs):
        result = super().get_context_data(**kwargs)
        try:
            result['thesis'] = SolrDocument.from_solr_id(self.kwargs['solr_id'])
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
