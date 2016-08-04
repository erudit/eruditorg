# -*- coding: utf-8 -*-

from collections import OrderedDict
from functools import reduce
from itertools import groupby
from string import ascii_lowercase

from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import reverse
from django.db.models import Q
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.template import RequestContext
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import ensure_csrf_cookie
from django.utils.functional import cached_property
from django.views.generic import DetailView
from django.views.generic import ListView
from django.views.generic import RedirectView
from django.views.generic import TemplateView
from eruditarticle.objects import EruditArticle
from PyPDF2 import PdfFileMerger
from PyPDF2 import PdfFileReader
from PyPDF2 import PdfFileWriter
from rules.contrib.views import PermissionRequiredMixin

from base.pdf import generate_pdf
from base.viewmixins import CacheMixin
from base.viewmixins import FedoraServiceRequiredMixin
from core.journal.viewmixins import ArticleAccessCheckMixin
from core.journal.viewmixins import SingleJournalMixin
from core.metrics.metric import metric
from erudit.fedora.objects import ArticleDigitalObject
from erudit.fedora.objects import JournalDigitalObject
from erudit.fedora.objects import MediaDigitalObject
from erudit.fedora.objects import PublicationDigitalObject
from erudit.fedora.views.generic import FedoraFileDatastreamView
from erudit.models import Discipline
from erudit.models import Article
from erudit.models import Author
from erudit.models import Journal
from erudit.models import Issue

from .forms import JournalListFilterForm
from .viewmixins import ArticleViewMetricCaptureMixin
from .viewmixins import SingleArticleMixin


class JournalListView(ListView):
    """
    Displays a list of Journal instances.
    """
    context_object_name = 'journals'
    filter_form_class = JournalListFilterForm
    model = Journal

    def apply_sorting(self, objects):
        if self.sorting == 'name':
            grouped = groupby(
                sorted(objects, key=lambda j: j.letter_prefix), key=lambda j: j.letter_prefix)
            first_pass_results = [{'key': g[0], 'name': g[0], 'objects': sorted(
                list(g[1]), key=lambda j: j.sortable_name)} for g in grouped]
            return first_pass_results
        elif self.sorting == 'disciplines':
            objects = objects.prefetch_related('disciplines')
            _disciplines_dict = {}
            for o in objects:
                for d in o.disciplines.all():
                    if d not in _disciplines_dict:
                        _disciplines_dict[d] = []
                    _disciplines_dict[d].append(o)

            first_pass_results = [{'key': d.code, 'name': d.name, 'objects': sorted(
                _disciplines_dict[d], key=lambda j: j.sortable_name)}
                for d in sorted(_disciplines_dict, key=lambda i: i.name)]

        # Only for "disciplines" sorting
        second_pass_results = []
        for r in first_pass_results:
            grouped = groupby(
                sorted(r['objects'], key=lambda j: j.collection_id), key=lambda j: j.collection)
            del r['objects']
            r['collections'] = [{'key': g[0], 'objects': sorted(
                list(g[1]), key=lambda j: j.sortable_name)} for g in grouped]
            second_pass_results.append(r)

        return second_pass_results

    def get(self, request, *args, **kwargs):
        sorting = self.request.GET.get('sorting', 'name')
        self.sorting = sorting if sorting in ['name', 'disciplines', ] else 'name'
        self.filter_form = self.get_filter_form()
        self.filter_form.is_valid()
        self.object_list = self.get_queryset()
        context = self.get_context_data(filter_form=self.filter_form)
        return self.render_to_response(context)

    def get_context_data(self, **kwargs):
        context = super(JournalListView, self).get_context_data(**kwargs)
        context['sorting'] = self.sorting
        context['sorted_objects'] = self.apply_sorting(context.get(self.context_object_name))
        context['disciplines'] = Discipline.objects.all().order_by('name')
        return context

    def get_filter_form(self):
        """ Returns an instance of the filter form to be used in this view. """
        return self.filter_form_class(**self.get_filter_form_kwargs())

    def get_filter_form_kwargs(self):
        """ Returns the keyword arguments for instantiating the search form. """
        form_kwargs = {}

        if self.request.method == 'GET':
            form_kwargs.update({'data': self.request.GET, })
        return form_kwargs

    def get_queryset(self):
        qs = super(JournalListView, self).get_queryset()
        qs = qs.select_related('collection', 'type')

        # Filter the queryset
        if self.filter_form.is_valid():
            if self.filter_form.cleaned_data['open_access']:
                qs = qs.filter(open_access=True)
            if self.filter_form.cleaned_data['types']:
                qs = qs.filter(reduce(
                    lambda q, jtype: q | Q(type__code=jtype),
                    self.filter_form.cleaned_data['types'], Q()))
            if self.filter_form.cleaned_data['collections']:
                qs = qs.filter(reduce(
                    lambda q, collection: q | Q(collection__code=collection),
                    self.filter_form.cleaned_data['collections'], Q()))

        return qs.select_related('collection')

    def get_template_names(self):
        if self.sorting == 'name':
            return ['public/journal/journal_list_per_names.html', ]
        elif self.sorting == 'disciplines':
            return ['public/journal/journal_list_per_disciplines.html', ]


