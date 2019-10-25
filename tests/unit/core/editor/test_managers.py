import datetime as dt
import pytest

from django.utils import timezone as tz

from core.editor.conf import settings as editor_settings
from core.editor.models import IssueSubmission
from core.editor.test.factories import IssueSubmissionFactory


@pytest.mark.django_db
class TestIssueSubmissionManager:
    def test_action_needed(self):
        statuses = [
            IssueSubmission.DRAFT,
            IssueSubmission.SUBMITTED,
            IssueSubmission.NEEDS_CORRECTIONS,
            IssueSubmission.VALID,
        ]

        # Issues recently modified, should not be returned by action_needed().
        new_issues = [IssueSubmissionFactory(status=status) for status in statuses]

        # Issues modified two weeks ago, should be returned by action_needed() if they are submitted
        # or in needs corrections.
        old_issues = [IssueSubmissionFactory(status=status) for status in statuses]
        old_dt = tz.now() - dt.timedelta(days=editor_settings.ACTION_NEEDED_DAY_OFFSET)
        for issue in old_issues:
            issue._meta.get_field('date_modified').auto_now = False
            issue.date_modified = old_dt
            issue.save()
            issue._meta.get_field('date_modified').auto_now = True

        # Expected issues, which have been modified two weeks ago and are submitted or in needs
        # corrections.
        expected_action_needed_issues = filter(lambda i: i.status in statuses[1:3], old_issues)

        assert list(IssueSubmission.objects.action_needed()) == list(expected_action_needed_issues)
