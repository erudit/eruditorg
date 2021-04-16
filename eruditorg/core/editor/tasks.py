from django.contrib.auth.models import Group
from itertools import groupby
from operator import attrgetter

from core.email import Email

from .models import IssueSubmission
from .apps import EMAIL_TAG
from .utils import get_production_teams_groups


def _handle_issue_submission_archival_and_files_deletion() -> None:
    # First, get issue submissions ready for archival and whose files must be deleted.
    for issue in IssueSubmission.objects.ready_for_archival():
        for fversion in issue.files_versions.all():
            [rf.delete() for rf in fversion.submissions.all()]
        issue.archived = True
        issue.save()

    # Now get issue submissions that will be archived eminently. The production team must be
    # informed that their files will be deleted in five days.
    issues = IssueSubmission.objects.eminent_archival()
    if not issues.count():
        return

    # Get all production teams groups and their emails.
    production_teams_groups = {
        production_team_group.id: {
            "emails": list(production_team_group.user_set.values_list("email", flat=True)),
            "issue_submissions": [],
        }
        for production_team_group in Group.objects.filter(productionteam__isnull=False)
    }

    # Group issues by production team group.
    for issue in issues:
        for production_team_group in get_production_teams_groups(issue.journal):
            production_teams_groups[production_team_group.id]["issue_submissions"].append(issue)

    # Now prepare and send an email to each production team group with eminent archival issues.
    for production_team_group in production_teams_groups.values():
        # Group issues by journal.
        eminent_archival_issues = {
            journal_name: list(issues)
            for journal_name, issues in groupby(
                production_team_group["issue_submissions"],
                attrgetter("journal.name"),
            )
        }

        # Do not send email if there is no emails or no issue submissions.
        if not production_team_group["emails"] or not production_team_group["issue_submissions"]:
            continue

        # Send the email.
        email = Email(
            production_team_group["emails"],
            html_template="emails/editor/issue_files_deletion_content.html",
            subject_template="emails/editor/issue_files_deletion_subject.html",
            extra_context={"issue_submissions": eminent_archival_issues},
            tag=EMAIL_TAG,
        )
        email.send()


def _handle_issue_submission_action_needed() -> None:
    # Get action needed issue submissions.
    issues = IssueSubmission.objects.action_needed()
    if not issues.exists():
        return

    # Get all production teams groups and their emails.
    production_teams_groups = {
        production_team_group.id: {
            "emails": list(production_team_group.user_set.values_list("email", flat=True)),
            IssueSubmission.SUBMITTED: [],
            IssueSubmission.NEEDS_CORRECTIONS: [],
        }
        for production_team_group in Group.objects.filter(productionteam__isnull=False)
    }

    # Group issues by production team group.
    for issue in issues:
        for production_team_group in get_production_teams_groups(issue.journal):
            production_teams_groups[production_team_group.id][issue.status].append(issue)

    # Now prepare and send an email to each production team group with action needed issues.
    for production_team_group in production_teams_groups.values():
        # Group issues by status and by journal.
        needs_review = {
            journal_name: list(issues)
            for journal_name, issues in groupby(
                production_team_group[IssueSubmission.SUBMITTED],
                attrgetter("journal.name"),
            )
        }
        needs_corrections = {
            journal_name: list(issues)
            for journal_name, issues in groupby(
                production_team_group[IssueSubmission.NEEDS_CORRECTIONS],
                attrgetter("journal.name"),
            )
        }

        # Do not send email if there is no emails or no issue submissions.
        if not production_team_group["emails"] or not (
            production_team_group[IssueSubmission.SUBMITTED]
            + production_team_group[IssueSubmission.NEEDS_CORRECTIONS]
        ):
            continue

        # Send the email.
        email = Email(
            production_team_group["emails"],
            html_template="emails/editor/issue_submission_action_needed_content.html",
            subject_template="emails/editor/issue_submission_action_needed_subject.html",
            extra_context={
                "submitted": needs_review,
                "needs_corrections": needs_corrections,
            },
            tag=EMAIL_TAG,
        )
        email.send()
