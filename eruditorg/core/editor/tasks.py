import structlog
import datetime as dt

from django.utils import timezone as tz
from itertools import groupby
from operator import attrgetter

from core.email import Email

from .conf import settings as editor_settings
from .models import IssueSubmission
from .shortcuts import get_production_team_group
from .apps import EMAIL_TAG

logger = structlog.getLogger(__name__)


def _get_production_team_emails():
    # Get the production team group.
    production_team = get_production_team_group()
    if production_team is None:
        logger.error(
            "email.error",
            msg="Cannot send action needed issue submissions notification email. "
                "There is no production team",
        )
        return

    # Get production team emails.
    emails = production_team.user_set.values_list('email', flat=True)
    if emails is None:
        logger.error(
            "email.error",
            msg="Cannot send action needed issue submissions notification email. "
                "The production team is empty.",
        )
        return
    return emails


def _handle_issuesubmission_files_removal():
    now_dt = tz.now()

    # First, fetches the issue submissions whose files must be deleted.
    for issue in IssueSubmission.objects.archived_expired():
        for fversion in issue.files_versions.all():
            [rf.delete() for rf in fversion.submissions.all()]
        issue.archived = True
        issue.save()

    # Fetches the production team group
    production_team = get_production_team_group()
    if production_team is None:
        logger.error(
            "email.error", msg="Cannot send issue submission removal notification email. There is NO production team"  # noqa
        )
        return

    # Now fetches the issue submissions that will soon be deleted. The production team must be
    # informed that the deletion will occur in a few days.
    email_limit_dt = now_dt - dt.timedelta(days=editor_settings.ARCHIVE_DAY_OFFSET - 5)
    email_limit_dt_range = [
        email_limit_dt.replace(hour=0, minute=0, second=0, microsecond=0),
        email_limit_dt.replace(hour=23, minute=59, second=59, microsecond=999999),
    ]

    issue_submissions_to_email = IssueSubmission.objects.filter(
        status=IssueSubmission.VALID, date_modified__range=email_limit_dt_range)
    if issue_submissions_to_email.exists():
        emails = production_team.user_set.values_list('email', flat=True)
        if not emails:
            return

        email = Email(
            list(emails),
            html_template='emails/editor/issue_files_deletion_content.html',
            subject_template='emails/editor/issue_files_deletion_subject.html',
            extra_context={'issue_submissions': issue_submissions_to_email},
            tag=EMAIL_TAG
        )
        email.send()


def _handle_issue_submission_action_needed():
    # Get production team emails.
    emails = _get_production_team_emails()
    if emails is None:
        return

    # Get action needed issue submissions.
    issues = IssueSubmission.objects.action_needed()
    if not issues.exists():
        return

    # Group issues by status and by journal.
    submitted = {
        journal_name: list(issues) for journal_name, issues in groupby(
            issues.filter(status=IssueSubmission.SUBMITTED),
            attrgetter('journal.name'),
        )
    }
    needs_corrections = {
        journal_name: list(issues) for journal_name, issues in groupby(
            issues.filter(status=IssueSubmission.NEEDS_CORRECTIONS),
            attrgetter('journal.name'),
        )
    }

    # Send the email.
    email = Email(
        list(emails),
        html_template='emails/editor/issue_submission_action_needed_content.html',
        subject_template='emails/editor/issue_submission_action_needed_subject.html',
        extra_context={
            'submitted': submitted,
            'needs_corrections': needs_corrections,
        },
        tag=EMAIL_TAG
    )
    email.send()
