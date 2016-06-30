# -*- coding: utf-8 -*-

import os
import unittest.mock

from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.contrib.messages.middleware import MessageMiddleware
from django.contrib.sessions.middleware import SessionMiddleware
from django.core.urlresolvers import reverse
from django.http.response import HttpResponseRedirect
from django.template.response import TemplateResponse
from influxdb import InfluxDBClient
from lxml import etree
from plupload.models import ResumableFile

from core.authorization.defaults import AuthorizationConfig as AC
from core.authorization.test.factories import AuthorizationFactory
from core.editor.models import IssueSubmission
from core.editor.test import BaseEditorTestCase

from apps.userspace.journal.editor.views import IssueSubmissionApproveView
from apps.userspace.journal.editor.views import IssueSubmissionArchiveView
from apps.userspace.journal.editor.views import IssueSubmissionCreate
from apps.userspace.journal.editor.views import IssueSubmissionRefuseView

FIXTURE_ROOT = os.path.join(os.path.dirname(__file__), 'fixtures')

_test_points = []


def fake_write_points(points):
    global _test_points
    _test_points.extend(points)


class TestIssueSubmissionDetailView(BaseEditorTestCase):
    def test_includes_the_status_tracks_into_the_context(self):
        # Setup
        self.issue_submission.submit()
        self.issue_submission.refuse()
        User.objects.create_superuser(
            username='admin', email='admin@xyz.com', password='top_secret')
        self.client.login(username='admin', password='top_secret')
        url = reverse(
            'userspace:journal:editor:detail', args=(self.journal.pk, self.issue_submission.pk))
        # Run
        response = self.client.get(url)
        # Check
        assert response.status_code == 200
        assert len(response.context['status_tracks']) == 2
        assert response.context['status_tracks'][0].status == 'S'
        assert response.context['status_tracks'][1].status == 'D'


