# -*- coding: utf-8 -*-

import datetime as dt

from django.http import Http404
from django.test import RequestFactory

from core.subscription.factories import InstitutionalAccountFactory
from core.subscription.factories import InstitutionIPAddressRangeFactory
from core.subscription.factories import PolicyFactory
from erudit.factories import ArticleFactory
from erudit.factories import IssueFactory
from erudit.factories import OrganisationFactory
from erudit.tests import BaseEruditTestCase

from ..viewmixins import ArticleAccessCheckMixin
from ..viewmixins import JournalCodeDetailMixin


class TestJournalCodeDetailMixin(BaseEruditTestCase):
    def test_can_return_a_journal_based_on_its_code(self):
        # Setup
        code = self.journal.code
        mixin = JournalCodeDetailMixin()
        mixin.kwargs = {'code': code}
        # Run & check
        self.assertEqual(mixin.get_object(), self.journal)

    def test_returns_http_404_if_the_journal_does_not_exist(self):
        # Setup
        code = self.journal.code
        mixin = JournalCodeDetailMixin()
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

        view = MyView()

        # Run # check
        self.assertTrue(view.has_access())

    def test_can_grant_access_to_an_article_if_it_is_associatd_to_an_institutional_account(self):
        # Setup
        issue = IssueFactory.create(
            journal=self.journal, date_published=dt.datetime.now(), localidentifier='test',
            open_access=True)
        article = ArticleFactory.create(issue=issue)

        policy = PolicyFactory.create(max_accounts=2)
        policy.access_journal.add(self.journal)
        organisation = OrganisationFactory.create()
        institutional_account = InstitutionalAccountFactory(
            institution=organisation, policy=policy)
        InstitutionIPAddressRangeFactory.build(
            institutional_account=institutional_account,
            ip_start='192.168.1.2', ip_end='192.168.1.4')

        class MyView(ArticleAccessCheckMixin):
            def get_article(self):
                return article

        request = self.factory.get('/')
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
