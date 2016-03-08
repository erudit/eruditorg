# -*- coding: utf-8 -*-

import logging

from django.contrib.auth.models import Group
from django.dispatch import receiver
from django_fsm import signals

from core.editor.conf import settings as editor_settings
from core.editor.models import IssueSubmission
from core.email import Email

logger = logging.getLogger(__name__)


@receiver(signals.post_transition, sender=IssueSubmission)
def send_production_team_email(sender, instance, name, source, target, **kwargs):
    if not instance.is_submitted:
        return

    try:
        production_team = Group.objects.get(id=editor_settings.PRODUCTION_TEAM_GROUP_ID)
    except Group.DoesNotExist:  # pragma: no cover
        logger.error('Unable to find production team group with ID {}'.format(
            editor_settings.PRODUCTION_TEAM_GROUP_ID), exc_info=True)
        return

    emails = production_team.user_set.values_list('email', flat=True)

    email = Email(
        emails,
        html_template='userspace/editor/emails/new_issue_submission_content.html',
        subject_template='userspace/editor/emails/new_issue_submission_subject.html',
        extra_context={'issue': instance})
    email.send()
