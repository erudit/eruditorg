# -*- coding: utf-8 -*-

from core.editor.models import IssueSubmission
from core.editor.models import IssueSubmissionFilesVersion
from core.editor.models import IssueSubmissionStatusTrack
from core.editor.test import BaseEditorTestCase


class TestRegisterStatusTrackReceiver(BaseEditorTestCase):
    def test_creates_a_track_on_status_changes(self):
        # Run & check
        self.issue_submission.submit()
        tracks = IssueSubmissionStatusTrack.objects.filter(issue_submission=self.issue_submission)
        assert tracks.count() == 1
        assert tracks.first().status == IssueSubmission.SUBMITTED

    def test_associates_the_latest_files_version_on_submit(self):
        # Run & check
        self.issue_submission.submit()
        tracks = IssueSubmissionStatusTrack.objects.filter(issue_submission=self.issue_submission)
        assert tracks.count() == 1
        assert tracks.first().status == IssueSubmission.SUBMITTED
        files_versions = IssueSubmissionFilesVersion.objects.filter(
            issue_submission=self.issue_submission
        )
        assert files_versions.count() == 1
        assert tracks.first().files_version == files_versions.first()
