# -*- coding: utf-8 -*-

import datetime as dt

from django.contrib.sessions.middleware import SessionMiddleware
from django.core.exceptions import PermissionDenied
from django.core.urlresolvers import resolve
from django.core.urlresolvers import reverse
from django.test import RequestFactory
from django.views.generic import TemplateView

from erudit.test import BaseEruditTestCase
from erudit.test.factories import OrganisationFactory

from base.test.factories import UserFactory
from core.subscription.test.factories import JournalAccessSubscriptionFactory
from core.subscription.test.factories import JournalAccessSubscriptionPeriodFactory

from apps.userspace.library.viewmixins import OrganisationScopeMixin


class TestOrganisationScopeMixin(BaseEruditTestCase):
    def setUp(self):
        super(TestOrganisationScopeMixin, self).setUp()
        self.factory = RequestFactory()
        self.organisation = OrganisationFactory.create()
        self.organisation.members.add(self.user)
        self.subscription = JournalAccessSubscriptionFactory.create(organisation=self.organisation)
        now_dt = dt.datetime.now()
        JournalAccessSubscriptionPeriodFactory.create(
            subscription=self.subscription,
            start=now_dt - dt.timedelta(days=10),
            end=now_dt + dt.timedelta(days=8))

    def get_request(self, url='/'):
        request = self.factory.get('/')
        middleware = SessionMiddleware()
        middleware.process_request(request)
        request.session.save()
        request.resolver_match = resolve(url)
        return request

    def test_can_use_an_organisation_passed_in_the_url(self):
        # Setup
        class MyView(OrganisationScopeMixin, TemplateView):
            template_name = 'dummy.html'

        url = reverse(
            'userspace:library:home', kwargs={'organisation_pk': self.organisation.pk})
        request = self.get_request(url)
        request.user = self.user
        my_view = MyView.as_view()

        # Run
        response = my_view(request, organisation_pk=self.organisation.pk)

        # Check
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context_data['scope_current_organisation'], self.organisation)
        self.assertEqual(
            list(response.context_data['scope_user_organisations']), [self.organisation, ])

    def test_can_set_last_year_of_subscription_in_context(self):
        class MyView(OrganisationScopeMixin, TemplateView):
            template_name = 'dummy.html'

        subscription = JournalAccessSubscriptionFactory(organisation=self.organisation, post__valid=True)
        JournalAccessSubscriptionPeriodFactory(
            subscription=subscription,
            start=dt.datetime.now(),
            end=dt.datetime(year=2020, month=12, day=31)
        )

        url = reverse(
            'userspace:library:home', kwargs={'organisation_pk': self.organisation.pk})

        request = self.get_request(url)
        request.user = self.user
        my_view = MyView.as_view()

        # Run
        response = my_view(request, organisation_pk=self.organisation.pk)
        assert response.status_code == 200
        assert response.context_data['last_year_of_subscription'] == 2020

    def test_redirects_to_the_scoped_url_if_the_organisation_id_is_not_present_in_the_url(self):
        # Setup
        class MyView(OrganisationScopeMixin, TemplateView):
            template_name = 'dummy.html'

        url = reverse('userspace:library:authorization:list')
        request = self.get_request(url)
        request.user = self.user
        my_view = MyView.as_view()

        # Run
        response = my_view(request)

        # Check
        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            response.url,
            reverse('userspace:library:authorization:list',
                    kwargs={'organisation_pk': self.organisation.pk}))

    def test_returns_a_403_error_if_no_organisation_can_be_associated_with_the_current_user(self):
        # Setup
        class MyView(OrganisationScopeMixin, TemplateView):
            template_name = 'dummy.html'

        user = UserFactory.create()
        url = reverse(
            'userspace:library:home', kwargs={'organisation_pk': self.organisation.pk})
        request = self.get_request(url)
        request.user = user
        my_view = MyView.as_view()

        # Run & check
        with self.assertRaises(PermissionDenied):
            my_view(request, organisation_pk=self.organisation.pk)