class JournalDetailView(FedoraServiceRequiredMixin, SingleJournalMixin, DetailView):
    """
    Displays a journal.
    """
    context_object_name = 'journal'
    model = Journal
    template_name = 'public/journal/journal_detail.html'

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        if self.object.url and not self.object.issues.count():
            # Tracks the redirection
            metric(
                'erudit__journal__journal_redirect',
                tags={'collection': self.object.collection.code, }, **{'code': self.object.code, })
            return HttpResponseRedirect(self.object.url)

        context = self.get_context_data(object=self.object)
        return self.render_to_response(context)

    def get_context_data(self, **kwargs):
        context = super(JournalDetailView, self).get_context_data(**kwargs)

        # Fetches the JournalInformation instance associated to the current journal
        try:
            journal_info = self.object.information
        except ObjectDoesNotExist:
            pass
        else:
            context['journal_info'] = journal_info

        # Fetches the published issues and the latest issue associated with the current journal
        context['issues'] = self.object.published_issues.order_by('-date_published')
        context['latest_issue'] = self.object.last_issue

        return context


class JournalAuthorsListView(SingleJournalMixin, ListView):
    """
    Displays a list of authors associated with a specific journal.
    """
    context_object_name = 'authors'
    model = Author
    template_name = 'public/journal/journal_authors_list.html'

    def get(self, request, *args, **kwargs):
        self.init_get_parameters(request)
        return super(JournalAuthorsListView, self).get(request, *args, **kwargs)

    def init_get_parameters(self, request):
        """ Initializes and verify GET parameters. """
        self.letter = request.GET.get('letter', None)
        try:
            assert self.letter is not None
            self.letter = str(self.letter).upper()
            assert len(self.letter) == 1 and 'A' <= self.letter <= 'Z'
        except AssertionError:
            self.letter = None

    def get_base_queryset(self):
        """ Returns the base queryset that will be used to retrieve the authors. """
        return Author.objects \
            .filter(lastname__isnull=False, article__issue__journal_id=self.journal.id) \
            .order_by('lastname').distinct()

    def get_letters_queryset_dict(self):
        """ Returns an ordered dict containing a list of authors for each letter. """
        qs = self.get_base_queryset()

        grouped = groupby(
            sorted(qs, key=lambda a: a.letter_prefix), key=lambda a: a.letter_prefix)
        letter_qsdict = OrderedDict([
            (g[0], sorted(list(g[1]), key=lambda a: a.lastname or a.othername)) for g in grouped])

        return letter_qsdict

    def get_queryset(self):
        qs = self.get_base_queryset()
        qsdict = self.get_letters_queryset_dict()

        if self.letter is None:
            first_author = qs.first()
            letter_prefix = first_author.letter_prefix if first_author else None
            self.letter = letter_prefix if letter_prefix else 'A'

        return qsdict[self.letter]

    @cached_property
    def letters_exists(self):
        """ Returns an ordered dict containing the number of authors for each letter. """
        qsdict = self.get_letters_queryset_dict()
        letters_exists = OrderedDict([(l.upper(), 0) for l in ascii_lowercase])
        for letter, qs in qsdict.items():
            letters_exists[letter] = len(qs)
        return letters_exists

    def get_context_data(self, **kwargs):
        context = super(JournalAuthorsListView, self).get_context_data(**kwargs)
        context['journal'] = self.journal
        context['letter'] = self.letter
        context['letters_exists'] = self.letters_exists
        return context


