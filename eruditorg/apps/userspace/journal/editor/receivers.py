# -*- coding: utf-8 -*-

import logging

from django.dispatch import receiver

from core.editor.shortcuts import get_production_team_group
from core.email import Email

from .signals import userspace_post_transition

logger = logging.getLogger(__name__)


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
        extra_context={'issue': issue_submission})
    email.send()


@receiver(userspace_post_transition)
def send_notification_email_after_issue_submission_approval(
        sender, issue_submission, transition_name, request, **kwargs):
    if not issue_submission.is_validated:
        return

    emails = [issue_submission.contact.email, ]

    email = Email(
        emails,
        html_template='emails/editor/issue_submission_validated_content.html',
        subject_template='emails/editor/issue_submission_validated_subject.html',
        extra_context={'issue': issue_submission, 'journal': issue_submission.journal})
    email.send()


@receiver(userspace_post_transition)
def send_notification_email_after_issue_submission_refusal(
        sender, issue_submission, transition_name, request, **kwargs):
    if not issue_submission.is_draft:
        return

    emails = [issue_submission.contact.email, ]

    email = Email(
        emails,
        html_template='emails/editor/issue_submission_refused_content.html',
        subject_template='emails/editor/issue_submission_refused_subject.html',
        extra_context={'issue': issue_submission})
    email.send()
