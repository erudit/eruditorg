# -*- coding: utf-8 -*-

import logging
import mimetypes
import os

from django.contrib import messages
from django.core.urlresolvers import reverse
from django.http import Http404
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.template.context_processors import csrf
from django.utils.translation import ugettext_lazy as _
from django.views.generic import CreateView
from django.views.generic import DetailView
from django.views.generic import ListView
from django.views.generic import UpdateView
from django.views.generic.detail import BaseDetailView
from django.views.generic.detail import SingleObjectTemplateResponseMixin
from plupload.models import ResumableFile

from base.viewmixins import LoginRequiredMixin
from base.viewmixins import MenuItemMixin
from core.editor.models import IssueSubmission
from core.metrics.metric import metric

from ..viewmixins import JournalScopePermissionRequiredMixin

from .forms import IssueSubmissionForm
from .forms import IssueSubmissionTransitionCommentForm
from .forms import IssueSubmissionUploadForm

logger = logging.getLogger(__name__)


class IssueSubmissionCreate(
        LoginRequiredMixin, JournalScopePermissionRequiredMixin, MenuItemMixin, CreateView):
    menu_journal = 'editor'
    model = IssueSubmission
    form_class = IssueSubmissionForm
    permission_required = 'editor.manage_issuesubmission'
    template_name = 'userspace/journal/editor/form.html'
    title = _("Faire un dépôt de numéros")

    def get_form_kwargs(self):
        kwargs = super(IssueSubmissionCreate, self).get_form_kwargs()
        kwargs.update({'journal': self.current_journal})
        kwargs.update({'user': self.request.user})
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(csrf(self.request))
        # In this view, we have a widget, django_select2, that has its JS loaded in the "extrahead"
        # block through {{ form.media }}. Because this outputs CSS at the same time as JS, we can't
        # move this to the footer, so we need jquery in the head.
        context['put_js_in_head'] = True
        return context

    def form_valid(self, form):
        result = super().form_valid(form)
        metric(
            'erudit__issuesubmission__create',
            author_id=self.request.user.id, submission_id=form.instance.id)
        return result


