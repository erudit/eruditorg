# -*- coding: utf-8 -*-

import os

from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.core.urlresolvers import reverse
from django.http.response import HttpResponseNotFound
from django.http.response import HttpResponseRedirect
from django.template.response import TemplateResponse
from lxml import etree
from plupload.models import ResumableFile

from core.authorization.defaults import AuthorizationConfig as AC
from core.authorization.factories import AuthorizationFactory
from core.editor.models import IssueSubmission
from core.editor.tests.base import BaseEditorTestCase

from ..views import IssueSubmissionCreate

FIXTURE_ROOT = os.path.join(os.path.dirname(__file__), 'fixtures')


class TestIssueSubmissionView(BaseEditorTestCase):

    def test_editor_views_are_login_protected(self):
        """ Editor views should all be login protected """

        result = self.client.get(reverse('userspace:editor:add'))
        self.assertIsInstance(result, HttpResponseRedirect)

        result = self.client.get(reverse('userspace:editor:issues'))
        self.assertIsInstance(result, HttpResponseRedirect)

        result = self.client.get(
            reverse('userspace:editor:update', kwargs={'pk': self.issue_submission.pk})
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
                'userspace:editor:update',
                kwargs={'pk': self.other_issue_submission.pk}
            )
        )

        self.assertIsInstance(
            response,
            HttpResponseNotFound,
            "The user should not be able to access another editor's submissions where he is not member"  # noqa
        )

    def test_sumit_changes_to_issue(self):
        """ Submitting changes to an issue doesn't crash.

            Previously, we would crash due to a bad reverse match.
        """
        self.client.login(
            username=self.user.username,
            password="top_secret"
        )
        url = reverse(
            'userspace:editor:update',
            kwargs={'pk': self.issue_submission.pk}
        )
        response = self.client.get(url)
        root = etree.HTML(response.content)
        args = self.extract_post_args(root)
        # The issue in our DB doesn't have a year or number, but they are required, so here we go.
        args['year'] = '2016'
        args['number'] = '01'
        response = self.client.post(url, data=args)
        expected_url = reverse('userspace:editor:issues')
        self.assertRedirects(response, expected_url)

    def test_logged_add_journalsubmission(self):
        """ Logged users should be able to see journal submissions """
        self.client.login(username='david', password='top_secret')

        result = self.client.get(reverse('userspace:editor:add'))
        self.assertIsInstance(
            result, TemplateResponse
        )

    def test_cannot_upload_while_adding(self):
        """ Test upload widget absence in creation

        We need to save it before the IssueSubmission before
        uploading so that file chunks are associated with the issue
        submission."""
        self.client.login(username='david', password='top_secret')
        response = self.client.get(reverse('userspace:editor:add'))
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
            reverse('userspace:editor:add'),
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
            reverse('userspace:editor:update', kwargs={'pk': self.issue_submission.pk})
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
        request = self.factory.get(reverse('userspace:editor:add'))
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
        request = self.factory.get(reverse('userspace:editor:add'))
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
        response = self.client.get(reverse('userspace:editor:issues'), user=self.user)
        journal_ids = [j.id for j in self.user.journals.all()]
        issues = set(IssueSubmission.objects.filter(journal__in=journal_ids))
        self.assertEqual(set(response.context_data['object_list']), issues)


