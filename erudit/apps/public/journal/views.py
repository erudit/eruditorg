# -*- coding: utf-8 -*-

from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import get_object_or_404
from django.template import RequestContext
from django.views.generic import DetailView
from django.views.generic import ListView
from django.views.generic import TemplateView
from eruditarticle.objects import EruditArticle
from PyPDF2 import PdfFileMerger

from core.journal.viewmixins import JournalCodeDetailMixin
from erudit.fedora.conf import settings as fedora_settings
from erudit.fedora.objects import ArticleDigitalObject
from erudit.fedora.objects import JournalDigitalObject
from erudit.fedora.objects import PublicationDigitalObject
from erudit.fedora.views.generic import FedoraFileDatastreamView
from erudit.models import Journal
from erudit.models import Issue
from erudit.models import Article
from erudit.utils.pdf import generate_pdf


class JournalListView(ListView):
    """
    Displays a list of Journal instances.
    """
    context_object_name = 'journals'
    model = Journal
    template_name = 'public/journal/journal_list.html'


class JournalDetailView(JournalCodeDetailMixin, DetailView):
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


class JournalRawLogoView(JournalCodeDetailMixin, FedoraFileDatastreamView):
    """
    Returns the image file associated with a Journal instance.
    """
    content_type = 'image/jpeg'
    datastream_name = 'logo'
    fedora_object_class = JournalDigitalObject
    model = Journal


class IssueDetailView(DetailView):
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


class ArticlePdfView(TemplateView):
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
        return fedora_settings.PID_PREFIX + '.'.join(
            [self.kwargs['journalid'], self.kwargs['issueid'], self.kwargs['articleid']])

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
