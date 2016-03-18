# -*- coding: utf-8 -*-

from django.conf import settings
from django.core.urlresolvers import reverse
from django.utils.translation import get_language
from django.utils.translation import ugettext_lazy as _
from django.views.generic import UpdateView
from rules.contrib.views import PermissionRequiredMixin

from base.viewmixins import LoginRequiredMixin
from base.viewmixins import MenuItemMixin
from erudit.models import JournalInformation

from ..viewmixins import JournalScopeMixin

from .forms import JournalInformationForm


class JournalInformationUpdateView(
        LoginRequiredMixin, JournalScopeMixin, MenuItemMixin, PermissionRequiredMixin, UpdateView):
    """
    Displays a form to update journal information. JournalInformation instances
    can hold information in many languages. The language used to save the values
    provided by the form can be controlled using a GET parameter whose name is
    defined using the `lang_get_parameter` attribute.
    """
    context_object_name = 'journal'
    form_class = JournalInformationForm
    lang_get_parameter = 'lang'
    menu_journal = 'information'
    model = JournalInformation
    permission_required = 'journal.edit_journal'
    raise_exception = True
    template_name = 'userspace/journal/information/journalinformation_update.html'

    def get_title(self):
        return _("Éditer une revue")

    @property
    def selected_language(self):
        languages = [l[0] for l in settings.LANGUAGES]
        get_lang = self.request.GET.get(self.lang_get_parameter, None)
        return get_lang if get_lang in languages else get_language()

    def get_object(self):
        journal = self.current_journal
        journal_info, dummy = JournalInformation.objects.get_or_create(journal=journal)
        return journal_info

    def get_permission_object(self):
        # Note: we work on a JournalInformation instance but the permission check
        # is performed against a Journal instance.
        return self.current_journal

    def get_form_kwargs(self):
        kwargs = super(JournalInformationUpdateView, self).get_form_kwargs()
        kwargs['language_code'] = self.selected_language
        return kwargs

    def get_context_data(self, **kwargs):
        context = super(JournalInformationUpdateView, self).get_context_data(**kwargs)
        context['selected_language'] = self.selected_language
        return context

    def get_success_url(self):
        return '{url}?{lang_get_parameter}={lang_value}'.format(
            url=reverse('userspace:journal:information:update',
                        kwargs={'journal_pk': self.current_journal.pk}),
            lang_get_parameter=self.lang_get_parameter, lang_value=self.selected_language)
