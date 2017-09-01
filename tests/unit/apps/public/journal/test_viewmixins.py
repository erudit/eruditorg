# -*- coding: utf-8 -*-

import datetime as dt

from django.contrib.auth.models import AnonymousUser
from django.http import Http404
from django.test import RequestFactory
from django.views.generic import DetailView

from erudit.test import BaseEruditTestCase
from erudit.test.factories import ArticleFactory, EmbargoedArticleFactory, NonEmbargoedArticleFactory, OpenAccessArticleFactory
from erudit.test.factories import IssueFactory
from erudit.test.factories import OrganisationFactory
from erudit.models import Article

from apps.public.journal.viewmixins import ContentAccessCheckMixin
from apps.public.journal.viewmixins import SingleArticleMixin
from apps.public.journal.viewmixins import SingleJournalMixin
from core.subscription.models import UserSubscriptions
from core.subscription.test.factories import JournalAccessSubscriptionFactory
from core.subscription.middleware import SubscriptionMiddleware

middleware = SubscriptionMiddleware()


class TestSingleArticleMixin(BaseEruditTestCase):
    def test_can_retrieve_the_article_using_the_local_identifier(self):
        # Setup
        article_1 = ArticleFactory.create(localidentifier='test_article')

        class MyView(SingleArticleMixin, DetailView):
            model = Article

        view = MyView()
        view.kwargs = {'localid': article_1.localidentifier}

        # Run & check
        assert view.get_object() == article_1


class TestSingleJournalMixin(BaseEruditTestCase):
    def test_can_return_a_journal_based_on_its_code(self):
        # Setup
        code = self.journal.code
        mixin = SingleJournalMixin()
        mixin.kwargs = {'code': code}
        # Run & check
        assert mixin.get_object() == self.journal

    def test_returns_http_404_if_the_journal_does_not_exist(self):
        # Setup
        code = self.journal.code
        mixin = SingleJournalMixin()
        mixin.kwargs = {'code': code + 'dummy'}
        # Run & check
        with self.assertRaises(Http404):
            mixin.get_object()


class TestContentAccessCheckMixin(BaseEruditTestCase):
    def setUp(self):
        super(TestContentAccessCheckMixin, self).setUp()
        self.factory = RequestFactory()

    def test_do_not_grant_access_by_default(self):
        # Setup
        article = EmbargoedArticleFactory()

        class MyView(ContentAccessCheckMixin):
            def get_content(self):
                return article

        request = self.factory.get('/')
        request.user = AnonymousUser()
        request.session = dict()
        request.subscriptions = UserSubscriptions()

        view = MyView()
        view.request = request

        # Run # check
        assert not view.content_access_granted

    def test_can_grant_access_to_an_article_if_it_is_in_open_access(self):
        # Setup
        article = OpenAccessArticleFactory()

        class MyView(ContentAccessCheckMixin):
            def get_content(self):
                return article

        request = self.factory.get('/')
        request.user = AnonymousUser()
        request.session = dict()
        request.subscriptions = UserSubscriptions()
        view = MyView()
        view.request = request

        # Run # check
        assert view.content_access_granted

    def test_can_grant_access_to_an_article_if_it_is_not_embargoed(self):
        # Setup
        article = NonEmbargoedArticleFactory.create()

        class MyView(ContentAccessCheckMixin):
            def get_content(self):
                return article

        request = self.factory.get('/')
        request.user = AnonymousUser()
        request.session = dict()
        view = MyView()
        view.request = request

        # Run # check
        assert view.content_access_granted

    def test_can_grant_access_to_an_article_if_it_is_associated_to_an_individual_subscription(self):
        # Setup
        article = EmbargoedArticleFactory()

        JournalAccessSubscriptionFactory.create(
            user=self.user,
            journal=article.issue.journal,
            post__valid=True
        )

        class MyView(ContentAccessCheckMixin):
            def get_content(self):
                return article

        request = self.factory.get('/')
        request.user = self.user
        request.session = dict()
        view = MyView()
        view.request = request
        middleware.process_request(request)

        # Run # check
        assert view.content_access_granted

    def test_cannot_grant_access_to_an_article_if_it_is_associated_to_an_individual_subscription_that_is_not_ongoing(self):  # noqa
        # Setup

        article = EmbargoedArticleFactory.create()

        JournalAccessSubscriptionFactory.create(user=self.user, journal=article.issue.journal)

        class MyView(ContentAccessCheckMixin):
            def get_content(self):
                return article

        request = self.factory.get('/')
        request.user = self.user
        request.session = dict()
        request.subscriptions = UserSubscriptions()
        view = MyView()
        view.request = request

        # Run # check
        assert not view.content_access_granted

    def test_can_grant_access_to_an_article_if_it_is_associated_to_an_institutional_account(self):
        # Setup
        article = EmbargoedArticleFactory.create()

        JournalAccessSubscriptionFactory(
            journal=article.issue.journal,
            post__valid=True,
            post__ip_start='192.168.1.2',
            post__ip_end='192.168.1.4'
        )

        class MyView(ContentAccessCheckMixin):
            def get_content(self):
                return article

        request = self.factory.get('/')
        request.user = AnonymousUser()
        request.session = dict()
        parameters = request.META.copy()
        parameters['HTTP_X_FORWARDED_FOR'] = '192.168.1.3'
        request.META = parameters
        middleware.process_request(request)

        view = MyView()
        view.request = request

        # Run # check
        assert view.content_access_granted

    def test_cannot_grant_access_to_an_article_if_it_is_associated_to_an_institutional_account_that_is_not_not_ongoing(self):  # noqa
        # Setup
        article = EmbargoedArticleFactory.create()

        JournalAccessSubscriptionFactory.create(
            journal=article.issue.journal,
            post__ip_start='192.168.1.2',
            post__ip_end='192.168.1.4'
        )

        class MyView(ContentAccessCheckMixin):
            def get_content(self):
                return article

        request = self.factory.get('/')
        request.user = AnonymousUser()
        request.session = dict()
        request.subscriptions = UserSubscriptions()
        parameters = request.META.copy()
        parameters['HTTP_X_FORWARDED_FOR'] = '192.168.1.3'
        request.META = parameters

        view = MyView()
        view.request = request

        # Run # check
        assert not view.content_access_granted

    def test_inserts_a_flag_into_the_context(self):
        # Setup
        article = NonEmbargoedArticleFactory.create()

        class MyViewAncestor(object):
            def get_context_data(self, **kwargs):
                return {}

        class MyView(ContentAccessCheckMixin, MyViewAncestor):
            def get_content(self):
                return article

        view = MyView()
        request = self.factory.get('/')
        request.subscriptions = UserSubscriptions()
        view.request = request
        # Run # check
        assert view.content_access_granted
        assert view.get_context_data()['content_access_granted']
