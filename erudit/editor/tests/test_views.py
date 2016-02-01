from lxml import etree

from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.http.response import HttpResponseRedirect, HttpResponseNotFound
from django.template.response import TemplateResponse

from editor.models import IssueSubmission
from editor.views import IssueSubmissionCreate

from editor.tests.base import BaseEditorTestCase


class TestIssueSubmissionView(BaseEditorTestCase):

    def test_editor_views_are_login_protected(self):
        """ Editor views should all be login protected """

        result = self.client.get(reverse('editor:add'))
        self.assertIsInstance(result, HttpResponseRedirect)

        result = self.client.get(reverse('editor:issues'))
        self.assertIsInstance(result, HttpResponseRedirect)

        result = self.client.get(
            reverse('editor:update', kwargs={'pk': self.issue_submission.pk})
        )
        self.assertIsInstance(result, HttpResponseRedirect)

    def test_user_filtered_issuesubmissions(self):
        """ A user should only be able to see the editor's submissions
            related to his journal's membership.
        """
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
            HttpResponseNotFound,
            "The user should not be able to access another editor's submissions where he is not member"  # noqa
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
            root.cssselect('#id_submissions'),
            "The rendered template should not contain an id_submissions"  # noqa
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
            root.cssselect('#id_submissions'),
            "The rendered upload template should contain an id_submissions input"  # noqa
        )

    def test_user_is_only_allowed_to_upload_to_his_journals(self):
        """ Test list of journals in the form

        Make sure the list contains all the journals the user upload to
        and only that """
        request = self.factory.get(reverse('editor:add'))
        request.user = self.user
        form = IssueSubmissionCreate(request=request).get_form()

        user_journals = set(self.user.journals.all())

        form_journals = set(
            form.fields['journal'].queryset
        )

        self.assertEquals(
            user_journals,
            form_journals
        )

    def test_user_can_only_select_journal_contacts(self):
        """ Test list of contacts

        Make sure the list contains all the contacts of the publisher
        and only that """
        request = self.factory.get(reverse('editor:add'))
        request.user = self.user
        form = IssueSubmissionCreate(request=request).get_form()

        user_contacts = set(User.objects.filter(
            journals=self.user.journals.all()
        ).distinct())

        form_contacts = set(
            form.fields['contact'].queryset
        )

        self.assertEquals(
            user_contacts,
            form_contacts
        )

    def test_user_can_only_list_where_he_has_journal_membership(self):
        """ Test list of issue submissions

        Make sure the list contains only issue submission link to a journal
        with his membership"""
        self.client.login(username=self.user.username, password='top_secret')
        response = self.client.get(reverse('editor:issues'), user=self.user)
        journal_ids = [j.id for j in self.user.journals.all()]
        issues = set(IssueSubmission.objects.filter(journal__in=journal_ids))
        self.assertEqual(set(response.context_data['object_list']), issues)
