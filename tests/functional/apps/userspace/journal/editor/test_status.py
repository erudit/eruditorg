import pytest

from lxml import etree

from django.urls import reverse

from core.editor.models import IssueSubmission
from core.editor.test import BaseEditorTestCase


class TestIssueSubmissionStatus(BaseEditorTestCase):

    def is_disabled(self, response):
        """ Test that an editable form is present in the result """
        root = etree.HTML(response.content)
        return all([
            elem.attrib.get('disabled', False)
            for elem in root.cssselect('main input')
            if not elem.attrib['type'] == 'hidden'
        ])

    def test_a_draft_submission_is_editable(self):
        draft_submission = IssueSubmission.objects.create(
            journal=self.journal,
            volume="2",
            contact=self.user,
            status=IssueSubmission.DRAFT
        )
        result = self.client.get(
            reverse('userspace:journal:editor:update', kwargs={
                'journal_pk': self.journal.pk, 'pk': draft_submission.pk})
        )
        assert not self.is_disabled(result)

    def test_a_submitted_submission_is_editable(self):
        submitted_submission = IssueSubmission.objects.create(
            journal=self.journal,
            volume="2",
            contact=self.user,
            status=IssueSubmission.SUBMITTED
        )
        result = self.client.get(
            reverse('userspace:journal:editor:update', kwargs={
                'journal_pk': self.journal.pk, 'pk': submitted_submission.pk})
        )
        assert not self.is_disabled(result)

    def test_a_valid_submission_is_not_editable(self):
        valid_submission = IssueSubmission.objects.create(
            journal=self.journal,
            volume="2",
            contact=self.user,
            status=IssueSubmission.VALID
        )
        result = self.client.get(
            reverse('userspace:journal:editor:update', kwargs={
                'journal_pk': self.journal.pk, 'pk': valid_submission.pk})
        )
        assert self.is_disabled(result)