class IssueSubmissionUpdate(
        LoginRequiredMixin, JournalScopePermissionRequiredMixin, MenuItemMixin, UpdateView):
    menu_journal = 'editor'
    model = IssueSubmission
    form_class = IssueSubmissionUploadForm
    template_name = 'userspace/journal/editor/form.html'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({'journal': self.current_journal})
        kwargs.update({'user': self.request.user})
        return kwargs

    def get_permission_object(self):
        obj = self.get_object()
        return obj.journal

    def get_title(self):
        return _("Modifier un dépôt de numéros")

    def get_form(self, form_class):
        form = super().get_form(form_class)

        obj = self.get_object()
        if obj.status in (
                IssueSubmission.VALID, IssueSubmission.SUBMITTED, IssueSubmission.ARCHIVED):
            form.disable_form()

        form.fields['submissions'].widget.set_model_reference(
            "editor.IssueSubmissionFilesVersion",
            obj.last_files_version.pk
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

        context['status_tracks'] = self.object.status_tracks.all()

        return context

    def get_success_url(self):
        return reverse('userspace:journal:editor:issues', args=(self.current_journal.pk, ))

    def has_permission(self):
        obj = self.get_permission_object()
        return self.request.user.has_perm('editor.manage_issuesubmission', obj) \
            or self.request.user.has_perm('editor.review_issuesubmission')


class IssueSubmissionTransitionView(
        LoginRequiredMixin, JournalScopePermissionRequiredMixin, MenuItemMixin,
        SingleObjectTemplateResponseMixin, BaseDetailView):
    context_object_name = 'issue_submission'
    menu_journal = 'editor'
    model = IssueSubmission
    raise_exception = True
    template_name = 'userspace/journal/editor/issuesubmission_transition.html'
    use_comment_form = False

    # The following attributes should be defined in subclasses
    question = None
    success_message = None
    transition_name = None

    def apply_transition(self, request, *args, **kwargs):
        """ Applies a specific transition and redirects the user to the success URL. """
        self.object = self.get_object()
        success_url = self.get_success_url()

        old_status = self.object.status

        # Applies the transition
        transition = getattr(self.object, self.transition_name)
        transition()
        self.object.save()

        # Saves a potential comment if applicable
        if self.use_comment_form:
            form = IssueSubmissionTransitionCommentForm(data=request.POST)
            comment = form.cleaned_data.get('comment', None) if form.is_valid() else None
            if comment:
                track = self.object.last_status_track
                track.comment = comment
                track.save()

        # Capture a metric when the status changes
        if self.object.status != old_status:
            metric(
                'erudit__issuesubmission__change_status',
                tags={'old_status': old_status, 'new_status': self.object.status},
                author_id=self.request.user.id, submission_id=self.object.id)

        return HttpResponseRedirect(success_url)

    def post(self, request, *args, **kwargs):
        return self.apply_transition(request, *args, **kwargs)

    def get_success_url(self):
        messages.success(self.request, self.success_message)
        return reverse('userspace:journal:editor:update',
                       args=(self.current_journal.pk, self.object.pk, ))

    def get_context_data(self, **kwargs):
        context = super(IssueSubmissionTransitionView, self).get_context_data(**kwargs)
        context['question'] = self.question
        if self.use_comment_form:
            context['comment_form'] = IssueSubmissionTransitionCommentForm()
        return context


class IssueSubmissionSubmitView(IssueSubmissionTransitionView):
    question = _('Voulez-vous soumettre le numéro ?')
    permission_required = 'editor.manage_issuesubmission'
    success_message = _('Le numéro a été soumis avec succès')
    transition_name = 'submit'

    def get_permission_object(self):
        # All the users who have the 'review_issuesubmission' authorization should be allowed to
        # review all journals.
        return self.get_object().journal


class IssueSubmissionApproveView(IssueSubmissionTransitionView):
    question = _('Voulez-vous approuver le numéro ?')
    success_message = _('Le numéro a été approuvé avec succès')
    transition_name = 'approve'

    def has_permission(self):
        return self.request.user.has_perm('editor.review_issuesubmission')


class IssueSubmissionRefuseView(IssueSubmissionTransitionView):
    question = _('Voulez-vous refuser le numéro ?')
    success_message = _('Le numéro a été refusé avec succès')
    transition_name = 'refuse'
    use_comment_form = True

    def has_permission(self):
        return self.request.user.has_perm('editor.review_issuesubmission')


class IssueSubmissionArchiveView(IssueSubmissionTransitionView):
    question = _('Voulez-vous archiver le numéro ?')
    success_message = _('Le numéro a été archivé avec succès')
    transition_name = 'archive'

    def has_permission(self):
        return self.request.user.has_perm('editor.review_issuesubmission')


class IssueSubmissionList(
        LoginRequiredMixin, JournalScopePermissionRequiredMixin, MenuItemMixin, ListView):
    menu_journal = 'editor'
    model = IssueSubmission
    template_name = 'userspace/journal/editor/issues.html'

    def get_queryset(self):
        qs = super(IssueSubmissionList, self).get_queryset()
        return qs.filter(journal=self.current_journal)

    def has_permission(self):
        obj = self.get_permission_object()
        return self.request.user.has_perm('editor.manage_issuesubmission', obj) \
            or self.request.user.has_perm('editor.review_issuesubmission')


class IssueSubmissionAttachmentView(
        LoginRequiredMixin, JournalScopePermissionRequiredMixin, DetailView):
    """
    Returns an IssueSubmission attachment.
    """
    model = ResumableFile
    raise_exception = True

    def render_to_response(self, context, **response_kwargs):
        filename = os.path.basename(self.object.path)

        try:
            fsock = open(self.object.path, 'rb')
        except FileNotFoundError:  # noqa
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
        obj = self.get_permission_object()
        return self.request.user.has_perm('editor.manage_issuesubmission', obj) \
            or self.request.user.has_perm('editor.review_issuesubmission')
