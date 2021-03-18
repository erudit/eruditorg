import datetime as dt
import pytest

from django.utils import timezone as tz

from core.editor.conf import settings as editor_settings
from core.editor.models import IssueSubmission
from core.editor.test.factories import IssueSubmissionFactory


@pytest.mark.django_db
class TestIssueSubmissionManager:
    def test_eminent_archival(self):
        old_dt = tz.now() - dt.timedelta(days=editor_settings.ARCHIVAL_DAY_OFFSET - 5)
        statuses = [
            IssueSubmission.DRAFT,
            IssueSubmission.SUBMITTED,
            IssueSubmission.NEEDS_CORRECTIONS,
            IssueSubmission.VALID,
        ]

        # Archived issue, should not be returned by eminent_archival().
        archived_issue = IssueSubmissionFactory(status=IssueSubmission.VALID, archived=True)
        archived_issue._meta.get_field("date_modified").auto_now = False
        archived_issue.date_modified = old_dt
        archived_issue.save()
        archived_issue._meta.get_field("date_modified").auto_now = True

        # Issues recently modified, should not be returned by eminent_archival().
        IssueSubmissionFactory(status=IssueSubmission.VALID)

        # Issues modified three months ago (minus five days), should be returned by
        # eminent_archival() if they are validated.
        old_issues = [IssueSubmissionFactory(status=status) for status in statuses]
        for issue in old_issues:
            issue._meta.get_field("date_modified").auto_now = False
            issue.date_modified = old_dt
            issue.save()
            issue._meta.get_field("date_modified").auto_now = True

        # Expected issues, which have been modified three months ago and are validated.
        expected_eminent_archival_issues = filter(
            lambda i: i.status == IssueSubmission.VALID, old_issues
        )

        eminent_archival = IssueSubmission.objects.eminent_archival()
        assert list(eminent_archival) == list(expected_eminent_archival_issues)

    def test_ready_for_archival(self):
        old_dt = tz.now() - dt.timedelta(days=editor_settings.ARCHIVAL_DAY_OFFSET)
        statuses = [
            IssueSubmission.DRAFT,
            IssueSubmission.SUBMITTED,
            IssueSubmission.NEEDS_CORRECTIONS,
            IssueSubmission.VALID,
        ]

        # Archived issue, should not be returned by eminent_archival().
        archived_issue = IssueSubmissionFactory(status=IssueSubmission.VALID, archived=True)
        archived_issue._meta.get_field("date_modified").auto_now = False
        archived_issue.date_modified = old_dt
        archived_issue.save()
        archived_issue._meta.get_field("date_modified").auto_now = True

        # Issues recently modified, should not be returned by eminent_archival().
        IssueSubmissionFactory(status=IssueSubmission.VALID)

        # Issues modified three months ago, should be returned by ready_for_archival() if they are
        # validated.
        old_issues = [IssueSubmissionFactory(status=status) for status in statuses]
        for issue in old_issues:
            issue._meta.get_field("date_modified").auto_now = False
            issue.date_modified = old_dt
            issue.save()
            issue._meta.get_field("date_modified").auto_now = True

        # Expected issues, which have been modified three months ago and are validated.
        expected_ready_for_archival_issues = filter(
            lambda i: i.status == IssueSubmission.VALID, old_issues
        )

        ready_for_archival = IssueSubmission.objects.ready_for_archival()
        assert list(ready_for_archival) == list(expected_ready_for_archival_issues)

    def test_action_needed(self):
        statuses = [
            IssueSubmission.DRAFT,
            IssueSubmission.SUBMITTED,
            IssueSubmission.NEEDS_CORRECTIONS,
            IssueSubmission.VALID,
        ]

        # Issues recently modified, should not be returned by action_needed().
        IssueSubmissionFactory(status=IssueSubmission.VALID)

        # Issues modified two weeks ago, should be returned by action_needed() if they are submitted
        # or in needs corrections.
        old_issues = [IssueSubmissionFactory(status=status) for status in statuses]
        old_dt = tz.now() - dt.timedelta(days=editor_settings.ACTION_NEEDED_DAY_OFFSET)
        for issue in old_issues:
            issue._meta.get_field("date_modified").auto_now = False
            issue.date_modified = old_dt
            issue.save()
            issue._meta.get_field("date_modified").auto_now = True

        # Expected issues, which have been modified two weeks ago and are submitted or in needs
        # corrections.
        expected_action_needed_issues = filter(lambda i: i.status in statuses[1:3], old_issues)

        assert list(IssueSubmission.objects.action_needed()) == list(expected_action_needed_issues)
