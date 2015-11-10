import datetime

from django.template.context_processors import csrf
from django.views.generic.edit import CreateView, UpdateView
from django.contrib.auth.decorators import login_required

from erudit.models import Journal
from editor.models import JournalSubmission
from editor.forms import JournalSubmissionForm


class LoginRequiredMixin(object):

    @classmethod
    def as_view(cls, **initkwargs):
        view = super().as_view(**initkwargs)
        return login_required(view)


class JournalSubmissionCreate(LoginRequiredMixin, CreateView):
    model = JournalSubmission
    form_class = JournalSubmissionForm
    template_name = 'form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(csrf(self.request))
        return context

    def get_form(self, form_class):
        form = super().get_form(form_class)
        form.fields['journal'].queryset = Journal.objects.all()
        form.fields['journal'].initial = form.fields['journal'].queryset.first()
        form.fields['contact'].initial = form.fields['contact'].queryset.first()
        form.fields['date_created'].initial = datetime.date.today

        return form


class JournalSubmissionUpdate(UpdateView):
    model = JournalSubmission