class JournalRawLogoView(CacheMixin, SingleJournalMixin, FedoraFileDatastreamView):
    """
    Returns the image file associated with a Journal instance.
    """
    cache_timeout = 60 * 60 * 24 * 15  # 15 days
    content_type = 'image/jpeg'
    datastream_name = 'logo'
    fedora_object_class = JournalDigitalObject
    model = Journal


class IssueDetailView(FedoraServiceRequiredMixin, DetailView):
    """
    Displays an Issue instance.
    """
    context_object_name = 'issue'
    model = Issue
    template_name = 'public/journal/issue_detail.html'

    def get_object(self, queryset=None):
        if 'pk' in self.kwargs:
            return super(IssueDetailView, self).get_object(queryset)

        return get_object_or_404(
            Issue.objects.select_related('journal', 'journal__collection').all(),
            localidentifier=self.kwargs['localidentifier'])

    def get_context_data(self, **kwargs):
        context = super(IssueDetailView, self).get_context_data(**kwargs)

        context['journal'] = self.object.journal

        articles = Article.objects \
            .select_related('issue', 'issue__journal', 'issue__journal__collection') \
            .prefetch_related('authors') \
            .filter(issue=self.object)

        try:
            articles = sorted(articles, key=lambda a: a.erudit_object.ordseq)
            # Groups the articles by section titles in order to generated the nested groups (which
            # will be generated by using the nested section titles).
            section1_grouped = groupby(articles, key=lambda a: a.erudit_object.section_title)
            sections1_tree = OrderedDict(((k[0], list(k[1])) for k in section1_grouped))
            context['articles_per_section'] = self._gen_sections_tree(sections1_tree)
        except AttributeError:  # pragma: no cover
            # This means that Fedora is unavailable
            pass

        context['articles'] = articles

        return context

    def _gen_sections_tree(self, sections_tree, current_level=1):
        if current_level > 3:
            # The Érudit articles cannot have nore than 3 nested sections. So we just stop here.
            return sections_tree

        # Iterates over the current dictionnary and generates the sub dictionnaries corresponding to
        # the nested sections (each sub section can contain a subset of the articles).
        for k, section_articles in sections_tree.items():
            sections_tree[k] = {
                'level': current_level,
                # We store here the titles (main and alternative titles) for convenience by using
                # liberuditarticle.
                'titles': getattr(
                    section_articles[0].erudit_object,
                    ('section_titles' if current_level == 1
                     else 'section_titles_' + str(current_level)))
            }
            if k is None or current_level >= 3:
                # If we do not have a section title, we juste stop here because this means that
                # there won't be nested sections to handle.
                sections_tree[k]['objects'] = section_articles
                continue
            else:
                # Otherwise we group the current articles by their nested section titles in orer to
                # generate the nested dictionnaries.
                sub_sections_grouped = groupby(
                    section_articles,
                    key=lambda a: getattr(
                        a.erudit_object, 'section_title_' + str(current_level + 1)))
                sub_sections_tree = OrderedDict(((k[0], list(k[1])) for k in sub_sections_grouped))
                if len(sub_sections_tree) == 1 and None in sub_sections_tree:
                    sections_tree[k]['objects'] = sub_sections_tree.pop(None)
                if len(sub_sections_tree):
                    sections_tree[k]['section' + str(current_level + 1)] = self._gen_sections_tree(
                        sub_sections_tree, current_level + 1)

        return sections_tree


