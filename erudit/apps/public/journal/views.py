# -*- coding: utf-8 -*-

from django.core.exceptions import ObjectDoesNotExist
from django.http import Http404
from django.http import HttpResponse
from django.template import RequestContext
from django.views.generic import DetailView
from django.views.generic import TemplateView
from django.views.generic import View
from eulfedora.util import RequestFailed
from eruditarticle.objects import EruditArticle
from PyPDF2 import PdfFileMerger
from requests.exceptions import ConnectionError

from core.journal.viewmixins import JournalCodeDetailMixin
from erudit.fedora.conf import settings as fedora_settings
from erudit.fedora.objects import ArticleDigitalObject
from erudit.fedora.repository import api
from erudit.models import Journal
from erudit.utils.pdf import generate_pdf


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

        return context


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


class ArticleRawPdfView(View):
    """
    Returns the PDF file associated with an article.
    """
    def get(self, request, journalid, issueid, articleid):
        full_pid = fedora_settings.PID_PREFIX + '.'.join([journalid, issueid, articleid])
        fedora_article = ArticleDigitalObject(api, full_pid)

        # Fetches the PDF content of the article
        try:
            pdf_content = fedora_article.pdf.content
        except (RequestFailed, ConnectionError):
            raise Http404

        # Prepares the response ; a PDF object
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename={}.pdf'.format(articleid)

        # Generates the cover page
        coverpage_context = {
            'fedora_article': fedora_article,
            'fedora_object': EruditArticle(fedora_article.xml_content),
        }
        coverpage = generate_pdf(
            'public/journal/article_pdf_coverpage.html',
            context=RequestContext(request).update(coverpage_context),
            base_url=request.build_absolute_uri('/'))

        # Merges the cover page and the full article
        merger = PdfFileMerger()
        merger.append(coverpage)
        merger.append(pdf_content)
        merger.write(response)
        merger.close()

        return response
