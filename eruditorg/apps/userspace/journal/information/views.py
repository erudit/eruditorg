from django.conf import settings
from django.urls import reverse
from django.utils.translation import get_language
from django.utils.translation import ugettext_lazy as _
from django.views.generic import UpdateView, DeleteView
from django.http import HttpResponseRedirect

from base.viewmixins import MenuItemMixin
from erudit.models import JournalInformation, Contributor

from ..viewmixins import JournalScopePermissionRequiredMixin

from .forms import JournalInformationForm, ContributorInlineFormset


class JournalInformationCollaboratorDeleteView(DeleteView):

    def get_object(self):
        if 'contributor_id' not in self.request.POST:
            raise ValueError
        contributor_id = self.request.POST.get('contributor_id')
        contributor = Contributor.objects.get(pk=contributor_id)
        journal = contributor.journal_information.journal
        if not self.request.user.has_perm('journal.edit_journal_information', journal):
            raise PermissionError
        return contributor

    def get_success_url(self):
        return "/"


class JournalInformationUpdateView(
        JournalScopePermissionRequiredMixin, MenuItemMixin, UpdateView):
    """
    Displays a form to update journal information. JournalInformation instances
    can hold information in many languages. The language used to save the values
    provided by the form can be controlled using a GET parameter whose name is
    defined using the `lang_get_parameter` attribute.
    """
    context_object_name = 'journal_info'
    form_class = JournalInformationForm
    lang_get_parameter = 'lang'
    menu_journal = 'information'
    model = JournalInformation
    permission_required = 'journal.edit_journal_information'
    raise_exception = True
    template_name = 'userspace/journal/information/journalinformation_update.html'

    def get_title(self):
        return _("À propos")

    @property
    def selected_language(self):
        languages = [l[0] for l in settings.LANGUAGES]
        get_lang = self.request.GET.get(self.lang_get_parameter, None)
        return get_lang if get_lang in languages else get_language()

    def get_object(self):
        journal = self.current_journal
        journal_info, dummy = JournalInformation.objects.get_or_create(journal=journal)
        return journal_info

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        contributor_inline_form = ContributorInlineFormset(self.request.POST, instance=self.object)
        if form.is_valid() and contributor_inline_form.is_valid():
            return self.form_valid(form, contributor_inline_form)
        return self.form_invalid(form, contributor_inline_form)

    def form_invalid(self, form, contributor_form):

        return self.render_to_response(self.get_context_data(form=form, formset=contributor_form))

    def form_valid(self, form, contributor_form):
        self.object = form.save()
        contributor_form.instance = self.object
        contributor_form.save()
        return HttpResponseRedirect(self.get_success_url())

    def get_permission_object(self):
        # Note: we work on a JournalInformation instance but the permission check
        # is performed against a Journal instance.
        return self.current_journal

    def get_form_kwargs(self):
        kwargs = super(JournalInformationUpdateView, self).get_form_kwargs()
        kwargs['language_code'] = self.selected_language
        kwargs['request'] = self.request
        return kwargs

    def get_context_data(self, **kwargs):
        context = super(JournalInformationUpdateView, self).get_context_data(**kwargs)
        context['selected_language'] = self.selected_language
        if 'formset' in kwargs:
            context['formset'] = kwargs['formset']
        else:
            context['formset'] = ContributorInlineFormset(instance=self.object)
        return context

    def get_success_url(self):
        return '{url}?{lang_get_parameter}={lang_value}'.format(
            url=reverse('userspace:journal:information:update',
                        kwargs={'journal_pk': self.current_journal.pk}),
            lang_get_parameter=self.lang_get_parameter, lang_value=self.selected_language)
