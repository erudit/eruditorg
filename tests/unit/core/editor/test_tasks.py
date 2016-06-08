# -*- coding: utf-8 -*-

import datetime as dt

from django.contrib.auth.models import Group
from django.core import mail
from django.utils import timezone as tz
from plupload.models import ResumableFile

from core.editor.conf import settings as editor_settings
from core.editor.tasks import _handle_issuesubmission_files_removal
from core.editor.test import BaseEditorTestCase


class TestHandleIssueSubmissionFilesRemoval(BaseEditorTestCase):
    def test_is_able_to_remove_files_from_archived_issue_submissions_after_30_days(self):
        # Setup
        rfile = ResumableFile.objects.create(path='dummy/path.png', filesize=42, uploadsize=42)
        self.issue_submission.last_files_version.submissions.add(rfile)
        self.issue_submission.archive()
        self.issue_submission._meta.get_field('date_modified').auto_now = False
        self.issue_submission.date_modified = tz.now() - dt.timedelta(days=30)
        self.issue_submission.save()
        self.issue_submission._meta.get_field('date_modified').auto_now = True
        # Run
        _handle_issuesubmission_files_removal()
        # Check
        self.assertFalse(ResumableFile.objects.count())

    def test_sends_an_email_to_notify_the_production_team_5_days_before_removal(self):
        # Setup
        production_team = Group.objects.create(
            name='Production team', pk=editor_settings.PRODUCTION_TEAM_GROUP_ID)
        self.user.groups.add(production_team)
        rfile = ResumableFile.objects.create(path='dummy/path.png', filesize=42, uploadsize=42)
        self.issue_submission.last_files_version.submissions.add(rfile)
        self.issue_submission.archive()
        self.issue_submission._meta.get_field('date_modified').auto_now = False
        self.issue_submission.date_modified = tz.now() - dt.timedelta(days=25)
        self.issue_submission.save()
        self.issue_submission._meta.get_field('date_modified').auto_now = True
        # Run
        _handle_issuesubmission_files_removal()
        # Check
        self.assertEqual(ResumableFile.objects.count(), 1)
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to[0], self.user.email)

    def test_do_not_send_an_email_if_the_production_team_group_does_not_exist(self):
        # Setup
        rfile = ResumableFile.objects.create(path='dummy/path.png', filesize=42, uploadsize=42)
        self.issue_submission.last_files_version.submissions.add(rfile)
        self.issue_submission.archive()
        self.issue_submission._meta.get_field('date_modified').auto_now = False
        self.issue_submission.date_modified = tz.now() - dt.timedelta(days=25)
        self.issue_submission.save()
        self.issue_submission._meta.get_field('date_modified').auto_now = True
        # Run
        _handle_issuesubmission_files_removal()
        # Check
        self.assertEqual(ResumableFile.objects.count(), 1)
        self.assertFalse(len(mail.outbox))

    def test_do_not_send_an_email_if_the_production_team_is_empty(self):
        # Setup
        Group.objects.create(
            name='Production team', pk=editor_settings.PRODUCTION_TEAM_GROUP_ID)
        rfile = ResumableFile.objects.create(path='dummy/path.png', filesize=42, uploadsize=42)
        self.issue_submission.last_files_version.submissions.add(rfile)
        self.issue_submission.archive()
        self.issue_submission._meta.get_field('date_modified').auto_now = False
        self.issue_submission.date_modified = tz.now() - dt.timedelta(days=25)
        self.issue_submission.save()
        self.issue_submission._meta.get_field('date_modified').auto_now = True
        # Run
        _handle_issuesubmission_files_removal()
        # Check
        self.assertEqual(ResumableFile.objects.count(), 1)
        self.assertFalse(len(mail.outbox))
