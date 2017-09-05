# -*- coding: utf-8 -*-

import pytest

from django.contrib.auth.models import AnonymousUser
from django.http import Http404
from django.test import RequestFactory
from django.views.generic import DetailView

from erudit.test import BaseEruditTestCase
from erudit.test.factories import ArticleFactory, EmbargoedArticleFactory, NonEmbargoedArticleFactory, OpenAccessArticleFactory
from erudit.models import Article

from base.test.factories import UserFactory
from apps.public.journal.viewmixins import ContentAccessCheckMixin
from apps.public.journal.viewmixins import SingleArticleMixin
from apps.public.journal.viewmixins import SingleJournalMixin
from core.subscription.models import UserSubscriptions
from core.subscription.test.factories import JournalAccessSubscriptionFactory
from core.subscription.middleware import SubscriptionMiddleware

middleware = SubscriptionMiddleware()


@pytest.fixture
def anonymous_request():
    request = RequestFactory().get('/')
    request.user = AnonymousUser()
    request.subscriptions = UserSubscriptions()
    request.session = dict()
    return request

@pytest.fixture
def authenticated_request():
    request = RequestFactory().get('/')
    request.user = UserFactory()
    request.subscriptions = UserSubscriptions()
    request.session = dict()
    return request

@pytest.fixture()
def single_article_view():
    class MyViewAncestor(object):
        def get_context_data(self, **kwargs):
            return {}

        def dispatch(self, **kwargs):
            return {}

    class MyView(ContentAccessCheckMixin, MyViewAncestor):
        pass

    return MyView


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


@pytest.mark.django_db
class TestContentAccessCheckMixin(object):

    def setUp(self):
        super(TestContentAccessCheckMixin, self).setUp()
        self.factory = RequestFactory()

    def test_do_not_grant_access_by_default(self, anonymous_request, single_article_view):
        # Setup
        article = EmbargoedArticleFactory()

        view = single_article_view()
        view.object = article
        view.request = anonymous_request

        # Run # check
        assert not view.content_access_granted

    def test_can_grant_access_to_an_article_if_it_is_in_open_access(self, anonymous_request, single_article_view):
        # Setup
        article = OpenAccessArticleFactory()
        view = single_article_view
        view.object = article
        view.request = anonymous_request

        # Run # check
        assert view.content_access_granted

    def test_can_grant_access_to_an_article_if_it_is_not_embargoed(self, anonymous_request, single_article_view):
        # Setup
        article = NonEmbargoedArticleFactory.create()

        view = single_article_view()
        view.object = article
        view.request = anonymous_request

        # Run # check
        assert view.content_access_granted

    def test_can_grant_access_to_an_article_if_it_is_associated_to_an_individual_subscription(self, authenticated_request, single_article_view):
        # Setup
        article = EmbargoedArticleFactory()

        JournalAccessSubscriptionFactory.create(
            user=authenticated_request.user,
            journal=article.issue.journal,
            post__valid=True
        )

        middleware.process_request(authenticated_request)

        view = single_article_view()
        view.object = article
        view.request = authenticated_request

        # Run # check
        assert view.content_access_granted

    def test_cannot_grant_access_to_an_article_if_it_is_associated_to_an_individual_subscription_that_is_not_ongoing(self, authenticated_request, single_article_view):  # noqa
        # Setup

        article = EmbargoedArticleFactory.create()

        JournalAccessSubscriptionFactory.create(user=authenticated_request.user, journal=article.issue.journal)

        view = single_article_view()
        view.object = article
        view.request = authenticated_request

        # Run # check
        assert not view.content_access_granted

    def test_can_grant_access_to_an_article_if_it_is_associated_to_an_institutional_account(self, anonymous_request, single_article_view):
        # Setup
        article = EmbargoedArticleFactory.create()

        JournalAccessSubscriptionFactory(
            journal=article.issue.journal,
            post__valid=True,
            post__ip_start='192.168.1.2',
            post__ip_end='192.168.1.4'
        )

        parameters = anonymous_request.META.copy()
        parameters['HTTP_X_FORWARDED_FOR'] = '192.168.1.3'
        anonymous_request.META = parameters
        middleware.process_request(anonymous_request)

        view = single_article_view()
        view.object = article
        view.request = anonymous_request

        # Run # check
        assert view.content_access_granted

    def test_cannot_grant_access_to_an_article_if_it_is_associated_to_an_institutional_account_that_is_not_not_ongoing(self, anonymous_request, single_article_view):  # noqa
        # Setup
        article = EmbargoedArticleFactory.create()

        JournalAccessSubscriptionFactory.create(
            journal=article.issue.journal,
            post__ip_start='192.168.1.2',
            post__ip_end='192.168.1.4'
        )

        parameters = anonymous_request.META.copy()
        parameters['HTTP_X_FORWARDED_FOR'] = '192.168.1.3'
        anonymous_request.META = parameters

        view = single_article_view()
        view.object = article
        view.request = anonymous_request

        # Run # check
        assert not view.content_access_granted

    def test_first_subscription_is_activated_when_both_are_valid(self):
        pass

    def test_inserts_a_flag_into_the_context(self, anonymous_request, single_article_view):
        # Setup
        article = NonEmbargoedArticleFactory.create()

        view = single_article_view()
        view.object = article
        view.request = anonymous_request
        # Run # check
        assert view.content_access_granted
        assert view.get_context_data()['content_access_granted']
