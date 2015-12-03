from datetime import datetime
from lxml import etree

from django.core.urlresolvers import reverse
from django.http.response import HttpResponseRedirect
from django.template.response import TemplateResponse

from editor.models import IssueSubmission
from erudit.tests import BaseEruditTestCase


class BaseEditorTestCase(BaseEruditTestCase):

    def setUp(self):
        super().setUp()

        self.issue_submission = IssueSubmission.objects.create(
            journal=self.journal,
            volume="2",
            date_created=datetime.now(),
            contact=self.user,
            submission_file=""
        )

        self.other_issue_submission = IssueSubmission.objects.create(
            journal=self.other_journal,
            volume="2",
            date_created=datetime.now(),
            contact=self.user,
            submission_file=""
        )


class TestIssueSubmissionStatus(BaseEditorTestCase):

    def setUp(self):
        super().setUp()

        # We need to be logged in for all the tests
        self.client.login(username='david', password='top_secret')

        self.draft_submission = IssueSubmission.objects.create(
            journal=self.journal,
            volume="2",
            date_created=datetime.now(),
            contact=self.user,
            submission_file="",
            status=IssueSubmission.DRAFT
        )

        self.submitted_submission = IssueSubmission.objects.create(
            journal=self.journal,
            volume="2",
            date_created=datetime.now(),
            contact=self.user,
            submission_file="",
            status=IssueSubmission.SUBMITTED
        )

        self.valid_submission = IssueSubmission.objects.create(
            journal=self.journal,
            volume="2",
            date_created=datetime.now(),
            contact=self.user,
            submission_file="",
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
            reverse('editor:update', kwargs={'pk': self.draft_submission.pk})
        )

        self.assertFalse(
            self.is_disabled(result),
            "Draft IssueSubmissions are editable"
        )

    def test_a_submitted_submission_is_not_editable(self):
        result = self.client.get(
            reverse('editor:update', kwargs={'pk': self.submitted_submission.pk})
        )

        self.assertTrue(
            self.is_disabled(result),
            "Submitted IssueSubmissions are not editable"
        )

    def test_a_valid_submission_is_not_editable(self):
        result = self.client.get(
            reverse('editor:update', kwargs={'pk': self.valid_submission.pk})
        )

        self.assertTrue(
            self.is_disabled(result),
            "Valid IssueSubmissions are not editable"
        )

    def test_post_on_a_non_draft_submission_does_not_modify(self):
        pass


class TestIssueSubmissionView(BaseEditorTestCase):

    def test_editor_views_are_login_protected(self):
        """ Editor views should all be login protected """

        result = self.client.get(reverse('editor:add'))
        self.assertIsInstance(result, HttpResponseRedirect)

        result = self.client.get(reverse('editor:dashboard'))
        self.assertIsInstance(result, HttpResponseRedirect)

        result = self.client.get(
            reverse('editor:update', kwargs={'pk': self.issue_submission.pk})
        )
        self.assertIsInstance(result, HttpResponseRedirect)

    def test_user_can_only_access_his_submissions(self):
        """ A user should only be able to see his editor's submissions """
        login = self.client.login(
            username=self.user.username,
            password="top_secret"
        )

        self.assertTrue(
            login
        )

        response = self.client.get(
            reverse(
                'editor:update',
                kwargs={'pk': self.other_issue_submission.pk}
            )
        )

        self.assertIsInstance(
            response,
            HttpResponseRedirect,
            "The user should not be able to access another editor's submissions"  # noqa
        )

    def test_logged_add_journalsubmission(self):
        """ Logged users should be able to see journal submissions """
        self.client.login(username='david', password='top_secret')

        result = self.client.get(reverse('editor:add'))
        self.assertIsInstance(
            result, TemplateResponse
        )

    def test_cannot_upload_while_adding(self):
        """ Test upload widget absence in creation

        We need to save it before the IssueSubmission before
        uploading so that file chunks are associated with the issue
        submission."""
        self.client.login(username='david', password='top_secret')
        response = self.client.get(reverse('editor:add'))
        root = etree.HTML(response.content)
        self.assertFalse(
            root.cssselect('#id_submission_file'),
            "The rendered template should not contain an id_submission_file input"  # noqa
        )

    def test_can_create_issuesubmission(self):
        """ Test that we can create an issue submission
        """
        issue_submission_count = IssueSubmission.objects.count()

        data = {
            'journal': self.journal.pk,
            'year': '2015',
            'volume': '2',
            'number': '2',
            'contact': self.user.pk,
            'comment': 'lorem ipsum dolor sit amet',
        }

        self.client.login(username='david', password='top_secret')

        self.client.post(
            reverse('editor:add'),
            data
        )

        self.assertEquals(
            IssueSubmission.objects.count(),
            issue_submission_count + 1,
            "An issue submission should have been added"
        )

    def test_can_upload_while_updating(self):
        """ Test upload widget presence in update

        The file upload widget should be present on update forms.
        Files are uploaded to an existing IssueSubmission so
        progress can be tracked.
        """
        self.client.login(username='david', password='top_secret')

        response = self.client.get(
            reverse('editor:update', kwargs={'pk': self.issue_submission.pk})
        )

        root = etree.HTML(response.content)

        self.assertTrue(
            root.cssselect('#id_submission_file'),
            "The rendered upload template should contain an id_submission_file input"  # noqa
        )
