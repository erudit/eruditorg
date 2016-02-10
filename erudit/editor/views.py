from django.template.context_processors import csrf

from django.views.generic.edit import CreateView, UpdateView
from django.views.generic import ListView

from django.contrib.auth.models import User
from django.core.urlresolvers import reverse

from rules.contrib.views import PermissionRequiredMixin

from userspace.views import LoginRequiredMixin
from .models import IssueSubmission
from .forms import IssueSubmissionForm, IssueSubmissionUploadForm


class IssueSubmissionCheckMixin(PermissionRequiredMixin, LoginRequiredMixin):
    permission_required = 'editor.manage_issuesubmission'

    def get_queryset(self):
        qs = super(IssueSubmissionCheckMixin, self).get_queryset()
        ids = [issue.id for issue in qs if self.request.user.has_perm(
               'editor.manage_issuesubmission', issue)]
        return qs.filter(id__in=ids)


class IssueSubmissionCreate(IssueSubmissionCheckMixin, CreateView):
    model = IssueSubmission
    form_class = IssueSubmissionForm
    template_name = 'editor/form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(csrf(self.request))
        return context

    def get_form(self, form_class):
        form = super().get_form(form_class)

        form.fields['journal'].queryset = self.request.user.journals.all()

        form.fields['journal'].initial = form.fields['journal'].queryset.first()

        journals_members = User.objects.filter(
            journals=self.request.user.journals.all()
        ).distinct()

        form.fields['contact'].queryset = journals_members
        form.fields['contact'].initial = form.fields['contact'].queryset.first()
        return form


class IssueSubmissionUpdate(IssueSubmissionCheckMixin, UpdateView):
    model = IssueSubmission
    form_class = IssueSubmissionUploadForm
    template_name = 'editor/form.html'

    def get_form(self, form_class):
        form = super().get_form(form_class)

        object = self.get_object()
        if object.status in (
                IssueSubmission.VALID, IssueSubmission.SUBMITTED):
            form.disable_form()

        form.fields['submissions'].widget.set_model_reference(
            "editor.IssueSubmission",
            object.pk
        )

        return form

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['model_name'] = "editor.IssueSubmission"
        context['model_pk'] = self.object.pk
        return context

    def get_success_url(self):
        return reverse('editor:issues')


class IssueSubmissionList(IssueSubmissionCheckMixin, ListView):
    model = IssueSubmission
    template_name = 'editor/issues.html'
