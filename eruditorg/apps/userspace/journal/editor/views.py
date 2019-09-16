import os.path
import datetime as dt
import structlog
from urllib.parse import quote

from django.conf import settings
from django.contrib import messages
from django.urls import reverse
from django.http import HttpResponseRedirect
from django.template.context_processors import csrf
from django.utils.formats import date_format
from django.utils.translation import ugettext_lazy as _
from django.views.generic import CreateView
from django.views.generic import DeleteView
from django.views.generic import DetailView
from django.views.generic import ListView
from django.views.generic import UpdateView
from django.views.generic.detail import BaseDetailView
from django.views.generic.detail import SingleObjectTemplateResponseMixin
from resumable_uploads.models import ResumableFile

from base.viewmixins import MenuItemMixin
from core.editor.models import IssueSubmission
from core.metrics.metric import metric
from core.editor.utils import get_archive_date

from ..viewmixins import JournalScopePermissionRequiredMixin
from .viewmixins import IssueSubmissionContextMixin

from .forms import IssueSubmissionForm
from .forms import IssueSubmissionTransitionCommentForm
from .forms import IssueSubmissionUploadForm
from .signals import userspace_post_transition

logger = structlog.getLogger(__name__)


class IssueSubmissionListView(
        JournalScopePermissionRequiredMixin, MenuItemMixin, ListView):
    menu_journal = 'editor'
    model = IssueSubmission
    raise_exception = False
    template_name = 'userspace/journal/editor/issues.html'

    def get_queryset(self):
        qs = super(IssueSubmissionListView, self).get_queryset()
        return qs.filter(journal=self.current_journal, archived=False)

    def has_permission(self):
        obj = self.get_permission_object()
        return self.request.user.has_perm('editor.manage_issuesubmission', obj) \
            or self.request.user.has_perm('editor.review_issuesubmission')


class IssueSubmissionDetailView(
        JournalScopePermissionRequiredMixin, MenuItemMixin, DetailView):
    context_object_name = 'issue'
    force_scope_switch_to_pattern_name = 'userspace:journal:editor:issues'
    menu_journal = 'editor'
    model = IssueSubmission
    template_name = 'userspace/journal/editor/detail.html'

    def get_context_data(self, **kwargs):
        context = super(IssueSubmissionDetailView, self).get_context_data(**kwargs)
        transitions = self.object.\
            get_available_user_status_transitions(self.request.user)
        context['transitions'] = transitions
        context['status_tracks'] = self.object.status_tracks.all()
        return context

    def get_queryset(self):
        qs = super(IssueSubmissionDetailView, self).get_queryset()
        return qs.filter(journal=self.current_journal)

    def has_permission(self):
        obj = self.get_permission_object()
        return self.request.user.has_perm('editor.manage_issuesubmission', obj) \
            or self.request.user.has_perm('editor.review_issuesubmission')


class IssueSubmissionCreate(
        IssueSubmissionContextMixin, JournalScopePermissionRequiredMixin, MenuItemMixin,
        CreateView):
    menu_journal = 'editor'
    model = IssueSubmission
    raise_exception = False
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
        return context

    def get_success_url(self):
        logger.info(
            'editor.issuesubmission.create',
            url=self.object.get_absolute_url(),
            **self.get_context_info()
        )
        messages.success(self.request, _('La demande a été créée avec succès'))
        return reverse(
            'userspace:journal:editor:update', args=(self.current_journal.pk, self.object.pk, ))

    def form_valid(self, form):
        result = super().form_valid(form)
        metric(
            'erudit__issuesubmission__create',
            author_id=self.request.user.id, submission_id=form.instance.id)
        return result


class IssueSubmissionUpdate(
        IssueSubmissionContextMixin, JournalScopePermissionRequiredMixin, MenuItemMixin,
        UpdateView):
    force_scope_switch_to_pattern_name = 'userspace:journal:editor:issues'
    menu_journal = 'editor'
    model = IssueSubmission
    raise_exception = False
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

    def get_form(self, form_class=None):
        form = super().get_form(form_class)

        obj = self.get_object()
        if obj.status in (
                IssueSubmission.VALID, IssueSubmission.SUBMITTED):
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

        transitions = self.object.\
            get_available_user_status_transitions(self.request.user)
        context['transitions'] = transitions

        context['status_tracks'] = self.object.status_tracks.all()

        return context

    def get_queryset(self):
        qs = super(IssueSubmissionUpdate, self).get_queryset()
        return qs.filter(journal=self.current_journal)

    def get_success_url(self):
        logger.debug('update', **self.get_context_info())
        messages.success(self.request, _('La demande a été enregistrée avec succès'))
        return reverse(
            'userspace:journal:editor:detail', args=(self.current_journal.pk, self.object.pk, ))

    def has_permission(self):
        obj = self.get_permission_object()
        return (
            self.request.user.has_perm('editor.manage_issuesubmission', obj) or
            self.request.user.has_perm('editor.review_issuesubmission')
        )


