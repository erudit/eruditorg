from django.template.context_processors import csrf

from django.views.generic.edit import CreateView, UpdateView
from django.views.generic import ListView

from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _

from rules.contrib.views import PermissionRequiredMixin
from navutils import Breadcrumb

from userspace.views import UserspaceBreadcrumbsMixin
from core.userspace.viewmixins import LoginRequiredMixin
from core.editor.models import IssueSubmission
from .forms import IssueSubmissionForm, IssueSubmissionUploadForm


class IssueSubmissionBreadcrumbsMixin(UserspaceBreadcrumbsMixin):

    def get_breadcrumbs(self):
        breadcrumbs = super(IssueSubmissionBreadcrumbsMixin,
                            self).get_breadcrumbs()
        breadcrumbs.append(Breadcrumb(
            _("Dépôts de numéros"),
            pattern_name='editor:issues'))
        return breadcrumbs


class IssueSubmissionCheckMixin(PermissionRequiredMixin, LoginRequiredMixin):
    permission_required = 'editor.manage_issuesubmission'

    def get_queryset(self):
        qs = super(IssueSubmissionCheckMixin, self).get_queryset()
        ids = [issue.id for issue in qs if self.request.user.has_perm(
               'editor.manage_issuesubmission', issue.journal)]
        return qs.filter(id__in=ids)


class IssueSubmissionCreate(IssueSubmissionBreadcrumbsMixin,
                            IssueSubmissionCheckMixin, CreateView):
    model = IssueSubmission
    form_class = IssueSubmissionForm
    template_name = 'userspace/editor/form.html'
    title = _("Faire un dépôt de numéros")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(csrf(self.request))
        return context

    def get_form(self, form_class):
        form = super().get_form(form_class)
        qs = self.request.user.journals.all()
        ids = [j.id for j in qs if self.request.user.has_perm(
               'editor.manage_issuesubmission', j)]
        qs.filter(id__in=ids)
        form.fields['journal'].queryset = qs.filter(id__in=ids)

        form.fields['journal'].initial = form.fields['journal'].queryset.first()

        journals_members = User.objects.filter(
            journals=self.request.user.journals.all()
        ).distinct()

        form.fields['contact'].queryset = journals_members
        form.fields['contact'].initial = form.fields['contact'].queryset.first()
        return form


class IssueSubmissionUpdate(IssueSubmissionBreadcrumbsMixin,
                            IssueSubmissionCheckMixin, UpdateView):
    model = IssueSubmission
    form_class = IssueSubmissionUploadForm
    template_name = 'userspace/editor/form.html'

    def get_permission_object(self):
        obj = self.get_object()
        return obj.journal

    def get_title(self):
        return _("Modifier un dépôt de numéros")

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


class IssueSubmissionList(IssueSubmissionBreadcrumbsMixin,
                          IssueSubmissionCheckMixin, ListView):
    model = IssueSubmission
    template_name = 'userspace/editor/issues.html'
