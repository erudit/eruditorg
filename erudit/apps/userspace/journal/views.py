# -*- coding: utf-8 -*-

from django.conf import settings
from django.core.exceptions import PermissionDenied
from django.core.urlresolvers import reverse
from django.utils.translation import get_language
from django.utils.translation import ugettext_lazy as _
from django.views.generic import ListView
from django.views.generic import RedirectView
from django.views.generic import UpdateView
from rules.contrib.views import PermissionRequiredMixin

from core.journal.rules_helpers import get_editable_journals
from core.journal.viewmixins import JournalCodeDetailMixin, JournalBreadcrumbsMixin
from erudit.models import Journal
from erudit.models import JournalInformation

from .forms import JournalInformationForm
from .rules_helpers import get_editable_journals


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
            return reverse('userspace:journal:journal-information-list')
        elif journal_count:
            return reverse(
                'userspace:journal:journal-information-update',
                kwargs={'code': journal_qs.first().code})
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
    template_name = 'userspace/journal/journal_information_list.html'

    def get_queryset(self):
        qs = get_editable_journals(self.request.user)
        return qs.order_by('name')


class JournalInformationUpdateView(JournalBreadcrumbsMixin, PermissionRequiredMixin, JournalCodeDetailMixin, UpdateView):
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
    template_name = 'userspace/journal/journal_information_update.html'

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
            url=reverse('userspace:journal:journal-information-update',
                        kwargs={'code': self.kwargs['code']}),
            lang_get_parameter=self.lang_get_parameter, lang_value=self.selected_language)
