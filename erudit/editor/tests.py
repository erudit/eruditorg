from datetime import datetime

from django.test import TestCase, RequestFactory
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