class IssueRawCoverpageView(FedoraFileDatastreamView):
    """
    Returns the image file associated with an Issue instance.
    """
    content_type = 'image/jpeg'
    datastream_name = 'coverpage'
    fedora_object_class = PublicationDigitalObject
    model = Issue

    def get_object(self):
        return get_object_or_404(Issue, localidentifier=self.kwargs['localidentifier'])


class BaseArticleDetailView(
        FedoraServiceRequiredMixin, ArticleAccessCheckMixin, SingleArticleMixin,
        ArticleViewMetricCaptureMixin, DetailView):
    context_object_name = 'article'
    model = Article
    tracking_view_type = 'html'

    def get_context_data(self, **kwargs):
        context = super(BaseArticleDetailView, self).get_context_data(**kwargs)
        obj = context.get(self.context_object_name)

        # Get all article from associated Issue
        related_articles = Article.objects \
            .select_related('issue', 'issue__journal', 'issue__journal__collection') \
            .prefetch_related('authors').filter(issue=obj.issue)

        # Pick the previous article and the next article
        try:
            sorted_articles = list(sorted(related_articles, key=lambda a: a.erudit_object.ordseq))
            obj_index = sorted_articles.index(obj)
            previous_article = sorted_articles[obj_index - 1] if obj_index > 0 else None
            next_article = sorted_articles[obj_index + 1] if obj_index + 1 < len(sorted_articles) \
                else None
        except AttributeError:  # pragma: no cover
            # Passes the error if we are in DEBUG mode
            if not settings.DEBUG:
                raise
        else:
            context['previous_article'] = previous_article
            context['next_article'] = next_article

        # return 4 randomly
        context['related_articles'] = related_articles.order_by('?')[:4]

        return context

    @method_decorator(ensure_csrf_cookie)
    def dispatch(self, *args, **kwargs):
        return super(BaseArticleDetailView, self).dispatch(*args, **kwargs)


class ArticleDetailView(BaseArticleDetailView):
    """
    Displays an Article page.
    """
    template_name = 'public/journal/article_detail.html'


class ArticleSummaryView(BaseArticleDetailView):
    """
    Displays the summary of an Article instance.
    """
    template_name = 'public/journal/article_summary.html'


class IdEruditArticleRedirectView(RedirectView):
    pattern_name = 'public:journal:article_detail'

    def get_redirect_url(self, *args, **kwargs):
        article = get_object_or_404(
            Article.objects.select_related('issue', 'issue__journal'),
            localidentifier=kwargs['localid'])
        return reverse(self.pattern_name, args=[
            article.issue.journal.code, article.issue.volume_slug, article.issue.localidentifier,
            article.localidentifier, ])


class ArticleEnwCitationView(SingleArticleMixin, DetailView):
    """
    Returns the enw file of a specific article.
    """
    content_type = 'application/x-endnote-refer'
    model = Article
    template_name = 'public/journal/citation/article.enw'


class ArticleRisCitationView(SingleArticleMixin, DetailView):
    """
    Returns the ris file of a specific article.
    """
    content_type = 'application/x-research-info-systems'
    model = Article
    template_name = 'public/journal/citation/article.ris'


class ArticleBibCitationView(SingleArticleMixin, DetailView):
    """
    Returns the bib file of a specific article.
    """
    content_type = 'application/x-bibtex'
    model = Article
    template_name = 'public/journal/citation/article.bib'


