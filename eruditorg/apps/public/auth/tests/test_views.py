# -*- coding: utf-8 -*-

from django.contrib.sessions.middleware import SessionMiddleware
from django.core.urlresolvers import reverse
from django.test import RequestFactory

from core.accounts.factories import AbonnementProfileFactory
from erudit.tests.base import BaseEruditTestCase


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

    def test_can_properly_update_the_password_of_abonnementprofile_users(self):
        # Setup
        self.user.set_unusable_password()
        self.user.save()
        profile = AbonnementProfileFactory.create(user=self.user)
        profile.password = profile.sha1('test-1')
        profile.save()
        self.client.login(username=self.user.username, password='test-1')
        url = reverse('public:auth:password_change')
        post_data = {
            'old_password': 'test-1',
            'new_password1': 'test',
            'new_password2': 'test',
        }
        # Run
        response = self.client.post(url, post_data, follow=False)
        # Check
        self.assertEqual(response.status_code, 302)
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password('test'))
