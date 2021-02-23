import pytest
from django.contrib.contenttypes.models import ContentType

from erudit.test.factories import JournalFactory

from base.test.factories import UserFactory
from core.authorization.defaults import AuthorizationConfig as AC
from core.authorization.models import Authorization

pytestmark = pytest.mark.django_db


def test_knows_if_a_user_cannot_manage_authorizations():
    user = UserFactory()
    journal = JournalFactory()
    is_granted = user.has_perm("authorization.manage_authorizations", journal)
    assert not is_granted

    journal.members.add(user)
    journal.save()
    is_granted = user.has_perm("authorization.manage_authorizations", journal)
    assert not is_granted


def test_knows_if_a_user_can_manage_authorizations():
    user = UserFactory()
    journal = JournalFactory()
    journal.members.add(user)
    journal.save()
    ct = ContentType.objects.get(app_label="erudit", model="journal")
    Authorization.objects.create(
        content_type=ct,
        user=user,
        object_id=journal.id,
        authorization_codename=AC.can_manage_authorizations.codename,
    )
    is_granted = user.has_perm("authorization.manage_authorizations", journal)
    assert is_granted


def test_knows_that_a_superuser_can_manage_authorizations():
    user = UserFactory(is_superuser=True)
    journal = JournalFactory()
    is_granted = user.has_perm("authorization.manage_authorizations", journal)
    assert is_granted


def test_knows_that_a_staff_member_can_manage_authorizations():
    user = UserFactory(is_staff=True)
    journal = JournalFactory()
    is_granted = user.has_perm("authorization.manage_authorizations", journal)
    assert is_granted
