# -*- coding: utf-8 -*-
import pytest

from django.contrib.sessions.middleware import SessionMiddleware
from django.core.urlresolvers import reverse
from django.test import RequestFactory
from erudit.test import BaseEruditTestCase

from base.test.testcases import EruditClientTestCase
from base.test.factories import UserFactory
from core.accounts.test.factories import LegacyAccountProfileFactory
from core.accounts.models import LegacyAccountProfile


class TestUserPersonalDataUpdateView(EruditClientTestCase):
    def test_can_update_the_personal_data_of_a_user(self):
        # Setup
        self.client.login(username=self.user.username, password='notreallysecret')
        post_data = {
            'first_name': 'Foo',
            'last_name': 'Bar',
        }
        url = reverse('public:auth:personal_data')
        # Run
        response = self.client.post(url, post_data, follow=False)
        # Check
        assert response.status_code == 302
        self.user.refresh_from_db()
        assert self.user.first_name == 'Foo'
        assert self.user.last_name == 'Bar'


class TestUserParametersUpdateView(EruditClientTestCase):
    def test_can_update_the_account_parameters_of_a_user(self):
        # Setup
        self.client.login(username=self.user.username, password='notreallysecret')
        post_data = {
            'username': 'foobar',
            'email': 'xyz@example.com',
        }
        url = reverse('public:auth:parameters')
        # Run
        response = self.client.post(url, post_data, follow=False)
        # Check
        assert response.status_code == 302
        self.user.refresh_from_db()
        assert self.user.username == 'foobar'
        assert self.user.email == 'xyz@example.com'

    @pytest.mark.parametrize("profile_origin, expected", [
        (LegacyAccountProfile.DB_ABONNEMENTS, 302),
        (LegacyAccountProfile.DB_RESTRICTION, 403),
    ])
    def test_users_with_legacy_restriction_profile_cannot_change_username(self, profile_origin, expected):  # noqa
        user = UserFactory(password="password")

        profile = LegacyAccountProfileFactory(user=user)
        profile.origin = profile_origin
        profile.save()

        self.client.login(username=user.username, password='password')
        post_data = {
            'username': 'foobar',
            'email': 'xyz@example.com',
        }
        url = reverse('public:auth:parameters')
        # Run
        response = self.client.post(url, post_data, follow=False)
        # Check
        assert response.status_code == expected


class TestUserPasswordChangeView(BaseEruditTestCase):
    def setUp(self):
        super(TestUserPasswordChangeView, self).setUp()
        self.factory = RequestFactory()

    def get_request(self, url='/'):
        request = self.factory.get('/')
        middleware = SessionMiddleware()
        middleware.process_request(request)
        request.session.save()
        return request

    def test_can_properly_update_the_password_of_standard_users(self):
        # Setup
        self.client.login(username=self.user.username, password='top_secret')
        url = reverse('public:auth:password_change')
        post_data = {
            'old_password': 'top_secret',
            'new_password1': 'test',
            'new_password2': 'test',
        }
        # Run
        response = self.client.post(url, post_data, follow=False)
        # Check
        self.assertEqual(response.status_code, 302)
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password('test'))
