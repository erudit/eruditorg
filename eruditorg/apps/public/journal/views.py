# -*- coding: utf-8 -*-

from collections import OrderedDict
from itertools import groupby
from string import ascii_lowercase

from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.template import RequestContext
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import ensure_csrf_cookie
from django.utils.functional import cached_property
from django.views.generic import DetailView
from django.views.generic import ListView
from django.views.generic import TemplateView
from eruditarticle.objects import EruditArticle
from PyPDF2 import PdfFileMerger
from rules.contrib.views import PermissionRequiredMixin

from base.pdf import generate_pdf
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

from .viewmixins import ArticleViewMetricCaptureMixin
from .viewmixins import SingleArticleMixin


class JournalListView(ListView):
    """
    Displays a list of Journal instances.
    """
    context_object_name = 'journals'
    model = Journal
    template_name = 'public/journal/journal_list.html'

    def apply_sorting(self, objects):
        if self.sorting == 'name':
            grouped = groupby(
                sorted(objects, key=lambda j: j.letter_prefix), key=lambda j: j.letter_prefix)
            first_pass_results = [{'key': g[0], 'name': g[0], 'objects': sorted(
                list(g[1]), key=lambda j: j.sortable_name)} for g in grouped]
        elif self.sorting == 'disciplines':
            disciplines = Discipline.objects.all().order_by('name')
            first_pass_results = [{'key': d.code, 'name': d.name, 'objects': sorted(
                d.journals.all(), key=lambda j: j.sortable_name)} for d in disciplines]

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
        return super(JournalListView, self).get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(JournalListView, self).get_context_data(**kwargs)
        context['sorting'] = self.sorting
        context['sorted_objects'] = self.apply_sorting(context.get(self.context_object_name))
        context['disciplines'] = Discipline.objects.all().order_by('name')
        return context

    def get_queryset(self):
        qs = super(JournalListView, self).get_queryset()
        return qs.select_related('collection')


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
            self.letter = str(self.letter).lower()
            assert len(self.letter) == 1 and 'a' <= self.letter <= 'z'
        except AssertionError:
            self.letter = None

    def get_base_queryset(self):
        """ Returns the base queryset that will be used to retrieve the authors. """
        return Author.objects.prefetch_related('article_set') \
            .filter(article__issue__journal_id=self.journal.id).order_by('lastname') \
            .distinct()

    def get_letters_queryset_dict(self):
        """ Returns an ordered dict containing an Author queryset for each letter. """
        qs = self.get_base_queryset()

        letter_qsdict = OrderedDict()
        for letter in ascii_lowercase:
            letter_qsdict[letter] = qs.filter(lastname__istartswith=letter)

        return letter_qsdict

    def get_queryset(self):
        qs = self.get_base_queryset()
        qsdict = self.get_letters_queryset_dict()

        if self.letter is None:
            first_author = qs.first()
            self.letter = first_author.lastname[0].lower() if first_author else 'a'

        return qsdict[self.letter]

    @cached_property
    def letters_counts(self):
        """ Returns an ordered dict containing the number of authors for each letter. """
        qsdict = self.get_letters_queryset_dict()
        letters_counts = OrderedDict()
        for letter, qs in qsdict.items():
            letters_counts[letter] = qs.count()
        return letters_counts

    def get_context_data(self, **kwargs):
        context = super(JournalAuthorsListView, self).get_context_data(**kwargs)
        context['journal'] = self.journal
        context['letter'] = self.letter
        context['letters_counts'] = self.letters_counts
        return context


class JournalRawLogoView(SingleJournalMixin, FedoraFileDatastreamView):
    """
    Returns the image file associated with a Journal instance.
    """
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
        context['articles'] = Article.objects \
            .select_related('issue', 'issue__journal', 'issue__journal__collection') \
            .prefetch_related('authors') \
            .filter(issue=self.object)
        return context


class IssueRawCoverpageView(FedoraFileDatastreamView):
    """
    Returns the image file associated with an Issue instance.
    """
    content_type = 'image/jpeg'
    datastream_name = 'coverpage'
    fedora_object_class = PublicationDigitalObject
    model = Issue


class ArticleDetailView(
        FedoraServiceRequiredMixin, ArticleAccessCheckMixin, SingleArticleMixin,
        ArticleViewMetricCaptureMixin, DetailView):
    """
    Displays an Article page.
    """
    context_object_name = 'article'
    model = Article
    template_name = 'public/journal/article_detail.html'
    tracking_view_type = 'html'

    def get_context_data(self, **kwargs):
        context = super(ArticleDetailView, self).get_context_data(**kwargs)
        obj = context.get(self.context_object_name)

        # Get all article from associated Issue
        related_articles = Article.objects.select_related('issue', 'issue__journal') \
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
        return super(ArticleDetailView, self).dispatch(*args, **kwargs)


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


class ArticlePdfView(FedoraServiceRequiredMixin, TemplateView):
    """
    Displays a page allowing to browse the PDF file associated with an article.
    """
    template_name = 'public/journal/article_pdf.html'

    def get_context_data(self, **kwargs):
        context = super(ArticlePdfView, self).get_context_data(**kwargs)
        context['journal_id'] = self.kwargs['journalid']
        context['issue_id'] = self.kwargs['issueid']
        context['article_id'] = self.kwargs['articleid']
        return context


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
        return get_object_or_404(Article, localidentifier=self.kwargs['articleid'])

    def get_fedora_object_pid(self):
        article = self.get_article()
        return article.pid

    def get_response_object(self, fedora_object):
        response = super(ArticleRawPdfView, self).get_response_object(fedora_object)
        response['Content-Disposition'] = 'attachment; filename={}.pdf'.format(
            self.kwargs['articleid'])
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


class ArticleMediaView(SingleArticleMixin, FedoraFileDatastreamView):
    """
    Returns an image file embedded in the INFOIMG datastream.
    """
    datastream_name = 'content'
    fedora_object_class = MediaDigitalObject

    def get_fedora_object_pid(self):
        article = get_object_or_404(Article, localidentifier=self.kwargs['articleid'])
        issue_pid = article.issue.pid
        return '{0}.{1}'.format(issue_pid, self.kwargs['localidentifier'])

    def get_content_type(self, fedora_object):
        return fedora_object.content.mimetype
