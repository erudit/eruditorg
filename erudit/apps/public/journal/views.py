# -*- coding: utf-8 -*-

from collections import OrderedDict
from string import ascii_lowercase

from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import get_object_or_404
from django.template import RequestContext
from django.utils.functional import cached_property
from django.views.generic import DetailView
from django.views.generic import ListView
from django.views.generic import TemplateView
from eruditarticle.objects import EruditArticle
from PyPDF2 import PdfFileMerger

from base.viewmixins import FedoraServiceRequiredMixin
from core.journal.viewmixins import ArticleAccessCheckMixin
from core.journal.viewmixins import JournalCodeDetailMixin
from erudit.fedora.objects import ArticleDigitalObject
from erudit.fedora.objects import JournalDigitalObject
from erudit.fedora.objects import PublicationDigitalObject
from erudit.fedora.views.generic import FedoraFileDatastreamView
from erudit.models import Discipline
from erudit.models import Article
from erudit.models import Author
from erudit.models import Journal
from erudit.models import Issue
from erudit.utils.pdf import generate_pdf


class JournalListView(ListView):
    """
    Displays a list of Journal instances.
    """
    context_object_name = 'journals'
    model = Journal
    template_name = 'public/journal/journal_list.html'

    def get(self, request, *args, **kwargs):
        self.init_get_parameters(request)
        return super(JournalListView, self).get(request, *args, **kwargs)

    def init_get_parameters(self, request):
        """ Initializes GET parameters. """
        # default sorting is by name
        self.sorting = request.GET.get('sorting', 'name')
        self.sorting_template = "public/journal/_journal_list_sort_%s.html" % self.sorting

    def get_context_data(self, **kwargs):
        context = super(JournalListView, self).get_context_data(**kwargs)

        context['disciplines'] = Discipline.objects.all().order_by('name')
        context['sorting_template'] = self.sorting_template

        return context


class JournalDetailView(FedoraServiceRequiredMixin, JournalCodeDetailMixin, DetailView):
    """
    Displays a journal.
    """
    context_object_name = 'journal'
    model = Journal
    template_name = 'public/journal/journal_detail.html'

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


class JournalAuthorsListView(JournalCodeDetailMixin, ListView):
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


class JournalRawLogoView(JournalCodeDetailMixin, FedoraFileDatastreamView):
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

        return get_object_or_404(Issue, localidentifier=self.kwargs['localidentifier'])

    def get_context_data(self, **kwargs):
        context = super(IssueDetailView, self).get_context_data(**kwargs)

        context['journal'] = self.get_object().journal
        context['articles'] = Article.objects.filter(issue=self.get_object())
        return context


class IssueRawCoverpageView(FedoraFileDatastreamView):
    """
    Returns the image file associated with an Issue instance.
    """
    content_type = 'image/jpeg'
    datastream_name = 'coverpage'
    fedora_object_class = PublicationDigitalObject
    model = Issue


class ArticleDetailView(FedoraServiceRequiredMixin, ArticleAccessCheckMixin, DetailView):
    """
    Displays an Article page.
    """
    context_object_name = 'article'
    model = Article
    template_name = 'public/journal/article_detail.html'

    def get_object(self, queryset=None):
        if 'pk' in self.kwargs:
            return super(ArticleDetailView, self).get_object(queryset)

        return get_object_or_404(Article, localidentifier=self.kwargs['localid'])

    def get_context_data(self, **kwargs):
        context = super(ArticleDetailView, self).get_context_data(**kwargs)

        # Get all article from associated Issue
        related_articles = Article.objects.all().filter(issue=self.get_object().issue)

        # return 4 randomly
        context['related_articles'] = related_articles.order_by('?')[:4]

        return context


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


class ArticleRawPdfView(FedoraFileDatastreamView):
    """
    Returns the PDF file associated with an article.
    """
    content_type = 'application/pdf'
    datastream_name = 'pdf'
    fedora_object_class = ArticleDigitalObject

    def get_fedora_object_pid(self):
        article = get_object_or_404(Article, localidentifier=self.kwargs['articleid'])
        return article.pid

    def get_response_object(self):
        response = super(ArticleRawPdfView, self).get_response_object()
        response['Content-Disposition'] = 'attachment; filename={}.pdf'.format(
            self.kwargs['articleid'])
        return response

    def write_datastream_content(self, response, content):
        # We are going to put a generated coverpage at the beginning of our PDF
        xml_content = self.fedora_object.xml_content
        coverpage_context = {
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
