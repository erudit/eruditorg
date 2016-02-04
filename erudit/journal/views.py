# -*- coding: utf-8 -*-

from django.http import Http404
from django.http import HttpResponse
from django.views.generic import DetailView
from django.views.generic import TemplateView
from django.views.generic import View
from eulfedora.util import RequestFailed
from requests.exceptions import ConnectionError

from erudit.fedora.conf import settings as fedora_settings
from erudit.fedora.objects import ArticleDigitalObject
from erudit.fedora.repository import api
from erudit.models import Journal


class JournalDetailView(DetailView):
    model = Journal
    context_object_name = 'journal'
    template_name = 'journal_detail.html'

    def get_object(self):
        try:
            return Journal.objects.get(code=self.kwargs['code'])
        except Journal.DoesNotExist:
            raise Http404


class ArticlePdfView(TemplateView):
    template_name = 'article_pdf.html'

    def get_context_data(self, **kwargs):
        context = super(ArticlePdfView, self).get_context_data(**kwargs)
        context['journal_id'] = self.kwargs['journalid']
        context['issue_id'] = self.kwargs['issueid']
        context['article_id'] = self.kwargs['articleid']
        return context


class ArticleRawPdfView(View):
    def get(self, request, journalid, issueid, articleid):
        full_pid = fedora_settings.PID_PREFIX + '.'.join([journalid, issueid, articleid])
        fedora_article = ArticleDigitalObject(api, full_pid)

        try:
            pdf_content = fedora_article.pdf.content
        except (RequestFailed, ConnectionError):
            raise Http404

        response = HttpResponse(pdf_content, content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename={}.pdf'.format(articleid)

        return response
