import pytest
from django.contrib.contenttypes.models import ContentType
from django.urls import reverse

from erudit.test.factories import JournalFactory
from base.test.factories import UserFactory
from base.test.testcases import Client
from core.authorization.defaults import AuthorizationConfig as AC
from core.authorization.models import Authorization
from core.editor.test.factories import IssueSubmissionFactory

pytestmark = pytest.mark.django_db


class TestViews:
    def test_issuesubmission_restricted(self):
        user_non_granted = UserFactory()
        journal = JournalFactory()
        client = Client(logged_user=user_non_granted)
        url = reverse('userspace:journal:editor:issues', args=(journal.pk, ))
        response = client.get(url)
        assert response.status_code == 403

    def test_issuesubmission_granted(self):
        user_granted = UserFactory()
        journal = JournalFactory()
        journal.members.add(user_granted)

        client = Client(logged_user=user_granted)
        url = reverse('userspace:journal:editor:issues', kwargs={'journal_pk': journal.pk})
        response = client.get(url)
        assert response.status_code == 403

        ct = ContentType.objects.get(app_label="erudit", model="journal")
        Authorization.objects.create(
            content_type=ct,
            user=user_granted,
            object_id=journal.id,
            authorization_codename=AC.can_manage_issuesubmission.codename)
        response = client.get(url)
        assert response.status_code == 200

    def test_issuesubmission_add_restricted(self):
        user_non_granted = UserFactory()
        journal = JournalFactory()
        client = Client(logged_user=user_non_granted)
        url = reverse('userspace:journal:editor:add', args=(journal.pk, ))
        response = client.get(url)
        assert response.status_code == 403

    def test_issuesubmission_add_granted(self):
        user_granted = UserFactory()
        journal = JournalFactory()
        journal.members.add(user_granted)

        client = Client(logged_user=user_granted)
        url = reverse('userspace:journal:editor:add', kwargs={'journal_pk': journal.pk})
        response = client.get(url)
        assert response.status_code == 403

        ct = ContentType.objects.get(app_label="erudit", model="journal")
        Authorization.objects.create(
            content_type=ct,
            user=user_granted,
            object_id=journal.id,
            authorization_codename=AC.can_manage_issuesubmission.codename)
        response = client.get(url)
        assert response.status_code == 200

    def test_issuesubmission_update_restricted(self):
        user_non_granted = UserFactory()
        issue = IssueSubmissionFactory()

        client = Client(logged_user=user_non_granted)
        url = reverse('userspace:journal:editor:update', args=(issue.journal.pk, issue.pk, ))
        response = client.get(url)
        assert response.status_code == 403

    def test_issuesubmission_update_granted(self):
        user_granted = UserFactory()
        journal = JournalFactory()
        journal.members.add(user_granted)
        issue = IssueSubmissionFactory(journal=journal)

        client = Client(logged_user=user_granted)
        url = reverse('userspace:journal:editor:update', kwargs={
            'journal_pk': journal.pk, 'pk': issue.pk})
        response = client.get(url)
        assert response.status_code == 403

        ct = ContentType.objects.get(app_label="erudit", model="journal")
        Authorization.objects.create(
            content_type=ct,
            user=user_granted,
            object_id=journal.id,
            authorization_codename=AC.can_manage_issuesubmission.codename)
        response = client.get(url)
        assert response.status_code == 200


class TestRules:

    def test_user_cant_manage(self):
        issue = IssueSubmissionFactory()
        user = UserFactory()

        is_granted = user.has_perm('editor.manage_issuesubmission',
                                   issue.journal)
        assert not is_granted

    def test_user_can_manage(self):
        journal = JournalFactory()
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
        assert is_granted

    def test_superuser_can_manage(self):
        user = UserFactory(is_superuser=True)
        issue = IssueSubmissionFactory()

        is_granted = user.has_perm('editor.manage_issuesubmission', issue)
        assert is_granted

    def test_staff_can_manage(self):
        user = UserFactory(is_staff=True)
        issue = IssueSubmissionFactory()

        is_granted = user.has_perm('editor.manage_issuesubmission', issue)
        assert is_granted