class TestIssueSubmissionView(BaseEditorTestCase):
    def tearDown(self):
        super(TestIssueSubmissionView, self).tearDown()
        global _test_points
        _test_points = []

    def test_editor_views_are_login_protected(self):
        """ Editor views should all be login protected """

        result = self.client.get(reverse('userspace:journal:editor:add', args=(self.journal.pk, )))
        self.assertIsInstance(result, HttpResponseRedirect)

        result = self.client.get(
            reverse('userspace:journal:editor:issues', args=(self.journal.pk, )))
        self.assertIsInstance(result, HttpResponseRedirect)

        result = self.client.get(
            reverse('userspace:journal:editor:update', kwargs={
                'journal_pk': self.journal.pk, 'pk': self.issue_submission.pk})
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
                'userspace:journal:editor:update',
                kwargs={'journal_pk': self.journal.pk, 'pk': self.other_issue_submission.pk}
            )
        )

        self.assertEqual(response.status_code, 403)

    def test_submit_changes_to_issue(self):
        """ Submitting changes to an issue doesn't crash.

            Previously, we would crash due to a bad reverse match.
        """
        self.client.login(
            username=self.user.username,
            password="top_secret"
        )
        url = reverse(
            'userspace:journal:editor:update',
            kwargs={'journal_pk': self.journal.pk, 'pk': self.issue_submission.pk}
        )
        response = self.client.get(url)
        root = etree.HTML(response.content)
        args = self.extract_post_args(root)
        # The issue in our DB doesn't have a year or number, but they are required, so here we go.
        args['year'] = '2016'
        args['number'] = '01'
        response = self.client.post(url, data=args)
        expected_url = reverse('userspace:journal:editor:detail',
                               args=(self.journal.pk, self.issue_submission.pk))
        self.assertRedirects(response, expected_url)

    def test_logged_add_journalsubmission(self):
        """ Logged users should be able to see journal submissions """
        self.client.login(username='david', password='top_secret')

        result = self.client.get(reverse('userspace:journal:editor:add',
                                 kwargs={'journal_pk': self.journal.pk}))
        self.assertIsInstance(
            result, TemplateResponse
        )

    def test_cannot_upload_while_adding(self):
        """ Test upload widget absence in creation

        We need to save it before the IssueSubmission before
        uploading so that file chunks are associated with the issue
        submission."""
        self.client.login(username='david', password='top_secret')
        response = self.client.get(
            reverse('userspace:journal:editor:add', kwargs={'journal_pk': self.journal.pk}))
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
            reverse('userspace:journal:editor:add', args=(self.journal.pk, )),
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
            reverse('userspace:journal:editor:update', kwargs={
                'journal_pk': self.journal.pk, 'pk': self.issue_submission.pk})
        )

        root = etree.HTML(response.content)

        self.assertTrue(
            root.cssselect('#id_submissions'),
            "The rendered upload template should contain an id_submissions input"  # noqa
        )

    def test_user_can_only_select_journal_contacts(self):
        """ Test list of contacts

        Make sure the list contains all the contacts of the publisher
        and only that """
        request = self.factory.get(
            reverse('userspace:journal:editor:add'), args=(self.journal.pk, ))
        request.user = self.user
        middleware = SessionMiddleware()
        middleware.process_request(request)
        request.session.save()
        view = IssueSubmissionCreate(request=request, journal_pk=self.journal.pk)
        view.current_journal = self.journal
        form = view.get_form()

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
        response = self.client.get(
            reverse('userspace:journal:editor:issues', args=(self.journal.pk, )), user=self.user)
        journal_ids = [j.id for j in self.user.journals.all()]
        issues = set(IssueSubmission.objects.filter(journal__in=journal_ids))
        self.assertEqual(set(response.context_data['object_list']), issues)

    @unittest.mock.patch.object(InfluxDBClient, 'get_list_database')
    @unittest.mock.patch.object(InfluxDBClient, 'create_database')
    @unittest.mock.patch.object(InfluxDBClient, 'write_points')
    def test_can_capture_a_metric_when_a_submission_is_created(
            self, mock_write_points, mock_list_db, mock_create_db):
        # Setup
        mock_write_points.side_effect = fake_write_points

        post_data = {
            'journal': self.journal.pk,
            'year': '2015',
            'volume': '2',
            'number': '2',
            'contact': self.user.pk,
            'comment': 'lorem ipsum dolor sit amet',
        }

        request = self.factory.post(
            reverse('userspace:journal:editor:add', args=(self.journal.pk, )), post_data)
        request.user = self.user
        middleware = SessionMiddleware()
        middleware.process_request(request)
        request.session.save()
        MessageMiddleware().process_request(request)
        view = IssueSubmissionCreate(request=request, journal_pk=self.journal.pk)
        view.current_journal = self.journal

        # Run
        view.post(request)

        # Check
        global _test_points
        self.assertEqual(len(_test_points), 1)
        issuesubmission = IssueSubmission.objects.last()
        self.assertEqual(
            _test_points,
            [{
                'tags': {},
                'fields': {
                    'author_id': self.user.pk,
                    'submission_id': issuesubmission.pk,
                    'num': 1,
                },
                'measurement': 'erudit__issuesubmission__create',
            }])


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
        self.issue_submission.last_files_version.submissions.add(rfile)
        url = reverse('userspace:journal:editor:attachment_detail', kwargs={'pk': rfile.pk})
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
        self.issue_submission.last_files_version.submissions.add(rfile)
        url = reverse('userspace:journal:editor:attachment_detail', kwargs={
            'journal_pk': self.journal.pk, 'pk': rfile.pk})
        # Run
        response = self.client.get(url)
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
        self.journal.members.add(user)

        self.client.login(username='dummy', password='top_secret')
        self.issue_submission.last_files_version.submissions.add(rfile)
        url = reverse('userspace:journal:editor:attachment_detail', kwargs={
            'journal_pk': self.journal.pk, 'pk': rfile.pk})
        # Run
        response = self.client.get(url)
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
        self.issue_submission.last_files_version.submissions.add(rfile)
        url = reverse('userspace:journal:editor:attachment_detail', kwargs={
            'journal_pk': self.journal.pk, 'pk': rfile.pk})
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
        self.issue_submission.last_files_version.submissions.add(rfile)
        url = reverse('userspace:journal:editor:attachment_detail', kwargs={
            'journal_pk': self.journal.pk, 'pk': rfile.pk})
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
        self.issue_submission.last_files_version.submissions.add(rfile)
        url = reverse('userspace:journal:editor:attachment_detail', kwargs={
            'journal_pk': self.journal.pk, 'pk': rfile.pk})
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
        url = reverse('userspace:journal:editor:transition_submit',
                      args=(self.journal.pk, self.issue_submission.pk, ))

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
        url = reverse('userspace:journal:editor:transition_submit', args=(
            self.journal.pk, self.issue_submission.pk, ))

        # Run
        response = self.client.post(url)

        # Check
        self.assertEqual(response.status_code, 302)
        self.issue_submission.refresh_from_db()
        self.assertEqual(self.issue_submission.status, IssueSubmission.SUBMITTED)


