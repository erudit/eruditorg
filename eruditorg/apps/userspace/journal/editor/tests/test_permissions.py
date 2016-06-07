# -*- coding: utf-8 -*-

from django.contrib.contenttypes.models import ContentType
from django.core.urlresolvers import reverse

from base.factories import UserFactory
from core.authorization.defaults import AuthorizationConfig as AC
from core.authorization.models import Authorization
from core.editor.factories import IssueSubmissionFactory
from erudit.test import BaseEruditTestCase
from erudit.test.factories import JournalFactory


class ViewsTestCase(BaseEruditTestCase):

    def setUp(self):
        super(ViewsTestCase, self).setUp()
        self.user_granted = UserFactory.create(username="user_granted")
        self.user_granted.set_password("user")
        self.user_granted.save()

        self.user_non_granted = UserFactory.create(username="user_non_granted")
        self.user_non_granted.set_password("user")
        self.user_non_granted.save()

    def test_issuesubmission_restricted(self):
        self.client.login(username=self.user_non_granted.username,
                          password="user")
        url = reverse('userspace:journal:editor:issues', args=(self.journal.pk, ))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 403)

    def test_issuesubmission_granted(self):
        journal = JournalFactory(collection=self.collection)
        journal.save()
        journal.members.add(self.user_granted)

        self.client.login(username=self.user_granted.username,
                          password="user")
        url = reverse('userspace:journal:editor:issues', kwargs={'journal_pk': journal.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 403)

        ct = ContentType.objects.get(app_label="erudit", model="journal")
        Authorization.objects.create(
            content_type=ct,
            user=self.user_granted,
            object_id=journal.id,
            authorization_codename=AC.can_manage_issuesubmission.codename)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_issuesubmission_add_restricted(self):
        self.client.login(username=self.user_non_granted.username,
                          password="user")
        url = reverse('userspace:journal:editor:add', args=(self.journal.pk, ))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 403)

    def test_issuesubmission_add_granted(self):
        journal = JournalFactory(collection=self.collection)
        journal.save()
        journal.members.add(self.user_granted)

        self.client.login(username=self.user_granted.username,
                          password="user")
        url = reverse('userspace:journal:editor:add', kwargs={'journal_pk': journal.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 403)

        ct = ContentType.objects.get(app_label="erudit", model="journal")
        Authorization.objects.create(
            content_type=ct,
            user=self.user_granted,
            object_id=journal.id,
            authorization_codename=AC.can_manage_issuesubmission.codename)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_issuesubmission_update_restricted(self):
        issue = IssueSubmissionFactory(journal=self.journal)

        self.client.login(username=self.user_non_granted.username,
                          password="user")
        url = reverse('userspace:journal:editor:update', args=(self.journal.pk, issue.pk, ))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 403)

    def test_issuesubmission_update_granted(self):
        journal = JournalFactory(collection=self.collection)
        journal.save()
        journal.members.add(self.user_granted)
        issue = IssueSubmissionFactory(journal=journal)

        self.client.login(username=self.user_granted.username,
                          password="user")
        url = reverse('userspace:journal:editor:update', kwargs={
            'journal_pk': journal.pk, 'pk': issue.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 403)

        ct = ContentType.objects.get(app_label="erudit", model="journal")
        Authorization.objects.create(
            content_type=ct,
            user=self.user_granted,
            object_id=journal.id,
            authorization_codename=AC.can_manage_issuesubmission.codename)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)


class RulesTestCase(BaseEruditTestCase):

    def test_user_cant_manage(self):
        issue = IssueSubmissionFactory(journal=self.journal)
        user = UserFactory()

        is_granted = user.has_perm('editor.manage_issuesubmission',
                                   issue.journal)
        self.assertEqual(is_granted, False)

    def test_user_can_manage(self):
        journal = JournalFactory(collection=self.collection)
        user = UserFactory()
        journal.members.add(user)
        journal.save()
        ct = ContentType.objects.get(app_label="erudit", model="journal")
        Authorization.objects.create(
            content_type=ct,
            user=user,
            object_id=journal.id,
            authorization_codename=AC.can_manage_issuesubmission.codename)
        issue = IssueSubmissionFactory(journal=journal)

        is_granted = user.has_perm('editor.manage_issuesubmission',
                                   issue.journal)
        self.assertEqual(is_granted, True)

    def test_superuser_can_manage(self):
        user = UserFactory(is_superuser=True)
        issue = IssueSubmissionFactory(journal=self.journal)

        is_granted = user.has_perm('editor.manage_issuesubmission', issue)
        self.assertEqual(is_granted, True)

    def test_staff_can_manage(self):
        user = UserFactory(is_staff=True)
        issue = IssueSubmissionFactory(journal=self.journal)

        is_granted = user.has_perm('editor.manage_issuesubmission', issue)
        self.assertEqual(is_granted, True)
