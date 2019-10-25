import datetime as dt

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
    def test_is_able_to_remove_files_from_approved_issue_submissions_after_90_days(self):
        # Setup
        rfile = ResumableFile.objects.create(path='dummy/path.png', filesize=42, uploadsize=42)
        self.issue_submission.last_files_version.submissions.add(rfile)
        self.issue_submission.submit()
        self.issue_submission.approve()
        self.issue_submission._meta.get_field('date_modified').auto_now = False
        self.issue_submission.date_modified = tz.now() - dt.timedelta(
            days=editor_settings.ARCHIVAL_DAY_OFFSET
        )
        self.issue_submission.save()
        self.issue_submission._meta.get_field('date_modified').auto_now = True
        # Run
        _handle_issue_submission_archival_and_files_deletion()
        # Check
        assert not ResumableFile.objects.count()
        self.issue_submission.refresh_from_db()
        assert self.issue_submission.archived

    def test_sends_an_email_to_notify_the_production_team_5_days_before_removal(self):
        # Setup
        group = Group.objects.create(name='Production team')
        ProductionTeamFactory.create(group=group, identifier='main')
        self.user.groups.add(group)
        rfile = ResumableFile.objects.create(path='dummy/path.png', filesize=42, uploadsize=42)
        self.issue_submission.last_files_version.submissions.add(rfile)
        self.issue_submission.submit()
        self.issue_submission.approve()
        self.issue_submission._meta.get_field('date_modified').auto_now = False
        self.issue_submission.date_modified = tz.now() - dt.timedelta(
            days=editor_settings.ARCHIVAL_DAY_OFFSET - 5
        )
        self.issue_submission.save()
        self.issue_submission._meta.get_field('date_modified').auto_now = True
        # Run
        _handle_issue_submission_archival_and_files_deletion()
        # Check
        assert ResumableFile.objects.count() == 1
        assert len(mail.outbox) == 1
        assert mail.outbox[0].to[0] == self.user.email

    def test_do_not_send_an_email_if_the_production_team_group_does_not_exist(self):
        # Setup
        rfile = ResumableFile.objects.create(path='dummy/path.png', filesize=42, uploadsize=42)
        self.issue_submission.last_files_version.submissions.add(rfile)
        self.issue_submission.submit()
        self.issue_submission.approve()
        self.issue_submission._meta.get_field('date_modified').auto_now = False
        self.issue_submission.date_modified = tz.now() - dt.timedelta(
            days=editor_settings.ARCHIVAL_DAY_OFFSET - 5
        )
        self.issue_submission.save()
        self.issue_submission._meta.get_field('date_modified').auto_now = True
        # Run
        _handle_issue_submission_archival_and_files_deletion()
        # Check
        assert ResumableFile.objects.count() == 1
        assert not len(mail.outbox)

    def test_do_not_send_an_email_if_the_production_team_is_empty(self):
        # Setup
        group = Group.objects.create(name='Production team')
        ProductionTeamFactory.create(group=group, identifier='main')
        rfile = ResumableFile.objects.create(path='dummy/path.png', filesize=42, uploadsize=42)
        self.issue_submission.last_files_version.submissions.add(rfile)
        self.issue_submission.submit()
        self.issue_submission.approve()
        self.issue_submission._meta.get_field('date_modified').auto_now = False
        self.issue_submission.date_modified = tz.now() - dt.timedelta(
            days=editor_settings.ARCHIVAL_DAY_OFFSET - 5
        )
        self.issue_submission.save()
        self.issue_submission._meta.get_field('date_modified').auto_now = True
        # Run
        _handle_issue_submission_archival_and_files_deletion()
        # Check
        assert ResumableFile.objects.count() == 1
        assert not len(mail.outbox)


class TestHandleActionNeededIssueSubmissions(BaseEditorTestCase):
    def test_email_production_team_about_action_needed_needs_review_issue_submissions(self):
        # Setup
        group = Group.objects.create(name='Production team')
        ProductionTeamFactory.create(group=group, identifier='main')
        self.user.groups.add(group)
        self.issue_submission.submit()
        self.issue_submission._meta.get_field('date_modified').auto_now = False
        self.issue_submission.date_modified = tz.now() - dt.timedelta(
            days=editor_settings.ACTION_NEEDED_DAY_OFFSET
        )
        self.issue_submission.save()
        self.issue_submission._meta.get_field('date_modified').auto_now = True
        # Run
        _handle_issue_submission_action_needed()
        # Check
        assert len(mail.outbox) == 1
        assert mail.outbox[0].to[0] == self.user.email

    def test_email_production_team_about_action_needed_needs_corrections_issue_submissions(self):
        # Setup
        group = Group.objects.create(name='Production team')
        ProductionTeamFactory.create(group=group, identifier='main')
        self.user.groups.add(group)
        self.issue_submission.submit()
        self.issue_submission.refuse()
        self.issue_submission._meta.get_field('date_modified').auto_now = False
        self.issue_submission.date_modified = tz.now() - dt.timedelta(
            days=editor_settings.ACTION_NEEDED_DAY_OFFSET
        )
        self.issue_submission.save()
        self.issue_submission._meta.get_field('date_modified').auto_now = True
        # Run
        _handle_issue_submission_action_needed()
        # Check
        assert len(mail.outbox) == 1
        assert mail.outbox[0].to[0] == self.user.email

    def test_do_not_send_an_email_if_the_production_team_group_does_not_exist(self):
        # Setup
        self.issue_submission.submit()
        self.issue_submission._meta.get_field('date_modified').auto_now = False
        self.issue_submission.date_modified = tz.now() - dt.timedelta(
            days=editor_settings.ACTION_NEEDED_DAY_OFFSET
        )
        self.issue_submission.save()
        self.issue_submission._meta.get_field('date_modified').auto_now = True
        # Run
        _handle_issue_submission_action_needed()
        # Check
        assert not len(mail.outbox)

    def test_do_not_send_an_email_if_the_production_team_is_empty(self):
        # Setup
        group = Group.objects.create(name='Production team')
        ProductionTeamFactory.create(group=group, identifier='main')
        self.issue_submission.submit()
        self.issue_submission._meta.get_field('date_modified').auto_now = False
        self.issue_submission.date_modified = tz.now() - dt.timedelta(
            days=editor_settings.ACTION_NEEDED_DAY_OFFSET
        )
        self.issue_submission.save()
        self.issue_submission._meta.get_field('date_modified').auto_now = True
        # Run
        _handle_issue_submission_action_needed()
        # Check
        assert not len(mail.outbox)
