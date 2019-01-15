from lxml import etree

from django.urls import reverse

from base.test.testcases import Client
from core.editor.models import IssueSubmission
from core.editor.test import BaseEditorTestCase


class TestIssueSubmissionStatus(BaseEditorTestCase):

    def setUp(self):
        super().setUp()

        # We need to be logged in for all the tests
        self.client = Client(logged_user=self.user)

        self.draft_submission = IssueSubmission.objects.create(
            journal=self.journal,
            volume="2",
            contact=self.user,
            status=IssueSubmission.DRAFT
        )

        self.submitted_submission = IssueSubmission.objects.create(
            journal=self.journal,
            volume="2",
            contact=self.user,
            status=IssueSubmission.SUBMITTED
        )

        self.valid_submission = IssueSubmission.objects.create(
            journal=self.journal,
            volume="2",
            contact=self.user,
            status=IssueSubmission.VALID
        )

    def is_disabled(self, response):
        """ Test that an editable form is present in the result """
        root = etree.HTML(response.content)
        return all([
            elem.attrib.get('disabled', False)
            for elem in root.cssselect('input')
            if not elem.attrib['type'] == 'hidden'
        ])

    def test_a_draft_submission_is_editable(self):
        result = self.client.get(
            reverse('userspace:journal:editor:update', kwargs={
                'journal_pk': self.journal.pk, 'pk': self.draft_submission.pk})
        )

        self.assertFalse(
            self.is_disabled(result),
            "Draft IssueSubmissions are editable"
        )

    def test_a_submitted_submission_is_not_editable(self):
        result = self.client.get(
            reverse('userspace:journal:editor:update', kwargs={
                'journal_pk': self.journal.pk, 'pk': self.submitted_submission.pk})
        )

        self.assertTrue(
            self.is_disabled(result),
            "Submitted IssueSubmissions are not editable"
        )

    def test_a_valid_submission_is_not_editable(self):
        result = self.client.get(
            reverse('userspace:journal:editor:update', kwargs={
                'journal_pk': self.journal.pk, 'pk': self.valid_submission.pk})
        )

        self.assertTrue(
            self.is_disabled(result),
            "Valid IssueSubmissions are not editable"
        )

    def test_post_on_a_non_draft_submission_does_not_modify(self):
        pass
