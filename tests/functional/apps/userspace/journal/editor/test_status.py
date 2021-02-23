import pytest

from lxml import etree

from django.urls import reverse

from core.editor.models import IssueSubmission
from core.editor.test import BaseEditorTestCase


class TestIssueSubmissionStatus(BaseEditorTestCase):
    def is_disabled(self, response):
        """ Test that an editable form is present in the result """
        root = etree.HTML(response.content)
        return all(
            [
                elem.attrib.get("disabled", False)
                for elem in root.cssselect("main input")
                if not elem.attrib["type"] == "hidden"
            ]
        )

    @pytest.mark.parametrize(
        "status, expected_is_disabled",
        (
            (IssueSubmission.DRAFT, False),
            (IssueSubmission.SUBMITTED, False),
            (IssueSubmission.NEEDS_CORRECTIONS, False),
            (IssueSubmission.VALID, True),
        ),
    )
    def test_issue_submission_is_editable_by_status(self, status, expected_is_disabled):
        issue_submission = IssueSubmission.objects.create(
            journal=self.journal,
            volume="2",
            contact=self.user,
            status=status,
        )
        url = reverse(
            "userspace:journal:editor:update",
            kwargs={
                "journal_pk": self.journal.pk,
                "pk": issue_submission.pk,
            },
        )
        result = self.client.get(url)
        assert self.is_disabled(result) == expected_is_disabled
