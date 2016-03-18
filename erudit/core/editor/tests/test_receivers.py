# -*- coding: utf-8 -*-

from ..models import IssueSubmission
from ..models import IssueSubmissionFilesVersion
from ..models import IssueSubmissionStatusTrack

from .base import BaseEditorTestCase


class TestRegisterStatusTrackReceiver(BaseEditorTestCase):
    def test_creates_a_track_on_status_changes(self):
        # Run & check
        self.issue_submission.submit()
        tracks = IssueSubmissionStatusTrack.objects.filter(issue_submission=self.issue_submission)
        self.assertEqual(tracks.count(), 1)
        self.assertEqual(tracks.first().status, IssueSubmission.SUBMITTED)

    def test_associates_the_latest_files_version_on_submit(self):
        # Run & check
        self.issue_submission.submit()
        tracks = IssueSubmissionStatusTrack.objects.filter(issue_submission=self.issue_submission)
        self.assertEqual(tracks.count(), 1)
        self.assertEqual(tracks.first().status, IssueSubmission.SUBMITTED)
        files_versions = IssueSubmissionFilesVersion.objects.filter(
            issue_submission=self.issue_submission)
        self.assertEqual(files_versions.count(), 1)
        self.assertEqual(tracks.first().files_version, files_versions.first())

    def test_associates_the_latest_files_version_on_refusal(self):
        # Run & check
        self.issue_submission.submit()
        self.issue_submission.refuse()
        tracks = IssueSubmissionStatusTrack.objects.filter(issue_submission=self.issue_submission)
        self.assertEqual(tracks.count(), 2)
        self.assertEqual(tracks.last().status, IssueSubmission.DRAFT)
        files_versions = IssueSubmissionFilesVersion.objects.filter(
            issue_submission=self.issue_submission)
        self.assertEqual(files_versions.count(), 2)
        self.assertEqual(tracks.last().files_version, self.issue_submission.last_files_version)