class TestIssueSubmissionAttachmentView(BaseEditorTestCase):
    def test_cannot_be_browsed_by_users_who_cannot_download_submission_files(self):
        # Setup
        with open(os.path.join(FIXTURE_ROOT, 'pixel.png'), mode='rb') as f:
            rfile = ResumableFile.objects.create(
                path=os.path.join(FIXTURE_ROOT, 'pixel.png'),
                filesize=f.tell(), uploadsize=f.tell())

        User.objects.create_user(
            username='dummy', email='dummy@xyz.com', password='top_secret')
        self.client.login(username='dummy', password='top_secret')
        self.issue_submission.submissions.add(rfile)
        url = reverse('userspace:editor:attachment-detail', args=(rfile.pk, ))
        # Run
        response = self.client.get(url, follow=False)
        # Check
        self.assertEqual(response.status_code, 403)

    def test_can_be_browsed_by_users_who_can_manage_issue_submissions(self):
        # Setup
        with open(os.path.join(FIXTURE_ROOT, 'pixel.png'), mode='rb') as f:
            rfile = ResumableFile.objects.create(
                path=os.path.join(FIXTURE_ROOT, 'pixel.png'),
                filesize=f.tell(), uploadsize=f.tell())

        user = User.objects.create_user(
            username='dummy', email='dummy@xyz.com', password='top_secret')
        self.journal.members.add(user)
        AuthorizationFactory.create(
            content_type=ContentType.objects.get_for_model(self.journal),
            object_id=self.journal.id,
            user=user,
            authorization_codename=AC.can_manage_issuesubmission.codename)

        self.client.login(username='dummy', password='top_secret')
        self.issue_submission.submissions.add(rfile)
        url = reverse('userspace:editor:attachment-detail', args=(rfile.pk, ))
        # Run
        response = self.client.get(url, follow=False)
        # Check
        self.assertEqual(response.status_code, 200)

    def test_can_be_browsed_by_users_who_can_review_issue_submissions(self):
        # Setup
        with open(os.path.join(FIXTURE_ROOT, 'pixel.png'), mode='rb') as f:
            rfile = ResumableFile.objects.create(
                path=os.path.join(FIXTURE_ROOT, 'pixel.png'),
                filesize=f.tell(), uploadsize=f.tell())

        user = User.objects.create_user(
            username='dummy', email='dummy@xyz.com', password='top_secret')
        AuthorizationFactory.create(
            user=user, authorization_codename=AC.can_review_issuesubmission.codename)

        self.client.login(username='dummy', password='top_secret')
        self.issue_submission.submissions.add(rfile)
        url = reverse('userspace:editor:attachment-detail', args=(rfile.pk, ))
        # Run
        response = self.client.get(url, follow=False)
        # Check
        self.assertEqual(response.status_code, 200)

    def test_embed_the_correct_http_headers_in_the_response(self):
        # Setup
        with open(os.path.join(FIXTURE_ROOT, 'pixel.png'), mode='rb') as f:
            rfile = ResumableFile.objects.create(
                path=os.path.join(FIXTURE_ROOT, 'pixel.png'),
                filesize=f.tell(), uploadsize=f.tell())

        User.objects.create_superuser(
            username='admin', email='admin@xyz.com', password='top_secret')
        self.client.login(username='admin', password='top_secret')
        self.issue_submission.submissions.add(rfile)
        url = reverse('userspace:editor:attachment-detail', args=(rfile.pk, ))
        # Run
        response = self.client.get(url)
        # Check
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'image/png')
        self.assertEqual(response['Content-Disposition'], 'attachment; filename=pixel.png')

    def test_is_able_to_handle_unknown_file_content_types(self):
        # Setup
        with open(os.path.join(FIXTURE_ROOT, 'dummy.kyz'), mode='rb') as f:
            rfile = ResumableFile.objects.create(
                path=os.path.join(FIXTURE_ROOT, 'dummy.kyz'),
                filesize=f.tell(), uploadsize=f.tell())

        User.objects.create_superuser(
            username='admin', email='admin@xyz.com', password='top_secret')
        self.client.login(username='admin', password='top_secret')
        self.issue_submission.submissions.add(rfile)
        url = reverse('userspace:editor:attachment-detail', args=(rfile.pk, ))
        # Run
        response = self.client.get(url)
        # Check
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'text/plain')
        self.assertEqual(response['Content-Disposition'], 'attachment; filename=dummy.kyz')

    def test_raises_http404_if_the_file_does_not_exist(self):
        # Setup
        rfile = ResumableFile.objects.create(
            path='/dummy/dummy.png', filesize=1, uploadsize=1)
        User.objects.create_superuser(
            username='admin', email='admin@xyz.com', password='top_secret')
        self.client.login(username='admin', password='top_secret')
        self.issue_submission.submissions.add(rfile)
        url = reverse('userspace:editor:attachment-detail', args=(rfile.pk, ))
        # Run
        response = self.client.get(url)
        # Check
        self.assertEqual(response.status_code, 404)


class TestIssueSubmissionSubmitView(BaseEditorTestCase):
    def test_cannot_be_browsed_by_a_user_who_cannot_manage_issue_submissions(self):
        # Setup
        User.objects.create_user(
            username='dummy', email='dummy@xyz.com', password='top_secret')

        self.client.login(username='dummy', password='top_secret')
        url = reverse('userspace:editor:transition-submit', args=(self.issue_submission.pk, ))

        # Run
        response = self.client.post(url)

        # Check
        self.assertEqual(response.status_code, 403)

    def test_can_submit_an_issue_submission(self):
        # Setup
        user = User.objects.create_user(
            username='dummy', email='dummy@xyz.com', password='top_secret')
        self.journal.members.add(user)
        AuthorizationFactory.create(
            content_type=ContentType.objects.get_for_model(self.journal),
            object_id=self.journal.id,
            user=user,
            authorization_codename=AC.can_manage_issuesubmission.codename)

        self.client.login(username='dummy', password='top_secret')
        url = reverse('userspace:editor:transition-submit', args=(self.issue_submission.pk, ))

        # Run
        response = self.client.post(url)

        # Check
        self.assertEqual(response.status_code, 302)
        self.issue_submission.refresh_from_db()
        self.assertEqual(self.issue_submission.status, IssueSubmission.SUBMITTED)


