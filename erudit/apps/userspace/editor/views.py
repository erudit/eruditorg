import json

from django.template.context_processors import csrf

from django.views.generic.edit import CreateView, UpdateView
from django.views.generic import ListView

from django.core.urlresolvers import reverse

from rules.contrib.views import PermissionRequiredMixin

from core.editor.models import IssueSubmission
from core.userspace.viewmixins import LoginRequiredMixin

from .forms import IssueSubmissionForm, IssueSubmissionUploadForm


class IssueSubmissionCheckMixin(PermissionRequiredMixin, LoginRequiredMixin):
    permission_required = 'editor.manage_issuesubmission'

    def get_queryset(self):
        qs = super(IssueSubmissionCheckMixin, self).get_queryset()
        ids = [issue.id for issue in qs if self.request.user.has_perm(
               'editor.manage_issuesubmission', issue.journal)]
        return qs.filter(id__in=ids)


class IssueSubmissionCreate(IssueSubmissionCheckMixin, CreateView):
    model = IssueSubmission
    form_class = IssueSubmissionForm
    template_name = 'userspace/editor/form.html'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({'user': self.request.user})
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(csrf(self.request))
        form = context['form']

        membership = {}
        for journal in form.fields['journal'].queryset:
            membership[journal.pk] = [
                v[0] for v in journal.members.values_list('id')]

        context.update({'journals': json.dumps(membership)})
        return context


class IssueSubmissionUpdate(IssueSubmissionCheckMixin, UpdateView):
    model = IssueSubmission
    form_class = IssueSubmissionUploadForm
    template_name = 'userspace/editor/form.html'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({'user': self.request.user})
        return kwargs

    def get_permission_object(self):
        obj = self.get_object()
        return obj.journal

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
        # In this view, we have a widget, plupload, that injects JS in the page. This JS needs
        # jquery. Because of this, we need to load jquery in the header rather than in the footer.
        context['put_js_in_head'] = True
        return context

    def get_success_url(self):
        return reverse('userspace:editor:issues')


class IssueSubmissionList(IssueSubmissionCheckMixin, ListView):
    model = IssueSubmission
    template_name = 'userspace/editor/issues.html'
