# -*- coding: utf-8 -*-

import logging

from django.dispatch import receiver
from django_fsm import signals

from core.editor.models import IssueSubmission
from core.editor.shortcuts import get_production_team_group
from core.email import Email

logger = logging.getLogger(__name__)


@receiver(signals.post_transition, sender=IssueSubmission)
def send_production_team_email(sender, instance, name, source, target, **kwargs):
    if not instance.is_submitted:
        return

    production_team_group = get_production_team_group(instance.journal)
    if production_team_group is None:
        return

    emails = production_team_group.user_set.values_list('email', flat=True)
    if not emails:
        return

    email = Email(
        emails,
        html_template='emails/editor/new_issue_submission_content.html',
        subject_template='emails/editor/new_issue_submission_subject.html',
        extra_context={'issue': instance})
    email.send()
