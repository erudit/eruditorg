from datetime import datetime
from lxml import etree

from django.test import RequestFactory
from django.core.urlresolvers import reverse
from django.http.response import HttpResponseRedirect
from django.template.response import TemplateResponse

from editor.models import IssueSubmission
from erudit.tests import BaseEruditTestCase


class TestIssueSubmissionView(BaseEruditTestCase):

    def setUp(self):
        super().setUp()
        self.factory = RequestFactory()

        self.issue_submission = IssueSubmission.objects.create(
            journal=self.journal,
            volume="2",
            date_created=datetime.now(),
            contact=self.user,
            submission_file=""
        )

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
            "The rendered template should not contain an id_submission_file input"
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
            "The rendered upload template should contain an id_submission_file input"
        )