class TestIssueSubmissionApproveView(BaseEditorTestCase):
    def tearDown(self):
        super(TestIssueSubmissionApproveView, self).tearDown()
        global _test_points
        _test_points = []

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
        url = reverse('userspace:journal:editor:transition_approve',
                      args=(self.journal.pk, self.issue_submission.pk, ))

        # Run
        response = self.client.post(url)

        # Check
        self.assertEqual(response.status_code, 403)

    def test_can_approve_an_issue_submission(self):
        # Setup
        User.objects.create_superuser(
            username='admin', email='admin@xyz.com', password='top_secret')

        self.client.login(username='admin', password='top_secret')
        url = reverse('userspace:journal:editor:transition_approve',
                      args=(self.journal.pk, self.issue_submission.pk, ))

        self.issue_submission.submit()
        self.issue_submission.save()

        # Run
        response = self.client.post(url)

        # Check
        self.assertEqual(response.status_code, 302)
        self.issue_submission.refresh_from_db()
        self.assertEqual(self.issue_submission.status, IssueSubmission.VALID)

    @unittest.mock.patch.object(InfluxDBClient, 'get_list_database')
    @unittest.mock.patch.object(InfluxDBClient, 'create_database')
    @unittest.mock.patch.object(InfluxDBClient, 'write_points')
    def test_can_capture_a_metric_on_status_change(
            self, mock_write_points, mock_list_db, mock_create_db):
        # Setup
        mock_write_points.side_effect = fake_write_points

        self.issue_submission.submit()
        self.issue_submission.save()

        url = reverse('userspace:journal:editor:transition_approve',
                      args=(self.journal.pk, self.issue_submission.pk, ))

        request = self.factory.post(url)
        request.user = self.user
        SessionMiddleware().process_request(request)
        MessageMiddleware().process_request(request)
        request.session.save()

        view = IssueSubmissionApproveView(request=request, journal_pk=self.journal.pk)
        view.request = request
        view.kwargs = {'journal_pk': self.journal.pk, 'pk': self.issue_submission.pk}
        view.current_journal = self.journal

        # Run
        view.post(request)

        # Check
        global _test_points
        self.assertEqual(len(_test_points), 1)
        self.assertEqual(
            _test_points,
            [{
                'tags': {'old_status': 'S', 'new_status': 'V'},
                'fields': {
                    'author_id': self.user.pk,
                    'submission_id': self.issue_submission.pk,
                    'num': 1,
                },
                'measurement': 'erudit__issuesubmission__change_status',
            }])


class TestIssueSubmissionRefuseView(BaseEditorTestCase):
    def tearDown(self):
        super(TestIssueSubmissionRefuseView, self).tearDown()
        global _test_points
        _test_points = []

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
        url = reverse('userspace:journal:editor:transition_refuse',
                      args=(self.journal.pk, self.issue_submission.pk, ))

        # Run
        response = self.client.post(url)

        # Check
        self.assertEqual(response.status_code, 403)

    def test_can_refuse_an_issue_submission(self):
        # Setup
        User.objects.create_superuser(
            username='admin', email='admin@xyz.com', password='top_secret')

        self.client.login(username='admin', password='top_secret')
        url = reverse('userspace:journal:editor:transition_refuse',
                      args=(self.journal.pk, self.issue_submission.pk, ))

        self.issue_submission.submit()
        self.issue_submission.save()

        # Run
        response = self.client.post(url)

        # Check
        self.assertEqual(response.status_code, 302)
        self.assertEqual(self.issue_submission.files_versions.count(), 2)

    def test_can_refuse_an_issue_submission_with_a_comment(self):
        # Setup
        User.objects.create_superuser(
            username='admin', email='admin@xyz.com', password='top_secret')

        self.client.login(username='admin', password='top_secret')
        url = reverse('userspace:journal:editor:transition_refuse',
                      args=(self.journal.pk, self.issue_submission.pk, ))

        self.issue_submission.submit()
        self.issue_submission.save()

        # Run
        response = self.client.post(url, {'comment': 'This is a comment!'})

        # Check
        self.assertEqual(response.status_code, 302)
        self.assertEqual(self.issue_submission.files_versions.count(), 2)
        track = self.issue_submission.last_status_track
        self.assertEqual(track.comment, 'This is a comment!')

    @unittest.mock.patch.object(InfluxDBClient, 'get_list_database')
    @unittest.mock.patch.object(InfluxDBClient, 'create_database')
    @unittest.mock.patch.object(InfluxDBClient, 'write_points')
    def test_can_capture_a_metric_on_status_change(
            self, mock_write_points, mock_list_db, mock_create_db):
        # Setup
        mock_write_points.side_effect = fake_write_points

        self.issue_submission.submit()
        self.issue_submission.save()

        url = reverse('userspace:journal:editor:transition_refuse',
                      args=(self.journal.pk, self.issue_submission.pk, ))

        request = self.factory.post(url)
        request.user = self.user
        SessionMiddleware().process_request(request)
        MessageMiddleware().process_request(request)
        request.session.save()

        view = IssueSubmissionRefuseView(request=request, journal_pk=self.journal.pk)
        view.request = request
        view.kwargs = {'journal_pk': self.journal.pk, 'pk': self.issue_submission.pk}
        view.current_journal = self.journal

        # Run
        view.post(request)

        # Check
        global _test_points
        self.assertEqual(len(_test_points), 1)
        self.assertEqual(
            _test_points,
            [{
                'tags': {'old_status': 'S', 'new_status': 'D'},
                'fields': {
                    'author_id': self.user.pk,
                    'submission_id': self.issue_submission.pk,
                    'num': 1,
                },
                'measurement': 'erudit__issuesubmission__change_status',
            }])


