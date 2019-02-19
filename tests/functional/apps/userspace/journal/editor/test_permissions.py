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


@pytest.mark.parametrize('permissions,code', (
    ([AC.can_manage_issuesubmission.codename], 200),
    ([], 302)
))
@pytest.mark.parametrize('view,use_issue_submission_args', (
    ('userspace:journal:editor:issues', False),
    ('userspace:journal:editor:add', False),
    ('userspace:journal:editor:update', True),
))
class TestViews:

    def test_userspace_journal_permissions(self, permissions, code, view, use_issue_submission_args):
        user_granted = UserFactory()
        journal = JournalFactory()
        journal.members.add(user_granted)
        client = Client(logged_user=user_granted)

        for permission in permissions:
            ct = ContentType.objects.get(app_label="erudit", model="journal")
            Authorization.objects.create(
                content_type=ct,
                user=user_granted,
                object_id=journal.id,
                authorization_codename=permission)

        if use_issue_submission_args:
            issue = IssueSubmissionFactory(journal=journal)
            args = (issue.journal.pk, issue.pk, )
            kwargs = {}
        else:
            args = ()
            kwargs = {'journal_pk': journal.pk}

        url = reverse(view, args=args, kwargs=kwargs)
        response = client.get(url)
        assert response.status_code == code

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
