# -*- coding: utf-8 -*-

import datetime as dt

from django.contrib.auth.models import AnonymousUser
from django.http import Http404
from django.test import RequestFactory

from erudit.test import BaseEruditTestCase
from erudit.test.factories import ArticleFactory
from erudit.test.factories import IssueFactory
from erudit.test.factories import OrganisationFactory

from core.subscription.test.factories import InstitutionIPAddressRangeFactory
from core.subscription.test.factories import JournalAccessSubscriptionFactory
from core.subscription.test.factories import JournalAccessSubscriptionPeriodFactory

from core.journal.viewmixins import ArticleAccessCheckMixin
from core.journal.viewmixins import SingleJournalMixin


class TestSingleJournalMixin(BaseEruditTestCase):
    def test_can_return_a_journal_based_on_its_code(self):
        # Setup
        code = self.journal.code
        mixin = SingleJournalMixin()
        mixin.kwargs = {'code': code}
        # Run & check
        self.assertEqual(mixin.get_object(), self.journal)

    def test_returns_http_404_if_the_journal_does_not_exist(self):
        # Setup
        code = self.journal.code
        mixin = SingleJournalMixin()
        mixin.kwargs = {'code': code + 'dummy'}
        # Run & check
        with self.assertRaises(Http404):
            mixin.get_object()