class ArticleRawPdfView(
        ArticleViewMetricCaptureMixin, ArticleAccessCheckMixin, PermissionRequiredMixin,
        FedoraFileDatastreamView):
    """
    Returns the PDF file associated with an article.
    """
    content_type = 'application/pdf'
    datastream_name = 'pdf'
    fedora_object_class = ArticleDigitalObject
    raise_exception = True
    tracking_view_type = 'pdf'

    def get_article(self):
        return get_object_or_404(Article, localidentifier=self.kwargs['localid'])

    def get_fedora_object_pid(self):
        article = self.get_article()
        return article.pid

    def get_response_object(self, fedora_object):
        response = super(ArticleRawPdfView, self).get_response_object(fedora_object)
        if 'embed' not in self.request.GET:
            response['Content-Disposition'] = 'attachment; filename={}.pdf'.format(
                self.kwargs['localid'])
        return response

    def get_permission_object(self):
        return self.get_article()

    def has_permission(self):
        obj = self.get_permission_object()
        return obj.publication_allowed_by_authors and self.article_access_granted

    def write_datastream_content(self, response, content):
        # We are going to put a generated coverpage at the beginning of our PDF
        article = self.get_article()
        xml_content = self.fedora_object.xml_content
        coverpage_context = {
            'article': article,
            'issue': article.issue,
            'journal': article.issue.journal,
            'fedora_article': self.fedora_object,
            'erudit_article': EruditArticle(xml_content) if xml_content else None,
        }
        coverpage = generate_pdf(
            'public/journal/article_pdf_coverpage.html',
            context=RequestContext(self.request).update(coverpage_context),
            base_url=self.request.build_absolute_uri('/'))

        # Merges the cover page and the full article
        merger = PdfFileMerger()
        merger.append(coverpage)
        merger.append(content)
        merger.write(response)
        merger.close()


class ArticleRawPdfFirstPageView(PermissionRequiredMixin, FedoraFileDatastreamView):
    """
    Returns the PDF file associated with an article.
    """
    content_type = 'application/pdf'
    datastream_name = 'pdf'
    fedora_object_class = ArticleDigitalObject
    raise_exception = True
    tracking_view_type = 'pdf'

    def get_article(self):
        return get_object_or_404(Article, localidentifier=self.kwargs['localid'])

    def get_fedora_object_pid(self):
        article = self.get_article()
        return article.pid

    def get_response_object(self, fedora_object):
        response = super(ArticleRawPdfFirstPageView, self).get_response_object(fedora_object)
        if 'embed' not in self.request.GET:
            response['Content-Disposition'] = 'attachment; filename={}.pdf'.format(
                self.kwargs['localid'])
        return response

    def get_permission_object(self):
        return self.get_article()

    def has_permission(self):
        obj = self.get_permission_object()
        return obj.publication_allowed_by_authors

    def write_datastream_content(self, response, content):
        pdf_in = PdfFileReader(content)
        output = PdfFileWriter()
        output.addPage(pdf_in.getPage(0))
        output.write(response)


class ArticleMediaView(CacheMixin, SingleArticleMixin, FedoraFileDatastreamView):
    """
    Returns an image file embedded in the INFOIMG datastream.
    """
    cache_timeout = 60 * 60 * 24 * 15  # 15 days
    datastream_name = 'content'
    fedora_object_class = MediaDigitalObject

    def get_fedora_object_pid(self):
        article = get_object_or_404(Article, localidentifier=self.kwargs['localid'])
        issue_pid = article.issue.pid
        return '{0}.{1}'.format(issue_pid, self.kwargs['media_localid'])

    def get_content_type(self, fedora_object):
        return fedora_object.content.mimetype


class GoogleScholarSubscribersView(CacheMixin, TemplateView):
    cache_timeout = 60 * 60 * 24  # 24 hours
    content_type = 'text/xml'
    template_name = 'public/journal/scholar/subscribers.xml'


class GoogleScholarSubscriberJournalsView(CacheMixin, TemplateView):
    cache_timeout = 60 * 60 * 24  # 24 hours
    content_type = 'text/xml'
    template_name = 'public/journal/scholar/subscriber_journals.xml'

    def get_context_data(self, **kwargs):
        context = super(GoogleScholarSubscriberJournalsView, self).get_context_data(**kwargs)
        context['journals'] = Journal.objects.filter(collection__code='erudit', type__code='S')
        return context
