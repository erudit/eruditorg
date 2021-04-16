import datetime as dt
import pytest

from django.contrib.auth.models import Group
from django.core import mail
from django.utils import timezone as tz
from resumable_uploads.models import ResumableFile

from core.editor.conf import settings as editor_settings
from core.editor.tasks import (
    _handle_issue_submission_archival_and_files_deletion,
    _handle_issue_submission_action_needed,
)
from core.editor.test import BaseEditorTestCase
from core.editor.test.factories import ProductionTeamFactory


class TestHandleIssueSubmissionFilesRemoval(BaseEditorTestCase):
    @pytest.fixture(autouse=True)
    def setup_issue_submission(self):
        # Add a file to the issue submission, submit it and approve it.
        rfile = ResumableFile.objects.create(path="dummy/path.png", filesize=42, uploadsize=42)
        self.issue_submission.last_files_version.submissions.add(rfile)
        self.issue_submission.submit()
        self.issue_submission.approve()

    @pytest.fixture
    def eminent_archival_issue(self):
        # Change the issue submission's modified date so that its archival is eminent.
        self.issue_submission._meta.get_field("date_modified").auto_now = False
        self.issue_submission.date_modified = tz.now() - dt.timedelta(
            days=editor_settings.ARCHIVAL_DAY_OFFSET - 5
        )
        self.issue_submission.save()
        self.issue_submission._meta.get_field("date_modified").auto_now = True

    def test_is_able_to_remove_files_from_approved_issue_submissions_after_90_days(self):
        self.issue_submission._meta.get_field("date_modified").auto_now = False
        self.issue_submission.date_modified = tz.now() - dt.timedelta(
            days=editor_settings.ARCHIVAL_DAY_OFFSET
        )
        self.issue_submission.save()
        self.issue_submission._meta.get_field("date_modified").auto_now = True
        _handle_issue_submission_archival_and_files_deletion()
        assert not ResumableFile.objects.count()
        self.issue_submission.refresh_from_db()
        assert self.issue_submission.archived

    def test_sends_an_email_to_notify_the_production_team_5_days_before_removal(
        self, eminent_archival_issue
    ):
        _handle_issue_submission_archival_and_files_deletion()
        assert ResumableFile.objects.count() == 1
        assert len(mail.outbox) == 1
        assert mail.outbox[0].to[0] == self.user.email

    def test_send_an_email_to_main_production_team_if_the_journal_has_no_production_team(
        self, eminent_archival_issue
    ):
        # Remove the journal from the production team.
        self.production_team.journals.remove(self.journal)

        _handle_issue_submission_archival_and_files_deletion()
        assert ResumableFile.objects.count() == 1
        assert len(mail.outbox) == 1

    def test_send_an_email_to_each_production_team_if_the_journal_has_multiple_production_teams(
        self, eminent_archival_issue
    ):
        # Associate a second production team to the journal.
        group_2 = Group.objects.create(name="Other production team")
        production_team_2 = ProductionTeamFactory(group=group_2, identifier="other-production-team")
        production_team_2.journals.add(self.journal)
        self.user.groups.add(group_2)

        _handle_issue_submission_archival_and_files_deletion()
        assert ResumableFile.objects.count() == 1
        assert len(mail.outbox) == 2

    def test_do_not_send_an_email_if_the_production_team_is_empty(self, eminent_archival_issue):
        # Remove the user from the production team so it's empty.
        self.user.groups.remove(self.group)
        _handle_issue_submission_archival_and_files_deletion()
        assert ResumableFile.objects.count() == 1
        assert not len(mail.outbox)


class TestHandleActionNeededIssueSubmissions(BaseEditorTestCase):
    @pytest.fixture
    def action_needed_issues(self):
        # Change the issue submission's modified date so that an action is needed.
        self.issue_submission.submit()
        self.issue_submission._meta.get_field("date_modified").auto_now = False
        self.issue_submission.date_modified = tz.now() - dt.timedelta(
            days=editor_settings.ACTION_NEEDED_DAY_OFFSET
        )
        self.issue_submission.save()
        self.issue_submission._meta.get_field("date_modified").auto_now = True

    def test_email_production_team_about_action_needed_needs_review_issue_submissions(
        self, action_needed_issues
    ):
        _handle_issue_submission_action_needed()
        assert len(mail.outbox) == 1
        assert mail.outbox[0].to[0] == self.user.email

    def test_email_production_team_about_action_needed_needs_corrections_issue_submissions(
        self, action_needed_issues
    ):
        # Refuse the issue submission.
        self.issue_submission.refuse()

        _handle_issue_submission_action_needed()
        assert len(mail.outbox) == 1
        assert mail.outbox[0].to[0] == self.user.email

    def test_send_an_email_to_main_production_team_if_the_journal_has_no_production_team(
        self, action_needed_issues
    ):
        # Remove the journal from the production team.
        self.production_team.journals.remove(self.journal)

        _handle_issue_submission_action_needed()
        assert len(mail.outbox) == 1

    def test_send_an_email_to_each_production_team_if_the_journal_has_multiple_production_teams(
        self, action_needed_issues
    ):
        # Associate a second production team to the journal.
        group_2 = Group.objects.create(name="Other production team")
        production_team_2 = ProductionTeamFactory(group=group_2, identifier="other-production-team")
        production_team_2.journals.add(self.journal)
        self.user.groups.add(group_2)

        _handle_issue_submission_action_needed()
        assert len(mail.outbox) == 2

    def test_do_not_send_an_email_if_the_production_team_is_empty(self, action_needed_issues):
        # Remove the user from the production team so it's empty.
        self.user.groups.remove(self.group)

        _handle_issue_submission_action_needed()
        assert not len(mail.outbox)