class IssueSubmissionTransitionView(
        IssueSubmissionContextMixin, JournalScopePermissionRequiredMixin, MenuItemMixin,
        SingleObjectTemplateResponseMixin, BaseDetailView):
    context_object_name = 'issue_submission'
    force_scope_switch_to_pattern_name = 'userspace:journal:editor:issues'
    menu_journal = 'editor'
    model = IssueSubmission
    raise_exception = True
    transition_signal = userspace_post_transition
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
        else:
            comment = None

        # Capture a metric when the status changes
        if self.object.status != old_status:
            metric(
                'erudit__issuesubmission__change_status',
                tags={'old_status': old_status, 'new_status': self.object.status},
                author_id=self.request.user.id, submission_id=self.object.id)

        logger.info(
            'editor.issuesubmission.update',
            old_status=old_status,
            new_status=self.object.status,
            comment=comment,
            url=self.object.get_absolute_url(),
            **self.get_context_info()
        )
        # Send a signal in order to notify the update of the issue submission's status
        self.transition_signal.send(
            sender=self, issue_submission=self.object, transition_name=self.transition_name,
            request=request)

        return HttpResponseRedirect(success_url)

    def post(self, request, *args, **kwargs):
        return self.apply_transition(request, *args, **kwargs)

    def get_queryset(self):
        qs = super(IssueSubmissionTransitionView, self).get_queryset()
        return qs.filter(journal=self.current_journal)

    def get_success_message(self):
        return self.success_message

    def get_success_url(self):
        messages.success(self.request, self.get_success_message())
        return reverse('userspace:journal:editor:detail',
                       args=(self.current_journal.pk, self.object.pk, ))

    def get_context_data(self, **kwargs):
        context = super(IssueSubmissionTransitionView, self).get_context_data(**kwargs)
        context['question'] = self.question
        if self.use_comment_form:
            context['comment_form'] = IssueSubmissionTransitionCommentForm()
        return context


class IssueSubmissionApproveView(IssueSubmissionTransitionView):
    question = _('Voulez-vous approuver le numéro ?')
    success_message = _('Le numéro a été approuvé avec succès')
    template_name = 'userspace/journal/editor/issuesubmission_approve.html'
    transition_name = 'approve'
    use_comment_form = True

    def get_context_data(self, **kwargs):
        context = super(IssueSubmissionApproveView, self).get_context_data(**kwargs)
        context['archive_date'] = get_archive_date(dt.datetime.now())
        return context

    def get_success_message(self):
        archive_date = get_archive_date(dt.datetime.now())
        return _(
            'Le numéro a été approuvé avec succès. Veuillez noter que le numéro sera archivé '
            'le {archive_date}. Les fichiers de production seront supprimés.').format(
                archive_date=date_format(archive_date, 'SHORT_DATE_FORMAT'))

    def has_permission(self):
        return self.request.user.has_perm('editor.review_issuesubmission')


class IssueSubmissionRefuseView(IssueSubmissionTransitionView):
    question = None
    success_message = _('Les corrections ont été transmises avec succès')
    transition_name = 'refuse'
    use_comment_form = True
    template_name = 'userspace/journal/editor/issuesubmission_refuse.html'

    def has_permission(self):
        return self.request.user.has_perm('editor.review_issuesubmission')


class IssueSubmissionDeleteView(
        JournalScopePermissionRequiredMixin, MenuItemMixin, DeleteView):
    force_scope_switch_to_pattern_name = 'userspace:journal:editor:issues'
    menu_journal = 'editor'
    model = IssueSubmission
    raise_exception = False
    template_name = 'userspace/journal/editor/delete.html'

    def get_queryset(self):
        qs = super(IssueSubmissionDeleteView, self).get_queryset()
        return qs.filter(journal=self.current_journal)

    def get_success_url(self):
        messages.success(self.request, _('La soumission a été supprimée avec succès'))
        return reverse('userspace:journal:editor:issues', args=(self.current_journal.pk, ))

    def has_permission(self):
        issue_submission = self.get_object()
        if issue_submission.is_validated:
            return False
        return self.request.user.has_perm('editor.manage_issuesubmission')


class IssueSubmissionAttachmentView(
        IssueSubmissionContextMixin, JournalScopePermissionRequiredMixin, DetailView):
    """
    Returns an IssueSubmission attachment.
    """
    model = ResumableFile
    raise_exception = False

    def render_to_response(self, context, **response_kwargs):
        path = self.object.path
        if path.startswith(settings.MEDIA_ROOT):
            path = path[len(settings.MEDIA_ROOT):]
        # urlencode the filename
        basename = os.path.basename(path)
        escaped_basename = quote(basename)
        redirect_to = settings.MEDIA_URL + path.replace(basename, escaped_basename)
        return HttpResponseRedirect(redirect_to)

    def has_permission(self):
        obj = self.get_permission_object()
        return self.request.user.has_perm('editor.manage_issuesubmission', obj) \
            or self.request.user.has_perm('editor.review_issuesubmission')
