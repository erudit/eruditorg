# -*- coding: utf-8 -*-

from django.contrib.sessions.middleware import SessionMiddleware
from django.core.exceptions import PermissionDenied
from django.core.urlresolvers import resolve
from django.core.urlresolvers import reverse
from django.test import RequestFactory
from django.views.generic import TemplateView

from erudit.test import BaseEruditTestCase
from erudit.test.factories import JournalFactory

from base.test.factories import UserFactory

from apps.userspace.journal.viewmixins import JournalScopeMixin


class TestJournalScopeMixin(BaseEruditTestCase):
    def setUp(self):
        super(TestJournalScopeMixin, self).setUp()
        self.factory = RequestFactory()

    def get_request(self, url='/'):
        request = self.factory.get('/')
        middleware = SessionMiddleware()
        middleware.process_request(request)
        request.session.save()
        request.resolver_match = resolve(url)
        return request

    def test_can_use_a_journal_passed_in_the_url(self):
        # Setup
        class MyView(JournalScopeMixin, TemplateView):
            template_name = 'dummy.html'

        url = reverse(
            'userspace:journal:information:update', kwargs={'journal_pk': self.journal.pk})
        request = self.get_request(url)
        request.user = self.user
        my_view = MyView.as_view()

        # Run
        response = my_view(request, journal_pk=self.journal.pk)

        # Check
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context_data['scope_current_journal'], self.journal)
        self.assertEqual(list(response.context_data['scope_user_journals']), [self.journal, ])

    def test_redirects_to_the_scoped_url_if_the_journal_id_is_not_present_in_the_url(self):
        # Setup
        class MyView(JournalScopeMixin, TemplateView):
            template_name = 'dummy.html'

        url = reverse('userspace:journal:information:update')
        request = self.get_request(url)
        request.user = self.user
        my_view = MyView.as_view()

        # Run
        response = my_view(request)

        # Check
        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            response.url,
            reverse('userspace:journal:information:update', kwargs={'journal_pk': self.journal.pk}))

    def test_returns_a_403_error_if_no_journal_can_be_associated_with_the_current_user(self):
        # Setup
        class MyView(JournalScopeMixin, TemplateView):
            template_name = 'dummy.html'

        user = UserFactory.create()
        journal = JournalFactory.create(collection=self.collection)
        url = reverse(
            'userspace:journal:information:update', kwargs={'journal_pk': journal.pk})
        request = self.get_request(url)
        request.user = user
        my_view = MyView.as_view()

        # Run & check
        with self.assertRaises(PermissionDenied):
            my_view(request, journal_pk=self.journal.pk)
