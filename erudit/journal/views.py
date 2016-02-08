# -*- coding: utf-8 -*-

from django.core.exceptions import PermissionDenied
from django.core.urlresolvers import reverse
from django.http import Http404
from django.http import HttpResponse
from django.template import RequestContext
from django.views.generic import DetailView
from django.views.generic import ListView
from django.views.generic import RedirectView
from django.views.generic import TemplateView
from django.views.generic import UpdateView
from django.views.generic import View
from eulfedora.util import RequestFailed
from eruditarticle.objects import EruditArticle
from PyPDF2 import PdfFileMerger
from requests.exceptions import ConnectionError
from rules.contrib.views import PermissionRequiredMixin

from erudit.fedora.conf import settings as fedora_settings
from erudit.fedora.objects import ArticleDigitalObject
from erudit.fedora.repository import api
from erudit.models import Journal
from erudit.utils.pdf import generate_pdf

from .rules_helpers import get_editable_journals
from .viewmixins import JournalDetailMixin


class JournalInformationDispatchView(RedirectView):
    """
    Redirects the user either to a list of Journal instances if he can edit
    many journals or to an update view of the considered journal.
    If the user cannot edit any journal, a permission denied error is returned.
    """
    permanent = False

    def get_redirect_url(self, *args, **kwargs):
        journal_qs = get_editable_journals(self.request.user)
        journal_count = journal_qs.count()
        if journal_count > 1:
            return reverse('journal:journal-list')
        elif journal_count:
            return reverse(
                'journal:journal-update', kwargs={'code': journal_qs.first().code})
        else:
            # No Journal instance can be edited
            raise PermissionDenied


class JournalListView(ListView):
    """
    Displays a list of Journal instances.
    """
    model = Journal
    template_name = 'journal_list.html'
    # TODO


class JournalUpdateView(PermissionRequiredMixin, JournalDetailMixin, UpdateView):
    """
    Displays a for; to update journal information.
    """
    context_object_name = 'journal'
    fields = []
    model = Journal
    permission_required = ['journal.edit_journal', ]
    template_name = 'journal_update.html'
    # TODO


class JournalDetailView(JournalDetailMixin, DetailView):
    """
    Displays a journal.
    """
    context_object_name = 'journal'
    model = Journal
    template_name = 'journal_detail.html'


class ArticlePdfView(TemplateView):
    """
    Displays a page allowing to browse the PDF file associated with an article.
    """
    template_name = 'article_pdf.html'

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
            'article_pdf_coverpage.html', context=RequestContext(request).update(coverpage_context),
            base_url=request.build_absolute_uri('/'))

        # Merges the cover page and the full article
        merger = PdfFileMerger()
        merger.append(coverpage)
        merger.append(pdf_content)
        merger.write(response)
        merger.close()

        return response
