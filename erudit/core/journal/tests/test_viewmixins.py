# -*- coding: utf-8 -*-

import datetime as dt

from django.contrib.auth.models import AnonymousUser
from django.http import Http404
from django.test import RequestFactory

from core.subscription.factories import InstitutionIPAddressRangeFactory
from core.subscription.factories import JournalAccessSubscriptionFactory
from erudit.factories import ArticleFactory
from erudit.factories import IssueFactory
from erudit.factories import OrganisationFactory
from erudit.tests import BaseEruditTestCase

from ..viewmixins import ArticleAccessCheckMixin
from ..viewmixins import SingleJournalMixin


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
        issue = IssueFactory.create(
            journal=self.journal, date_published=dt.datetime.now(), localidentifier='test',
            open_access=False)
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
        issue = IssueFactory.create(
            journal=self.journal, date_published=dt.datetime.now(), localidentifier='test',
            open_access=True)
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
        issue = IssueFactory.create(
            journal=self.journal, date_published=dt.datetime.now(), localidentifier='test',
            open_access=False)
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
        self.assertTrue(view.has_access())

    def test_can_grant_access_to_an_article_if_it_is_associated_to_an_institutional_account(self):
        # Setup
        issue = IssueFactory.create(
            journal=self.journal, date_published=dt.datetime.now(), localidentifier='test',
            open_access=False)
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
        self.assertTrue(view.has_access())

    def test_inserts_a_flag_into_the_context(self):
        # Setup
        issue = IssueFactory.create(
            journal=self.journal, date_published=dt.datetime.now(), localidentifier='test',
            open_access=True)
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
