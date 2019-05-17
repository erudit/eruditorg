import pytest
import unittest.mock

from django.http import Http404
from django.test import RequestFactory
from django.views.generic import DetailView

from erudit.test.factories import (
    ArticleFactory, EmbargoedArticleFactory, NonEmbargoedArticleFactory, OpenAccessArticleFactory, EmbargoedIssueFactory
)
from erudit.models import Article

from apps.public.journal.viewmixins import ContentAccessCheckMixin
from apps.public.journal.viewmixins import SingleArticleMixin
from apps.public.journal.viewmixins import SingleJournalMixin
from apps.public.journal.viewmixins import ContributorsMixin
from apps.public.journal.views import ArticleRawPdfView, ArticleXmlView
from core.subscription.test.factories import JournalAccessSubscriptionFactory
from core.subscription.middleware import SubscriptionMiddleware
from core.subscription.models import UserSubscriptions
from base.test.factories import get_anonymous_request, get_authenticated_request
from erudit.test.factories import JournalFactory, JournalInformationFactory, ContributorFactory, \
    IssueFactory
from erudit.fedora import repository

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

    @pytest.mark.parametrize('is_published,authorized', (
        (False, True),
        (True, False)
    ))
    def test_can_grant_access_to_an_article_if_prepublication_ticket_is_valid(self, is_published, authorized, single_article_view):
        article = EmbargoedArticleFactory(issue__is_published=is_published)

        view = single_article_view()
        view.object = article
        request = RequestFactory().get('/', {
            'ticket': article.issue.prepublication_ticket
        })
        view.request = request
        request.subscriptions = UserSubscriptions()
        request.session = dict()

        # Run # check
        assert view.content_access_granted == authorized

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
        issue_embargoed = EmbargoedIssueFactory(journal=article.issue.journal)

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
            journals=[article.issue.journal],
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

        JournalAccessSubscriptionFactory.create(user=authenticated_request.user, journals=[article.issue.journal])

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
            journals=[article.issue.journal],
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
            journals=[article.issue.journal],
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
            journals=[article.issue.journal],
            post__valid=True,
            post__ip_start="0.0.0.1",
            post__ip_end="0.0.0.3",
        )

        # Create another embargoed article
        other_article = EmbargoedArticleFactory()

        # Create an individual subscription that gives access to this article
        individual_subscription = JournalAccessSubscriptionFactory(
            journals=[other_article.issue.journal],
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
            journals=[article.issue.journal],
            post__valid=True,
            post__ip_start="0.0.0.1",
            post__ip_end="0.0.0.3",
        )

        # Create an individual subscription that gives access to this article
        JournalAccessSubscriptionFactory(
            journals=[article.issue.journal],
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
        issue_embargoed = EmbargoedIssueFactory(journal=article.issue.journal)
        anonymous_request = get_anonymous_request()

        view = single_article_view()
        view.object = article
        view.request = anonymous_request
        # Run # check
        assert view.content_access_granted
        assert view.get_context_data()['content_access_granted']

    def test_can_grant_access_to_an_issue_if_prepublication_ticket_start_with_zero(self, single_article_view):
        # Create an article from an issue with a prepublication ticket starting with a '0'.
        # md5('moebius04311'.encode('utf-8')).hexdigest() == '08844a3d4413c44ab754c60fd23c83fc'
        article = ArticleFactory(issue__is_published=False, issue__localidentifier='moebius04311')

        view = single_article_view()
        view.object = article
        # Try to access the article without the leading '0' in the prepublication ticket.
        view.request = RequestFactory().get('/', {
            'ticket': article.issue.prepublication_ticket[1:]
        })
        # Run # check
        assert view.content_access_granted == True


    @pytest.mark.parametrize('ticket_provided, access_granted', (
        (False, False),
        (True, True)
    ))
    @pytest.mark.parametrize('View', (ArticleRawPdfView, ArticleXmlView))
    def test_cannot_grant_access_to_an_unpublished_article_pdf_and_xml_if_no_prepublication_ticket_is_provided(self, ticket_provided, access_granted, View):
        article = ArticleFactory(issue__is_published=False)
        view = View()
        view.request = unittest.mock.MagicMock()
        # Access should not be granted even if the user has a valid subscription.
        view.request.subscriptions.provides_access_to = unittest.mock.MagicMock(return_value=True)
        view.kwargs = {
            'journal_code': article.issue.journal.code,
            'issue_localid': article.issue.localidentifier,
            'localid': article.localidentifier,
        }
        view.request.GET = {
            'ticket': article.issue.prepublication_ticket if ticket_provided else None,
        }
        assert view.content_access_granted == access_granted


class TestContributorsMixin:

    @pytest.mark.parametrize('use_journal_info, use_issue, expected_contributors', (
        (False, False, {
            'directors': [],
            'editors': [],
        }),
        (False, True, {
            'directors': [{'name': 'Claude Racine', 'role': None}],
            'editors': [{'name': 'Marie-Claude Loiselle', 'role': 'Rédactrice en chef'}],
        }),
        (True, False, {
            'directors': [{'name': 'Foo', 'role': 'Bar'}],
            'editors': [],
        }),
        (True, True, {
            'directors': [{'name': 'Foo', 'role': 'Bar'}],
            'editors': [],
        }),
    ))
    def test_get_contributors(self, use_journal_info, use_issue, expected_contributors):
        issue = IssueFactory()
        repository.api.set_publication_xml(
            issue.get_full_identifier(),
            open('tests/fixtures/issue/images1102374.xml', 'rb').read(),
        )
        journal_info = JournalInformationFactory(journal=issue.journal)
        journal_info.editorial_leaders.add(
            ContributorFactory(
                type='D',
                name='Foo',
                role='Bar',
                journal_information=journal_info,
            )
        )
        mixin = ContributorsMixin()
        contributors = mixin.get_contributors(
            journal_info=journal_info if use_journal_info else None,
            issue=issue if use_issue else None,
        )
        assert contributors == expected_contributors
