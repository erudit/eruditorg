# -*- coding: utf-8 -*-

from django.conf import settings
from django.core.exceptions import PermissionDenied
from django.core.urlresolvers import reverse
from django.http import Http404
from django.http import HttpResponse
from django.template import RequestContext
from django.utils.translation import get_language
from django.utils.translation import ugettext_lazy as _
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

from .forms import JournalInformationForm
from .models import JournalInformation
from .rules_helpers import get_editable_journals
from .viewmixins import JournalCodeDetailMixin, JournalBreadcrumbsMixin


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
            return reverse('journal:journal-information-list')
        elif journal_count:
            return reverse(
                'journal:journal-information-update', kwargs={'code': journal_qs.first().code})
        else:
            # No Journal instance can be edited
            raise PermissionDenied


class JournalInformationListView(JournalBreadcrumbsMixin, ListView):
    """
    Displays a list of Journal instances whose information can be edited by
    the current user.
    """
    context_object_name = 'journals'
    model = Journal
    paginate_by = 36
    template_name = 'journal_information_list.html'

    def get_queryset(self):
        qs = get_editable_journals(self.request.user)
        return qs.order_by('name')


class JournalInformationUpdateView(JournalBreadcrumbsMixin,
                                   PermissionRequiredMixin,
                                   JournalCodeDetailMixin,
                                   UpdateView):
    """
    Displays a form to update journal information. JournalInformation instances
    can hold information in many languages. The language used to save the values
    provided by the form can be controlled using a GET parameter whose name is
    defined using the `lang_get_parameter` attribute.
    """
    context_object_name = 'journal'
    form_class = JournalInformationForm
    lang_get_parameter = 'lang'
    model = JournalInformation
    permission_required = ['journal.edit_journal', ]
    raise_exception = True
    template_name = 'journal_information_update.html'

    def get_title(self):
        return _("Éditer une revue")

    @property
    def selected_language(self):
        languages = [l[0] for l in settings.LANGUAGES]
        get_lang = self.request.GET.get(self.lang_get_parameter, None)
        return get_lang if get_lang in languages else get_language()

    def get_object(self):
        journal = self.get_journal()
        journal_info, dummy = JournalInformation.objects.get_or_create(journal=journal)
        return journal_info

    def get_permission_object(self):
        # Note: we work on a JournalInformation instance but the permission check
        # is performed against a Journal instance.
        return self.get_object().journal

    def get_form_kwargs(self):
        kwargs = super(JournalInformationUpdateView, self).get_form_kwargs()
        kwargs['language_code'] = self.selected_language
        return kwargs

    def get_context_data(self, **kwargs):
        context = super(JournalInformationUpdateView, self).get_context_data(**kwargs)
        context['journal_code'] = self.kwargs['code']
        context['selected_language'] = self.selected_language
        return context

    def get_success_url(self):
        return '{url}?{lang_get_parameter}={lang_value}'.format(
            url=reverse('journal:journal-information-update', kwargs={'code': self.kwargs['code']}),
            lang_get_parameter=self.lang_get_parameter, lang_value=self.selected_language)


class JournalDetailView(JournalCodeDetailMixin, DetailView):
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
