import structlog
from itertools import groupby
from operator import attrgetter

from core.email import Email

from .models import IssueSubmission, ProductionTeam
from .apps import EMAIL_TAG

logger = structlog.getLogger(__name__)


def _handle_issue_submission_archival_and_files_deletion():
    # First, get issue submissions ready for archival and whose files must be deleted.
    for issue in IssueSubmission.objects.ready_for_archival():
        for fversion in issue.files_versions.all():
            [rf.delete() for rf in fversion.submissions.all()]
        issue.archived = True
        issue.save()

    # Get production team emails.
    emails = ProductionTeam.emails()
    if emails is None:
        return

    # Now get issue submissions that will be archived eminently. The production team must be
    # informed that their files will be deleted in five days.
    issues = IssueSubmission.objects.eminent_archival()
    if not issues.exists():
        return

    # Group issues by journal.
    eminent_archival_issues = {
        journal_name: list(issues) for journal_name, issues in groupby(
            issues,
            attrgetter('journal.name'),
        )
    }

    # Send the email.
    email = Email(
        list(emails),
        html_template='emails/editor/issue_files_deletion_content.html',
        subject_template='emails/editor/issue_files_deletion_subject.html',
        extra_context={'issue_submissions': eminent_archival_issues},
        tag=EMAIL_TAG
    )
    email.send()


def _handle_issue_submission_action_needed():
    # Get production team emails.
    emails = ProductionTeam.emails()
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