class TestIssueSubmissionApproveView(BaseEditorTestCase):
    def test_cannot_be_browsed_by_a_user_who_cannot_review_issue_submissions(self):
        # Setup
        user = User.objects.create_user(
            username='dummy', email='dummy@xyz.com', password='top_secret')
        self.journal.members.add(user)
        AuthorizationFactory.create(
            content_type=ContentType.objects.get_for_model(self.journal),
            object_id=self.journal.id,
            user=user,
            authorization_codename=AC.can_manage_issuesubmission.codename)

        self.client.login(username='dummy', password='top_secret')
        url = reverse('userspace:editor:transition-approve', args=(self.issue_submission.pk, ))

        # Run
        response = self.client.post(url)

        # Check
        self.assertEqual(response.status_code, 403)

    def test_can_approve_an_issue_submission(self):
        # Setup
        User.objects.create_superuser(
            username='admin', email='admin@xyz.com', password='top_secret')

        self.client.login(username='admin', password='top_secret')
        url = reverse('userspace:editor:transition-approve', args=(self.issue_submission.pk, ))

        self.issue_submission.submit()
        self.issue_submission.save()

        # Run
        response = self.client.post(url)

        # Check
        self.assertEqual(response.status_code, 302)
        self.issue_submission.refresh_from_db()
        self.assertEqual(self.issue_submission.status, IssueSubmission.VALID)


class TestIssueSubmissionRefuseView(BaseEditorTestCase):
    def test_cannot_be_browsed_by_a_user_who_cannot_review_issue_submissions(self):
        # Setup
        user = User.objects.create_user(
            username='dummy', email='dummy@xyz.com', password='top_secret')
        self.journal.members.add(user)
        AuthorizationFactory.create(
            content_type=ContentType.objects.get_for_model(self.journal),
            object_id=self.journal.id,
            user=user,
            authorization_codename=AC.can_manage_issuesubmission.codename)

        self.client.login(username='dummy', password='top_secret')
        url = reverse('userspace:editor:transition-refuse', args=(self.issue_submission.pk, ))

        # Run
        response = self.client.post(url)

        # Check
        self.assertEqual(response.status_code, 403)

    def test_can_refuse_an_issue_submission(self):
        # Setup
        User.objects.create_superuser(
            username='admin', email='admin@xyz.com', password='top_secret')

        self.client.login(username='admin', password='top_secret')
        url = reverse('userspace:editor:transition-refuse', args=(self.issue_submission.pk, ))

        self.issue_submission.submit()
        self.issue_submission.save()

        # Run
        response = self.client.post(url)

        # Check
        self.assertEqual(response.status_code, 302)
        new_version = IssueSubmission.head.first()
        self.assertEqual(new_version.status, IssueSubmission.DRAFT)


class TestIssueSubmissionArchiveView(BaseEditorTestCase):
    def test_cannot_be_browsed_by_a_user_who_cannot_manage_issue_submissions(self):
        # Setup
        User.objects.create_user(
            username='dummy', email='dummy@xyz.com', password='top_secret')

        self.client.login(username='dummy', password='top_secret')
        url = reverse('userspace:editor:transition-archive', args=(self.issue_submission.pk, ))

        # Run
        response = self.client.post(url)

        # Check
        self.assertEqual(response.status_code, 403)

    def test_can_archive_an_issue_submission(self):
        # Setup
        User.objects.create_superuser(
            username='admin', email='admin@xyz.com', password='top_secret')

        self.client.login(username='admin', password='top_secret')
        url = reverse('userspace:editor:transition-archive', args=(self.issue_submission.pk, ))

        self.issue_submission.submit()
        self.issue_submission.save()

        # Run
        response = self.client.post(url)

        # Check
        self.assertEqual(response.status_code, 302)
        self.issue_submission.refresh_from_db()
        self.assertEqual(self.issue_submission.status, IssueSubmission.ARCHIVED)
