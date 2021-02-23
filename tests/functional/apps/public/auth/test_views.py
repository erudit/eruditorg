import pytest

from django.contrib.sessions.middleware import SessionMiddleware
from django.urls import reverse
from django.test import RequestFactory

from base.test.testcases import Client
from base.test.factories import UserFactory
from core.accounts.test.factories import LegacyAccountProfileFactory
from core.accounts.models import LegacyAccountProfile

pytestmark = pytest.mark.django_db


class TestUserPersonalDataUpdateView:
    def test_can_update_the_personal_data_of_a_user(self):
        user = UserFactory()
        client = Client(logged_user=user)
        post_data = {
            "first_name": "Foo",
            "last_name": "Bar",
        }
        url = reverse("public:auth:personal_data")
        response = client.post(url, post_data, follow=False)
        assert response.status_code == 302
        user.refresh_from_db()
        assert user.first_name == "Foo"
        assert user.last_name == "Bar"


class TestUserParametersUpdateView:
    def test_can_update_the_account_parameters_of_a_user(self):
        user = UserFactory()
        client = Client(logged_user=user)
        post_data = {
            "username": "foobar",
            "email": "xyz@example.com",
        }
        url = reverse("public:auth:parameters")
        response = client.post(url, post_data, follow=False)
        assert response.status_code == 302
        user.refresh_from_db()
        assert user.username == "foobar"
        assert user.email == "xyz@example.com"

    @pytest.mark.parametrize(
        "profile_origin, expected",
        [
            (LegacyAccountProfile.DB_ABONNEMENTS, 302),
            (LegacyAccountProfile.DB_RESTRICTION, 403),
        ],
    )
    def test_users_with_legacy_restriction_profile_cannot_change_username(
        self, profile_origin, expected
    ):  # noqa
        user = UserFactory()

        profile = LegacyAccountProfileFactory(user=user)
        profile.origin = profile_origin
        profile.save()

        client = Client(logged_user=user)
        post_data = {
            "username": "foobar",
            "email": "xyz@example.com",
        }
        url = reverse("public:auth:parameters")
        response = client.post(url, post_data, follow=False)
        assert response.status_code == expected


class TestUserPasswordChangeView:
    def get_request(self, url="/"):
        request = RequestFactory().get("/")
        middleware = SessionMiddleware()
        middleware.process_request(request)
        request.session.save()
        return request

    def test_can_properly_update_the_password_of_standard_users(self):
        user = UserFactory()
        client = Client(logged_user=user)
        url = reverse("public:auth:password_change")
        post_data = {
            "old_password": user._plaintext_password,
            "new_password1": "test",
            "new_password2": "test",
        }
        response = client.post(url, post_data, follow=False)
        assert response.status_code == 302
        user.refresh_from_db()
        assert user.check_password("test")
