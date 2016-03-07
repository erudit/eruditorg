# -*- coding: utf-8 -*-

import json
import logging
import mimetypes
import os

from django.core.urlresolvers import reverse
from django.http import Http404
from django.http import HttpResponse
from django.template.context_processors import csrf
from django.utils.translation import ugettext_lazy as _
from django.views.generic import CreateView
from django.views.generic import DetailView
from django.views.generic import ListView
from django.views.generic import UpdateView
from plupload.models import ResumableFile
from rules.contrib.views import PermissionRequiredMixin

from core.editor.models import IssueSubmission
from erudit.models.event import Event
from erudit.utils.workflow import WorkflowMixin

from .forms import IssueSubmissionForm
from .forms import IssueSubmissionUploadForm
from .viewmixins import IssueSubmissionBreadcrumbsMixin
from .viewmixins import IssueSubmissionCheckMixin

logger = logging.getLogger(__name__)


class IssueSubmissionCreate(IssueSubmissionBreadcrumbsMixin,
                            IssueSubmissionCheckMixin, CreateView):
    model = IssueSubmission
    form_class = IssueSubmissionForm
    template_name = 'userspace/editor/form.html'
    title = _("Faire un dépôt de numéros")

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
        # In this view, we have a widget, django_select2, that has its JS loaded in the "extrahead"
        # block through {{ form.media }}. Because this outputs CSS at the same time as JS, we can't
        # move this to the footer, so we need jquery in the head.
        context['put_js_in_head'] = True
        return context

    def form_valid(self, form):
        result = super().form_valid(form)
        Event.create_submission(author=self.request.user, submission=form.instance)
        return result


class IssueSubmissionUpdate(WorkflowMixin,
                            IssueSubmissionBreadcrumbsMixin,
                            IssueSubmissionCheckMixin, UpdateView):
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

        # In this view, we have a widget, plupload, that injects JS in the page. This JS needs
        # jquery. Because of this, we need to load jquery in the header rather than in the footer.
        context['put_js_in_head'] = True

        transitions = self.object.\
            get_available_user_status_transitions(self.request.user)
        context['transitions'] = transitions

        return context

    def apply_transition(self, *args, **kwargs):
        old_status = self.object.status
        result = super().apply_transition(*args, **kwargs)
        if self.object.status != old_status:
            Event.change_submission_status(
                author=self.request.user,
                submission=self.object,
                old_status=old_status
            )
        return result

    def get_success_url(self):
        return reverse('userspace:editor:issues')


class IssueSubmissionList(IssueSubmissionBreadcrumbsMixin,
                          IssueSubmissionCheckMixin, ListView):
    model = IssueSubmission
    template_name = 'userspace/editor/issues.html'


class IssueSubmissionAttachmentView(PermissionRequiredMixin, DetailView):
    """
    Returns an IssueSubmission attachment.
    """
    model = ResumableFile
    raise_exception = True

    def render_to_response(self, context, **response_kwargs):
        filename = os.path.basename(self.object.path)

        try:
            fsock = open(self.object.path, 'rb')
        except FileNotFoundError:
            # The feed is not available.
            logger.error('Resumable file not found: {}'.format(self.object.path),
                         exc_info=True, extra={'request': self.request, })
            raise Http404

        # Try to guess the content type of the given file
        content_type, _ = mimetypes.guess_type(self.object.path)
        if not content_type:
            content_type = 'text/plain'

        response = HttpResponse(fsock, content_type=content_type)
        response['Content-Disposition'] = 'attachment; filename={}'.format(filename)

        return response

    def has_permission(self):
        return self.request.user.has_perm('editor.manage_issuesubmission') \
            or self.request.user.has_perm('editor.review_issuesubmission')