class TestIssueSubmissionArchiveView(BaseEditorTestCase):
    def tearDown(self):
        super(TestIssueSubmissionArchiveView, self).tearDown()
        global _test_points
        _test_points = []

    def test_cannot_be_browsed_by_a_user_who_cannot_manage_issue_submissions(self):
        # Setup
        User.objects.create_user(
            username='dummy', email='dummy@xyz.com', password='top_secret')

        self.client.login(username='dummy', password='top_secret')
        url = reverse('userspace:journal:editor:transition_archive',
                      args=(self.journal.pk, self.issue_submission.pk, ))

        # Run
        response = self.client.post(url)

        # Check
        self.assertEqual(response.status_code, 403)

    def test_can_archive_an_issue_submission(self):
        # Setup
        User.objects.create_superuser(
            username='admin', email='admin@xyz.com', password='top_secret')

        self.client.login(username='admin', password='top_secret')
        url = reverse('userspace:journal:editor:transition_archive',
                      args=(self.journal.pk, self.issue_submission.pk, ))

        self.issue_submission.submit()
        self.issue_submission.save()

        # Run
        response = self.client.post(url)

        # Check
        self.assertEqual(response.status_code, 302)
        self.issue_submission.refresh_from_db()
        self.assertEqual(self.issue_submission.status, IssueSubmission.ARCHIVED)

    @unittest.mock.patch.object(InfluxDBClient, 'get_list_database')
    @unittest.mock.patch.object(InfluxDBClient, 'create_database')
    @unittest.mock.patch.object(InfluxDBClient, 'write_points')
    def test_can_capture_a_metric_on_status_change(
            self, mock_write_points, mock_list_db, mock_create_db):
        # Setup
        mock_write_points.side_effect = fake_write_points

        self.issue_submission.submit()
        self.issue_submission.save()

        url = reverse('userspace:journal:editor:transition_archive',
                      args=(self.journal.pk, self.issue_submission.pk, ))

        request = self.factory.post(url)
        request.user = self.user
        SessionMiddleware().process_request(request)
        MessageMiddleware().process_request(request)
        request.session.save()

        view = IssueSubmissionArchiveView(request=request, journal_pk=self.journal.pk)
        view.request = request
        view.kwargs = {'journal_pk': self.journal.pk, 'pk': self.issue_submission.pk}
        view.current_journal = self.journal

        # Run
        view.post(request)

        # Check
        global _test_points
        self.assertEqual(len(_test_points), 1)
        self.assertEqual(
            _test_points,
            [{
                'tags': {'old_status': 'S', 'new_status': 'A'},
                'fields': {
                    'author_id': self.user.pk,
                    'submission_id': self.issue_submission.pk,
                    'num': 1,
                },
                'measurement': 'erudit__issuesubmission__change_status',
            }])


class TestIssueSubmissionDeleteView(BaseEditorTestCase):
    def test_cannot_be_browsed_by_a_user_who_cannot_manage_issue_submissions(self):
        # Setup
        User.objects.create_user(
            username='dummy', email='dummy@xyz.com', password='top_secret')

        self.client.login(username='dummy', password='top_secret')
        url = reverse('userspace:journal:editor:delete',
                      args=(self.journal.pk, self.issue_submission.pk, ))

        # Run
        response = self.client.post(url)

        # Check
        assert response.status_code == 403

    def test_can_delete_an_issue_submission(self):
        # Setup
        User.objects.create_superuser(
            username='admin', email='admin@xyz.com', password='top_secret')

        self.client.login(username='admin', password='top_secret')
        url = reverse('userspace:journal:editor:delete',
                      args=(self.journal.pk, self.issue_submission.pk, ))
        deleted_pk = self.issue_submission.pk

        # Run
        response = self.client.post(url)

        # Check
        self.assertEqual(response.status_code, 302)
        assert deleted_pk not in IssueSubmission.objects.values_list('pk', flat=True)
