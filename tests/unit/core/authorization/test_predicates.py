import pytest
from django.contrib.auth.models import AnonymousUser
from django.contrib.contenttypes.models import ContentType

from base.test.factories import GroupFactory, UserFactory
from erudit.test.factories import JournalFactory
from core.authorization.defaults import AuthorizationConfig as AC
from core.authorization.predicates import HasAnyAuthorization
from core.authorization.predicates import HasAuthorization
from core.authorization.test.factories import AuthorizationFactory

pytestmark = pytest.mark.django_db


class TestHasAuthorizationPredicate:
    def test_can_check_if_a_user_has_an_authorization(self):
        user = UserFactory()
        AuthorizationFactory.create(
            user=user, authorization_codename=AC.can_manage_authorizations.codename
        )
        auth_check_1 = HasAuthorization(AC.can_manage_authorizations)
        auth_check_2 = HasAuthorization(AC.can_manage_individual_subscription)
        assert auth_check_1(user)
        assert not auth_check_2(user)

    def test_can_check_if_a_user_has_an_authorization_using_its_group(self):
        user = UserFactory()
        group = GroupFactory.create()
        user.groups.add(group)
        AuthorizationFactory.create(
            group=group, authorization_codename=AC.can_manage_authorizations.codename
        )
        auth_check_1 = HasAuthorization(AC.can_manage_authorizations)
        auth_check_2 = HasAuthorization(AC.can_manage_individual_subscription)
        assert auth_check_1(user)
        assert not auth_check_2(user)

    def test_can_check_if_a_user_has_an_authorization_on_a_specific_object(self):
        user = UserFactory()
        journal = JournalFactory()
        object_id = journal.id
        content_type = ContentType.objects.get_for_model(journal)
        AuthorizationFactory.create(
            user=user,
            authorization_codename=AC.can_manage_authorizations.codename,
            content_type=content_type,
            object_id=object_id,
        )
        auth_check_1 = HasAuthorization(AC.can_manage_authorizations)
        auth_check_2 = HasAuthorization(AC.can_manage_individual_subscription)
        assert auth_check_1(user, journal)
        assert not auth_check_2(user, journal)

    def test_can_check_if_a_user_has_an_authorization_on_a_specific_object_foreign_key(self):
        user = UserFactory()
        journal = JournalFactory()
        object_id = journal.collection.id
        content_type = ContentType.objects.get_for_model(journal.collection)
        AuthorizationFactory.create(
            user=user,
            authorization_codename=AC.can_manage_authorizations.codename,
            content_type=content_type,
            object_id=object_id,
        )
        auth_check_1 = HasAuthorization(AC.can_manage_authorizations, "collection")
        auth_check_2 = HasAuthorization(AC.can_manage_individual_subscription, "collection")
        assert auth_check_1(user, journal)
        assert not auth_check_2(user, journal)

    def test_knows_that_anonymous_users_cannot_have_authorizations(self):
        user = AnonymousUser()
        journal = JournalFactory()
        auth_check_1 = HasAuthorization(AC.can_manage_authorizations, "collection")
        auth_check_2 = HasAuthorization(AC.can_manage_individual_subscription, "collection")
        assert not auth_check_1(user, journal)
        assert not auth_check_2(user, journal)


class TestHasAnyAuthorization:
    def test_can_check_if_a_user_has_at_least_one_authorization(self):
        user = UserFactory()
        AuthorizationFactory.create(
            user=user, authorization_codename=AC.can_manage_authorizations.codename
        )
        auth_check_1 = HasAnyAuthorization(
            [AC.can_manage_authorizations, AC.can_manage_individual_subscription]
        )
        auth_check_2 = HasAnyAuthorization(
            [AC.can_manage_issuesubmission, AC.can_manage_individual_subscription]
        )
        # Run & check
        assert auth_check_1(user)
        assert not auth_check_2(user)

    def test_can_check_if_a_user_has_an_authorization_using_its_group(self):
        user = UserFactory()
        group = GroupFactory.create()
        user.groups.add(group)
        AuthorizationFactory.create(
            group=group, authorization_codename=AC.can_manage_authorizations.codename
        )
        auth_check_1 = HasAnyAuthorization(
            [
                AC.can_manage_authorizations,
            ]
        )
        auth_check_2 = HasAnyAuthorization(
            [
                AC.can_manage_individual_subscription,
            ]
        )
        assert auth_check_1(user)
        assert not auth_check_2(user)

    def test_can_check_if_a_user_has_an_authorization_on_a_specific_object(self):
        user = UserFactory()
        journal = JournalFactory()
        object_id = journal.id
        content_type = ContentType.objects.get_for_model(journal)
        AuthorizationFactory.create(
            user=user,
            authorization_codename=AC.can_manage_authorizations.codename,
            content_type=content_type,
            object_id=object_id,
        )
        auth_check_1 = HasAnyAuthorization(
            [
                AC.can_manage_authorizations,
            ]
        )
        auth_check_2 = HasAnyAuthorization(
            [
                AC.can_manage_individual_subscription,
            ]
        )
        assert auth_check_1(user, journal)
        assert not auth_check_2(user, journal)

    def test_can_check_if_a_user_has_an_authorization_on_a_specific_object_foreign_key(self):
        user = UserFactory()
        journal = JournalFactory()
        object_id = journal.collection.id
        content_type = ContentType.objects.get_for_model(journal.collection)
        AuthorizationFactory.create(
            user=user,
            authorization_codename=AC.can_manage_authorizations.codename,
            content_type=content_type,
            object_id=object_id,
        )
        auth_check_1 = HasAnyAuthorization(
            [
                AC.can_manage_authorizations,
            ],
            "collection",
        )
        auth_check_2 = HasAnyAuthorization(
            [
                AC.can_manage_individual_subscription,
            ],
            "collection",
        )
        assert auth_check_1(user, journal)
        assert not auth_check_2(user, journal)

    def test_knows_that_anonymous_users_cannot_have_authorizations(self):
        user = AnonymousUser()
        journal = JournalFactory()
        auth_check_1 = HasAnyAuthorization(
            [
                AC.can_manage_authorizations,
            ],
            "collection",
        )
        auth_check_2 = HasAnyAuthorization(
            [
                AC.can_manage_individual_subscription,
            ],
            "collection",
        )
        assert not auth_check_1(user, journal)
        assert not auth_check_2(user, journal)
