import pytest

from django.http import Http404
from django.test import RequestFactory
from django.views.generic import DetailView

from erudit.test.factories import (
    ArticleFactory, EmbargoedArticleFactory, NonEmbargoedArticleFactory, OpenAccessArticleFactory
)
from erudit.models import Article

from apps.public.journal.viewmixins import ContentAccessCheckMixin
from apps.public.journal.viewmixins import SingleArticleMixin
from apps.public.journal.viewmixins import SingleJournalMixin
from core.subscription.test.factories import JournalAccessSubscriptionFactory
from core.subscription.middleware import SubscriptionMiddleware
from base.test.factories import get_anonymous_request, get_authenticated_request
from erudit.test.factories import JournalFactory

middleware = SubscriptionMiddleware()
pytestmark = pytest.mark.django_db


@pytest.fixture()
def single_article_view():
    class MyViewAncestor:
        def get_context_data(self, **kwargs):
            return {}

        def dispatch(self, **kwargs):
            return {}

    class MyView(ContentAccessCheckMixin, MyViewAncestor):
        pass

    return MyView


class TestSingleArticleMixin:
    def test_can_retrieve_the_article_using_the_local_identifier(self):
        article_1 = ArticleFactory.create(localidentifier='test_article')

        class MyView(SingleArticleMixin, DetailView):
            model = Article

        view = MyView()
        view.kwargs = {'localid': article_1.localidentifier}
        assert view.get_object() == article_1


class TestSingleJournalMixin:
    def test_can_return_a_journal_based_on_its_code(self):
        journal = JournalFactory()
        mixin = SingleJournalMixin()
        mixin.kwargs = {'code': journal.code}
        assert mixin.get_object() == journal

    def test_returns_http_404_if_the_journal_does_not_exist(self):
        journal = JournalFactory()
        mixin = SingleJournalMixin()
        mixin.kwargs = {'code': journal.code + 'dummy'}
        with pytest.raises(Http404):
            mixin.get_object()


class TestContentAccessCheckMixin:

    def setUp(self):
        super(TestContentAccessCheckMixin, self).setUp()
        self.factory = RequestFactory()

    def test_do_not_grant_access_by_default(self, single_article_view):
        # Setup
        article = EmbargoedArticleFactory()

        view = single_article_view()
        view.object = article
        view.request = get_anonymous_request()

        # Run # check
        assert not view.content_access_granted

    def test_can_grant_access_to_an_article_if_it_is_in_open_access(self, single_article_view):
        # Setup
        article = OpenAccessArticleFactory()
        view = single_article_view
        view.object = article
        view.request = get_anonymous_request()

        # Run # check
        assert view.content_access_granted

    def test_can_grant_access_to_an_article_if_it_is_not_embargoed(self, single_article_view):
        # Setup
        article = NonEmbargoedArticleFactory.create()

        view = single_article_view()
        view.object = article
        view.request = get_anonymous_request()

        # Run # check
        assert view.content_access_granted

    def test_can_grant_access_to_an_article_if_it_is_associated_to_an_individual_subscription(self, single_article_view):
        # Setup
        article = EmbargoedArticleFactory()
        authenticated_request = get_authenticated_request()

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

    def test_cannot_grant_access_to_an_article_if_it_is_associated_to_an_individual_subscription_that_is_not_ongoing(self, single_article_view):  # noqa
        # Setup

        article = EmbargoedArticleFactory.create()
        authenticated_request = get_authenticated_request()

        JournalAccessSubscriptionFactory.create(user=authenticated_request.user, journal=article.issue.journal)

        view = single_article_view()
        view.object = article
        view.request = authenticated_request

        # Run # check
        assert not view.content_access_granted

    def test_can_grant_access_to_an_article_if_it_is_associated_to_an_institutional_account(self, single_article_view):
        # Setup
        article = EmbargoedArticleFactory.create()
        anonymous_request = get_anonymous_request()

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

    def test_cannot_grant_access_to_an_article_if_it_is_associated_to_an_institutional_account_that_is_not_not_ongoing(self, single_article_view):  # noqa
        # Setup
        article = EmbargoedArticleFactory.create()
        anonymous_request = get_anonymous_request()

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

    def test_second_subscription_is_activated_when_first_doesnt_give_access_to_article(self, single_article_view):
        """ Test that the adequate subscription is activated """

        # Create an embargoed article
        article = EmbargoedArticleFactory()
        authenticated_request = get_authenticated_request()

        # Create an institutional subscription that gives access to this article
        JournalAccessSubscriptionFactory(
            journal=article.issue.journal,
            post__valid=True,
            post__ip_start="0.0.0.1",
            post__ip_end="0.0.0.3",
        )

        # Create another embargoed article
        other_article = EmbargoedArticleFactory()

        # Create an individual subscription that gives access to this article
        individual_subscription = JournalAccessSubscriptionFactory(
            journal=other_article.issue.journal,
            user=authenticated_request.user,
            post__valid=True
        )

        parameters = authenticated_request.META.copy()
        parameters['HTTP_X_FORWARDED_FOR'] = '0.0.0.2'
        authenticated_request.META = parameters
        middleware.process_request(authenticated_request)

        view = single_article_view()
        view.object = other_article
        view.request = authenticated_request
        view.dispatch()
        assert view.content_access_granted
        assert authenticated_request.subscriptions.active_subscription == individual_subscription
        assert authenticated_request.subscriptions._subscriptions.index(individual_subscription) == 1

    def test_first_subscription_is_activated_when_both_are_valid(self, single_article_view):
        # Create an embargoed article
        article = EmbargoedArticleFactory()
        authenticated_request = get_authenticated_request()

        # Create an institutional subscription that gives access to this article
        ip_subscription = JournalAccessSubscriptionFactory(
            journal=article.issue.journal,
            post__valid=True,
            post__ip_start="0.0.0.1",
            post__ip_end="0.0.0.3",
        )

        # Create an individual subscription that gives access to this article
        JournalAccessSubscriptionFactory(
            journal=article.issue.journal,
            user=authenticated_request.user,
            post__valid=True
        )
        parameters = authenticated_request.META.copy()
        parameters['HTTP_X_FORWARDED_FOR'] = '0.0.0.2'
        authenticated_request.META = parameters
        middleware.process_request(authenticated_request)

        view = single_article_view()
        view.object = article
        view.request = authenticated_request
        view.dispatch()
        assert view.content_access_granted
        assert authenticated_request.subscriptions.active_subscription == ip_subscription
        assert authenticated_request.subscriptions._subscriptions.index(ip_subscription) == 0

    def test_inserts_a_flag_into_the_context(self, single_article_view):
        # Setup
        article = NonEmbargoedArticleFactory.create()
        anonymous_request = get_anonymous_request()

        view = single_article_view()
        view.object = article
        view.request = anonymous_request
        # Run # check
        assert view.content_access_granted
        assert view.get_context_data()['content_access_granted']
