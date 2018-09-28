# -*- coding: utf-8 -*-
import pytest

import datetime as dt

from django.contrib.sessions.middleware import SessionMiddleware
from django.core.exceptions import PermissionDenied
from django.urls import resolve
from django.urls import reverse
from django.test import RequestFactory
from django.views.generic import TemplateView

from base.test.factories import UserFactory
from erudit.test.factories import OrganisationFactory

from base.test.factories import UserFactory
from core.subscription.test.factories import JournalAccessSubscriptionFactory
from core.subscription.test.factories import JournalAccessSubscriptionPeriodFactory

from apps.userspace.library.viewmixins import OrganisationScopeMixin


class MyView(OrganisationScopeMixin, TemplateView):
    template_name = 'dummy.html'


@pytest.mark.django_db
class TestOrganisationScopeMixin:

    @pytest.fixture(autouse=True)
    def setup(self):
        self.user = UserFactory()
        self.organisation = OrganisationFactory.create()
        self.organisation.members.add(self.user)
        self.subscription = JournalAccessSubscriptionFactory.create(
            organisation=self.organisation,
            post__valid=True
        )

    def get_request(self, url='/'):
        request = RequestFactory().get('/')
        middleware = SessionMiddleware()
        middleware.process_request(request)
        request.session.save()
        request.resolver_match = resolve(url)
        request.user = self.user
        return request

    def test_can_use_an_organisation_passed_in_the_url(self):
        # Setup
        url = reverse(
            'userspace:library:home', kwargs={'organisation_pk': self.organisation.pk})
        request = self.get_request(url)
        my_view = MyView.as_view()

        # Run
        response = my_view(request, organisation_pk=self.organisation.pk)

        # Check
        assert response.status_code == 200
        assert response.context_data['scope_current_organisation'] == self.organisation
        assert list(response.context_data['scope_user_organisations']) == [self.organisation, ]

    def test_can_set_last_year_of_subscription_in_context(self):
        JournalAccessSubscriptionPeriodFactory(
            subscription=self.subscription,
            start=dt.datetime.now(),
            end=dt.datetime(year=2020, month=12, day=31)
        )

        url = reverse(
            'userspace:library:home', kwargs={'organisation_pk': self.organisation.pk})

        request = self.get_request(url)
        my_view = MyView.as_view()

        # Run
        response = my_view(request, organisation_pk=self.organisation.pk)
        assert response.status_code == 200
        assert response.context_data['last_year_of_subscription'] == 2020

    def test_redirects_to_the_scoped_url_if_the_organisation_id_is_not_present_in_the_url(self):
        # Setup
        url = reverse('userspace:library:authorization:list')
        request = self.get_request(url)
        my_view = MyView.as_view()

        # Run
        response = my_view(request)

        # Check
        assert response.status_code == 302
        assert response.url == reverse(
            'userspace:library:authorization:list',
            kwargs={'organisation_pk': self.organisation.pk}
        )

    def tests_adds_subscription_status_to_the_context(self):
        url = reverse('userspace:library:home', kwargs = {'organisation_pk': self.organisation.pk})
        request = self.get_request(url)
        my_view = MyView.as_view()

        # Run
        response = my_view(request, organisation_pk=self.organisation.pk)
        assert response.status_code == 200
        assert response.context_data['has_active_subscription'] is True

        organisation = OrganisationFactory()
        organisation.members.add(self.user)
        organisation.save()
        JournalAccessSubscriptionFactory(organisation=organisation)

        # Run
        response = my_view(request, organisation_pk=organisation.pk)
        assert response.status_code == 200
        assert response.context_data['has_active_subscription'] is False

    def test_returns_a_403_error_if_no_organisation_can_be_associated_with_the_current_user(self):
        # Setup
        url = reverse(
            'userspace:library:home', kwargs={'organisation_pk': self.organisation.pk})
        request = self.get_request(url)
        request.user = UserFactory()
        my_view = MyView.as_view()

        # Run & check
        with pytest.raises(PermissionDenied):
            my_view(request, organisation_pk=self.organisation.pk)