class TestArticleAccessCheckMixin(BaseEruditTestCase):
    def setUp(self):
        super(TestArticleAccessCheckMixin, self).setUp()
        self.factory = RequestFactory()

    def test_do_not_grant_access_by_default(self):
        # Setup
        self.journal.open_access = False
        self.journal.save()
        issue = IssueFactory.create(
            journal=self.journal, year=dt.datetime.now().year,
            date_published=dt.datetime.now(), localidentifier='test')
        article = ArticleFactory.create(issue=issue)

        class MyView(ArticleAccessCheckMixin):
            def get_article(self):
                return article

        request = self.factory.get('/')
        request.user = AnonymousUser()

        view = MyView()
        view.request = request

        # Run # check
        self.assertFalse(view.has_access())

    def test_can_grant_access_to_an_article_if_it_is_in_open_access(self):
        # Setup
        self.journal.open_access = True
        self.journal.save()
        issue = IssueFactory.create(
            journal=self.journal, year=dt.datetime.now().year, date_published=dt.datetime.now(),
            localidentifier='test')
        article = ArticleFactory.create(issue=issue)

        class MyView(ArticleAccessCheckMixin):
            def get_article(self):
                return article

        request = self.factory.get('/')
        request.user = AnonymousUser()
        view = MyView()
        view.request = request

        # Run # check
        self.assertTrue(view.has_access())

    def test_can_grant_access_to_an_article_has_no_movable_limitation(self):
        # Setup
        now_dt = dt.datetime.now()

        self.journal.open_access = False
        self.journal.save()
        issue = IssueFactory.create(
            journal=self.journal, year=dt.datetime.now().year - 5,
            date_published=dt.date(now_dt.year - 5, 3, 20),
            localidentifier='test')
        article = ArticleFactory.create(issue=issue)

        class MyView(ArticleAccessCheckMixin):
            def get_article(self):
                return article

        request = self.factory.get('/')
        request.user = AnonymousUser()
        view = MyView()
        view.request = request

        # Run # check
        self.assertTrue(view.has_access())

    def test_can_grant_access_to_an_article_if_it_is_associated_to_an_individual_subscription(self):
        # Setup
        self.journal.open_access = False
        self.journal.save()
        issue = IssueFactory.create(
            journal=self.journal, year=dt.datetime.now().year, date_published=dt.datetime.now(),
            localidentifier='test')
        article = ArticleFactory.create(issue=issue)

        now_dt = dt.datetime.now()

        subscription = JournalAccessSubscriptionFactory.create(user=self.user, journal=self.journal)
        JournalAccessSubscriptionPeriodFactory.create(
            subscription=subscription,
            start=now_dt - dt.timedelta(days=10),
            end=now_dt + dt.timedelta(days=8))

        class MyView(ArticleAccessCheckMixin):
            def get_article(self):
                return article

        request = self.factory.get('/')
        request.user = self.user
        view = MyView()
        view.request = request

        # Run # check
        self.assertTrue(view.has_access())

    def test_cannot_grant_access_to_an_article_if_it_is_associated_to_an_individual_subscription_that_is_not_ongoing(self):  # noqa
        # Setup
        self.journal.open_access = False
        self.journal.save()
        issue = IssueFactory.create(
            journal=self.journal, year=dt.datetime.now().year, date_published=dt.datetime.now(),
            localidentifier='test')
        article = ArticleFactory.create(issue=issue)

        JournalAccessSubscriptionFactory.create(user=self.user, journal=self.journal)

        class MyView(ArticleAccessCheckMixin):
            def get_article(self):
                return article

        request = self.factory.get('/')
        request.user = self.user
        view = MyView()
        view.request = request

        # Run # check
        self.assertFalse(view.has_access())

    def test_can_grant_access_to_an_article_if_it_is_associated_to_an_institutional_account(self):
        # Setup
        self.journal.open_access = False
        self.journal.save()
        issue = IssueFactory.create(
            journal=self.journal, year=dt.datetime.now().year, date_published=dt.datetime.now(),
            localidentifier='test')
        article = ArticleFactory.create(issue=issue)

        organisation = OrganisationFactory.create()

        now_dt = dt.datetime.now()

        subscription = JournalAccessSubscriptionFactory.create(
            journal=self.journal, organisation=organisation)
        JournalAccessSubscriptionPeriodFactory.create(
            subscription=subscription,
            start=now_dt - dt.timedelta(days=10),
            end=now_dt + dt.timedelta(days=8))

        InstitutionIPAddressRangeFactory.create(
            subscription=subscription,
            ip_start='192.168.1.2', ip_end='192.168.1.4')

        class MyView(ArticleAccessCheckMixin):
            def get_article(self):
                return article

        request = self.factory.get('/')
        request.user = AnonymousUser()
        parameters = request.META.copy()
        parameters['HTTP_X_FORWARDED_FOR'] = '192.168.1.3'
        request.META = parameters

        view = MyView()
        view.request = request

        # Run # check
        self.assertTrue(view.has_access())

    def test_cannot_grant_access_to_an_article_if_it_is_associated_to_an_institutional_account_that_is_not_not_ongoing(self):  # noqa
        # Setup
        self.journal.open_access = False
        self.journal.save()
        issue = IssueFactory.create(
            journal=self.journal, year=dt.datetime.now().year, date_published=dt.datetime.now(),
            localidentifier='test')
        article = ArticleFactory.create(issue=issue)

        organisation = OrganisationFactory.create()

        subscription = JournalAccessSubscriptionFactory.create(
            journal=self.journal, organisation=organisation)

        InstitutionIPAddressRangeFactory.create(
            subscription=subscription,
            ip_start='192.168.1.2', ip_end='192.168.1.4')

        class MyView(ArticleAccessCheckMixin):
            def get_article(self):
                return article

        request = self.factory.get('/')
        request.user = AnonymousUser()
        parameters = request.META.copy()
        parameters['HTTP_X_FORWARDED_FOR'] = '192.168.1.3'
        request.META = parameters

        view = MyView()
        view.request = request

        # Run # check
        self.assertFalse(view.has_access())

    def test_inserts_a_flag_into_the_context(self):
        # Setup
        self.journal.open_access = True
        self.journal.save()
        issue = IssueFactory.create(
            journal=self.journal, year=dt.datetime.now().year, date_published=dt.datetime.now(),
            localidentifier='test')
        article = ArticleFactory.create(issue=issue)

        class MyViewAncestor(object):
            def get_context_data(self, **kwargs):
                return {}

        class MyView(ArticleAccessCheckMixin, MyViewAncestor):
            def get_article(self):
                return article

        view = MyView()

        # Run # check
        self.assertTrue(view.has_access())
        self.assertTrue(view.get_context_data()['article_access_granted'])
