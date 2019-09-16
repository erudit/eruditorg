from django.dispatch import receiver

from core.editor.shortcuts import get_production_team_group
from core.email import Email
from django.conf import settings
from core.editor.apps import EMAIL_TAG


from .signals import userspace_post_transition


@receiver(userspace_post_transition)
def send_production_team_email(sender, issue_submission, transition_name, request, **kwargs):
    if not issue_submission.is_submitted:
        return

    production_team_group = get_production_team_group(issue_submission.journal)
    if production_team_group is None:
        return

    emails = list(production_team_group.user_set.values_list('email', flat=True))
    if not emails:
        return

    email = Email(
        emails,
        html_template='emails/editor/new_issue_submission_content.html',
        subject_template='emails/editor/new_issue_submission_subject.html',
        extra_context={'issue': issue_submission, 'journal': issue_submission.journal},
        tag=EMAIL_TAG
    )
    email.send()


@receiver(userspace_post_transition)
def send_notification_email_after_issue_submission_approval(
        sender, issue_submission, transition_name, request, **kwargs):
    if not issue_submission.is_validated:
        return

    emails = [issue_submission.contact.email, ]
    extra_context = {'issue': issue_submission, 'journal': issue_submission.journal}

    comment = issue_submission.status_tracks.last().comment

    if comment:
        extra_context['comment'] = comment

    email = Email(
        emails,
        from_email=settings.PUBLISHER_EMAIL,
        html_template='emails/editor/issue_submission_validated_content.html',
        subject_template='emails/editor/issue_submission_validated_subject.html',
        extra_context=extra_context,
        tag=EMAIL_TAG
    )
    email.send()


@receiver(userspace_post_transition)
def send_notification_email_after_issue_submission_refusal(
        sender, issue_submission, transition_name, request, **kwargs):
    if not issue_submission.is_draft and not issue_submission.needs_corrections:
        return
    extra_context = {'issue': issue_submission, 'journal': issue_submission.journal}
    emails = [issue_submission.contact.email, ]

    comment = issue_submission.status_tracks.last().comment

    if comment:
        extra_context['comment'] = comment

    email = Email(
        emails,
        from_email=settings.PUBLISHER_EMAIL,
        html_template='emails/editor/issue_submission_refused_content.html',
        subject_template='emails/editor/issue_submission_refused_subject.html',
        extra_context=extra_context,
        tag=EMAIL_TAG
    )
    email.send()
