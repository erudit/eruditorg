import datetime as dt
import io
import os
import unittest.mock
import subprocess
import itertools

from django.contrib.auth.models import AnonymousUser
from django.core.urlresolvers import reverse
from django.http.response import HttpResponseRedirect
from django.test import Client
from django.test import RequestFactory
from django.conf import settings
from django.test.utils import override_settings
import pytest

from erudit.models import JournalType, Issue
from erudit.test import BaseEruditTestCase
from erudit.test.factories import ArticleFactory
from erudit.test.factories import AuthorFactory
from erudit.test.factories import CollectionFactory
from erudit.test.factories import DisciplineFactory
from erudit.test.factories import IssueFactory
from erudit.test.factories import JournalFactory
from erudit.test.factories import JournalInformationFactory
from erudit.fedora.objects import ArticleDigitalObject
from erudit.fedora.objects import MediaDigitalObject
from erudit.fedora.modelmixins import FedoraMixin

from base.test.factories import UserFactory
from core.subscription.test.factories import JournalAccessSubscriptionFactory
from core.subscription.models import UserSubscriptions

from apps.public.journal.views import ArticleDetailView
from apps.public.journal.views import ArticleMediaView
from apps.public.journal.views import ArticleRawPdfView
from apps.public.journal.views import ArticleXmlView

from base.test.testcases import EruditClientTestCase

FIXTURE_ROOT = os.path.join(os.path.dirname(__file__), 'fixtures')


def get_mocked_erudit_object(self):
    m = unittest.mock.MagicMock()
    m.get_last_published_issue_pid.return_value = "mock-1234"
    m.get_formatted_title.return_value = "mocked title"
    m.get_formatted_authors.return_value = ['author 1', 'author 2']
    return m

def issue_detail_url(issue):
    return reverse('public:journal:issue_detail', args=[
        issue.journal.code, issue.volume_slug, issue.localidentifier])

def article_detail_url(article):
    issue = article.issue
    return reverse('public:journal:article_detail', kwargs={
        'journal_code': issue.journal.code, 'issue_slug': issue.volume_slug,
        'issue_localid': issue.localidentifier, 'localid': article.localidentifier})

def article_raw_pdf_url(article):
    issue = article.issue
    journal_id = issue.journal.localidentifier
    issue_id = issue.localidentifier
    article_id = article.localidentifier
    return reverse('public:journal:article_raw_pdf', args=(
        journal_id, issue.volume_slug, issue_id, article_id
    ))

@pytest.mark.django_db
class TestJournalListView(object):

    @pytest.fixture(autouse=True)
    def setup(self):
        self.client = Client()
        self.user = UserFactory.create(username='foobar')
        self.user.set_password('notsecret')
        self.user.save()

    def test_upcoming_journals_are_hidden_from_list(self):

        # Create 6 journals
        journals = JournalFactory.create_batch(6)

        # Create an issue for the first 5 journals
        for journal in journals[:5]:
            IssueFactory(journal=journal)

        url = reverse('public:journal:journal_list')
        # Run
        response = self.client.get(url)
        displayed_journals = set(response.context['journals'])
        assert displayed_journals == set(journals[:5])
        assert journals[5] not in displayed_journals

    def test_can_sort_journals_by_name(self):
        # Setup
        collection = CollectionFactory.create()
        journal_1 = JournalFactory.create_with_issue(collection=collection, name='ABC journal')
        journal_2 = JournalFactory.create_with_issue(collection=collection, name='ACD journal')
        journal_3 = JournalFactory.create_with_issue(collection=collection, name='DEF journal')
        journal_4 = JournalFactory.create_with_issue(collection=collection, name='GHI journal')
        journal_5 = JournalFactory.create_with_issue(collection=collection, name='GIJ journal')
        journal_6 = JournalFactory.create_with_issue(collection=collection, name='GJK journal')
        url = reverse('public:journal:journal_list')
        # Run
        response = self.client.get(url)
        # Check
        assert response.status_code == 200
        assert len(response.context['sorted_objects']) == 3
        assert response.context['sorted_objects'][0]['key'] == 'A'
        assert response.context['sorted_objects'][0]['objects'] == [
            journal_1, journal_2, ]
        assert response.context['sorted_objects'][1]['key'] == 'D'
        assert response.context['sorted_objects'][1]['objects'] == [journal_3, ]
        assert response.context['sorted_objects'][2]['key'] == 'G'
        assert response.context['sorted_objects'][2]['objects'] == [
            journal_4, journal_5, journal_6, ]

    def test_can_sort_journals_by_disciplines(self):
        # Setup
        collection = CollectionFactory.create()
        discipline_1 = DisciplineFactory.create(code='abc-discipline', name='ABC')
        discipline_2 = DisciplineFactory.create(code='def-discipline', name='DEF')
        discipline_3 = DisciplineFactory.create(code='ghi-discipline', name='GHI')
        journal_1 = JournalFactory.create_with_issue(collection=collection)
        journal_1.disciplines.add(discipline_1)
        journal_2 = JournalFactory.create_with_issue(collection=collection)
        journal_2.disciplines.add(discipline_1)
        journal_3 = JournalFactory.create_with_issue(collection=collection)
        journal_3.disciplines.add(discipline_2)
        journal_4 = JournalFactory.create_with_issue(collection=collection)
        journal_4.disciplines.add(discipline_3)
        journal_5 = JournalFactory.create_with_issue(collection=collection)
        journal_5.disciplines.add(discipline_3)
        journal_6 = JournalFactory.create_with_issue(collection=collection)
        journal_6.disciplines.add(discipline_3)
        url = reverse('public:journal:journal_list')
        # Run
        response = self.client.get(url, {'sorting': 'disciplines'})
        # Check
        assert response.status_code == 200
        assert len(response.context['sorted_objects']) == 3
        assert response.context['sorted_objects'][0]['key'] == discipline_1.code
        assert response.context['sorted_objects'][0]['collections'][0]['key'] == collection
        assert response.context['sorted_objects'][0]['collections'][0]['objects'] == [
            journal_1, journal_2, ]
        assert response.context['sorted_objects'][1]['key'] == discipline_2.code
        assert response.context['sorted_objects'][1]['collections'][0]['key'] == collection
        assert response.context['sorted_objects'][1]['collections'][0]['objects'] == [journal_3, ]
        assert response.context['sorted_objects'][2]['key'] == discipline_3.code
        assert response.context['sorted_objects'][2]['collections'][0]['key'] == collection
        assert set(response.context['sorted_objects'][2]['collections'][0]['objects']) == set([
            journal_4, journal_5, journal_6, ])

    def test_only_main_collections_are_shown_by_default(self):
        collection = CollectionFactory.create()
        main_collection = CollectionFactory.create(is_main_collection=True)
        journal1 = JournalFactory.create_with_issue(collection=collection)
        journal2 = JournalFactory.create_with_issue(collection=main_collection)
        url = reverse('public:journal:journal_list')
        response = self.client.get(url)

        assert list(response.context['journals']) == [journal2]

    def test_can_filter_the_journals_by_open_access(self):
        # Setup
        collection = CollectionFactory.create()
        journal_1 = JournalFactory.create_with_issue(collection=collection, open_access=True)
        JournalFactory.create(collection=collection, open_access=False)
        url = reverse('public:journal:journal_list')
        # Run
        response = self.client.get(url, data={'open_access': True})
        # Check
        assert list(response.context['journals']) == [journal_1, ]

    def test_can_filter_the_journals_by_types(self):
        # Setup
        collection = CollectionFactory.create()
        jtype_1 = JournalType.objects.create(code='T1', name='T1')
        jtype_2 = JournalType.objects.create(code='T2', name='T2')
        JournalFactory.create(collection=collection, type=jtype_1)
        journal_2 = JournalFactory.create_with_issue(collection=collection, type=jtype_2)
        url = reverse('public:journal:journal_list')
        # Run
        response = self.client.get(url, data={'types': ['T2', ]})
        # Check
        assert list(response.context['journals']) == [journal_2, ]

    def test_can_filter_the_journals_by_collections(self):
        # Setup
        col_1 = CollectionFactory(code='col1')
        col_2 = CollectionFactory(code='col2')
        JournalFactory.create_with_issue(collection=col_1)
        journal_2 = JournalFactory.create_with_issue(collection=col_2)
        url = reverse('public:journal:journal_list')
        # Run
        response = self.client.get(url, data={'collections': ['col2', ]})
        # Check
        assert list(response.context['journals']) == [journal_2, ]


@pytest.mark.django_db
class TestJournalDetailView:

    @pytest.fixture(autouse=True)
    def setup(self, settings):
        settings.DEBUG = True
        self.client = Client()
        self.user = UserFactory.create(username='foobar')
        self.user.set_password('notsecret')
        self.user.save()

    def test_can_embed_the_journal_information_in_the_context_if_available(self):
        # Setup
        journal_info = JournalInformationFactory(journal=JournalFactory(use_fedora=False))
        url_1 = reverse('public:journal:journal_detail', kwargs={'code': journal_info.journal.code})
        journal_2 = JournalFactory(use_fedora=False)
        url_2 = reverse('public:journal:journal_detail', kwargs={'code': journal_2.code})

        # Run
        response_1 = self.client.get(url_1)
        response_2 = self.client.get(url_2)

        # Check
        assert response_1.status_code == response_2.status_code == 200

        assert response_1.context['journal_info'] == journal_info
        assert 'journal_info' not in response_2.context

    def test_can_display_when_issues_have_a_space_in_their_number(self, monkeypatch):
        monkeypatch.setattr(Issue, 'has_coverpage', unittest.mock.Mock(return_value=True))
        monkeypatch.setattr(Issue, 'erudit_object', unittest.mock.MagicMock())
        issue = IssueFactory(number='2 bis')
        url_1 = reverse('public:journal:journal_detail', kwargs={'code': issue.journal.code})
        # Run
        response_1 = self.client.get(url_1)
        assert response_1.status_code == 200

    def test_can_embed_the_published_issues_in_the_context(self):
        # Setup

        journal = JournalFactory(collection=CollectionFactory(localidentifier='erudit'))

        issue = IssueFactory(journal=journal)
        IssueFactory(journal=journal, is_published=False)

        url = reverse('public:journal:journal_detail', kwargs={'code': journal.code})
        # Run
        response = self.client.get(url)
        # Check
        assert response.status_code == 200
        assert list(response.context['issues']) == [issue]

    @pytest.mark.parametrize('external_url', ['https://example.com', None])
    def test_can_embed_the_latest_issue_in_the_context(self, external_url):
        # Setup
        collection = CollectionFactory.create(localidentifier='erudit')
        journal = JournalFactory.create(collection=collection)

        IssueFactory.create(
            journal=journal, date_published=dt.datetime.now())
        issue_2 = IssueFactory.create(
            journal=journal, date_published=dt.datetime.now() + dt.timedelta(days=1),
            external_url=external_url)

        url = reverse('public:journal:journal_detail', kwargs={'code': journal.code})
        # Run
        response = self.client.get(url)
        # Check
        assert response.status_code == 200
        assert response.context['latest_issue'] == issue_2
        link_attrs = response.context['latest_issue'].helper.detail_link_attrs()
        if external_url:
            assert external_url in link_attrs
        assert ('_blank' in link_attrs) == (external_url is not None)

    def test_embeds_a_boolean_indicating_if_the_user_is_subscribed_to_the_current_journal(self):
        # Setup

        journal = JournalFactory()
        subscription = JournalAccessSubscriptionFactory(user=self.user, post__journals=[journal], post__valid=True)

        self.client.login(username='foobar', password='notsecret')
        url = reverse('public:journal:journal_detail', kwargs={'code': journal.code})
        # Run
        response = self.client.get(url)
        # Check
        assert response.status_code == 200
        assert response.context['content_access_granted']

    def test_embeds_the_subscription_type(self, settings):
        journal = JournalFactory()
        subscription = JournalAccessSubscriptionFactory(
            organisation=None, user=self.user, post__journals=[journal], post__valid=True
        )
        self.client.login(username='foobar', password='notsecret')
        url = reverse('public:journal:journal_detail', kwargs={'code': journal.code})
        # Run
        response = self.client.get(url)
        # Check
        assert response.status_code == 200
        assert response.context['subscription_type'] == 'individual'


@override_settings(DEBUG=True)
class TestJournalAuthorsListView(BaseEruditTestCase):

    @pytest.fixture(autouse=True)
    def monkeypatch_get_erudit_article(self, monkeypatch):
        monkeypatch.setattr(FedoraMixin, "get_erudit_object", get_mocked_erudit_object)

    def test_supports_authors_with_empty_firstnames_and_empty_lastnames(self):
        # Setup
        issue_1 = IssueFactory.create(journal=JournalFactory(), date_published=dt.datetime.now())
        article_1 = ArticleFactory.create(issue=issue_1)
        author_1 = AuthorFactory.create(firstname='', lastname='')
        article_1.authors.add(author_1)

        issue_2 = IssueFactory.create(journal=JournalFactory(), date_published=dt.datetime.now())
        article_2 = ArticleFactory.create(issue=issue_2)
        author_2 = AuthorFactory.create(firstname='Ada', lastname='Lovelace')
        article_2.authors.add(author_2)

        url = reverse('public:journal:journal_authors_list', kwargs={'code': self.journal.code})

        # Run
        response = self.client.get(url)

        # Check
        self.assertEqual(response.status_code, 200)

    def test_supports_authors_with_only_special_characters_in_their_name(self):
        # Setup
        issue_1 = IssueFactory.create(journal=JournalFactory(use_fedora=False), date_published=dt.datetime.now())
        article_1 = ArticleFactory.create(issue=issue_1)
        author_1 = AuthorFactory.create(lastname=':')
        article_1.authors.add(author_1)
        url = reverse('public:journal:journal_authors_list', kwargs={'code': self.journal.code})

        # Run
        response = self.client.get(url)

        # Check
        self.assertEqual(response.status_code, 200)

    def test_provides_only_authors_for_the_first_available_letter_by_default(self):
        # Setup
        issue_1 = IssueFactory.create(journal=self.journal, date_published=dt.datetime.now())
        article_1 = ArticleFactory.create(issue=issue_1)

        author_1 = AuthorFactory.create(lastname='btest')
        author_2 = AuthorFactory.create(lastname='ctest1')
        author_3 = AuthorFactory.create(lastname='ctest2')

        article_1.authors.add(author_1)
        article_1.authors.add(author_2)
        article_1.authors.add(author_3)
        url = reverse('public:journal:journal_authors_list', kwargs={'code': self.journal.code})

        # Run
        response = self.client.get(url)

        # Check
        self.assertEqual(response.status_code, 200)
        self.assertEqual(list(response.context['authors']), [author_1, ])

    def test_only_provides_authors_for_the_given_letter(self):
        # Seetup
        issue_1 = IssueFactory.create(journal=self.journal, date_published=dt.datetime.now())
        article_1 = ArticleFactory.create( issue=issue_1)

        author_1 = AuthorFactory.create(lastname='btest')
        author_2 = AuthorFactory.create(lastname='ctest1')

        article_1.authors.add(author_1)
        article_1.authors.add(author_2)
        article_1.save()
        url = reverse('public:journal:journal_authors_list', kwargs={'code': self.journal.code})

        # Run
        response = self.client.get(url, letter='b')

        # Check
        self.assertEqual(response.status_code, 200)
        authors_dicts = response.context['authors_dicts']
        assert len(authors_dicts) == 1
        assert authors_dicts[0]['author'] == author_1

    def test_can_provide_contributors_of_article(self):
        issue_1 = IssueFactory.create(journal=self.journal, date_published=dt.datetime.now())
        article_1 = ArticleFactory.create( issue=issue_1)

        author_1 = AuthorFactory.create(lastname='btest')
        author_2 = AuthorFactory.create(lastname='ctest1')

        article_1.authors.add(author_1)
        article_1.authors.add(author_2)
        article_1.save()
        url = reverse('public:journal:journal_authors_list', kwargs={'code': self.journal.code})

        # Run
        response = self.client.get(url, letter='b')

        # Check
        self.assertEqual(response.status_code, 200)

        authors_dicts = response.context['authors_dicts']
        contributors = authors_dicts[0]['articles'][0]['contributors']

        assert len(contributors) == 1
        assert contributors[0].pk == author_2.pk

    def test_can_filter_by_article_type(self):
        # Setup
        issue_1 = IssueFactory.create(journal=self.journal, date_published=dt.datetime.now())
        article_1 = ArticleFactory.create( issue=issue_1, type='article')
        article_2 = ArticleFactory.create( issue=issue_1, type='compterendu')  # noqa

        author_1 = AuthorFactory.create(lastname='btest')
        article_1.authors.add(author_1)

        url = reverse('public:journal:journal_authors_list', kwargs={'code': self.journal.code})

        # Run
        response = self.client.get(url, article_type='article')

        # Check
        self.assertEqual(response.status_code, 200)
        authors_dicts = response.context['authors_dicts']

        assert len(authors_dicts) == 1

    def test_can_filter_by_article_type_when_no_article_of_type(self):
        issue_1 = IssueFactory.create(journal=self.journal, date_published=dt.datetime.now())
        article_1 = ArticleFactory.create( issue=issue_1, type='article')
        author_1 = AuthorFactory.create(lastname='atest')
        article_1.authors.add(author_1)
        url = reverse('public:journal:journal_authors_list', kwargs={'code': self.journal.code})

        # Run
        response = self.client.get(url, {"article_type": 'compterendu'})

        # Check
        self.assertEqual(response.status_code, 200)

    def test_only_letters_with_results_are_active(self):
        """ Test that for a given selection in the authors list view, only the letters for which
        results are present are shown """
        issue_1 = IssueFactory.create(journal=JournalFactory(use_fedora=False), date_published=dt.datetime.now(), use_fedora=False)
        article_1 = ArticleFactory.create( issue=issue_1, type='article')
        author_1 = AuthorFactory.create(lastname='atest')
        article_1.authors.add(author_1)
        url = reverse('public:journal:journal_authors_list', kwargs={'code': self.journal.code})

        # Run
        response = self.client.get(url, {"article_type": 'compterendu'})

        # Check
        self.assertEqual(response.status_code, 200)
        assert response.context['letters_exists'].get('A') == 0

    def test_do_not_fail_when_user_requests_a_letter_with_no_articles(self):
        # Setup
        issue_1 = IssueFactory.create(journal=self.journal, date_published=dt.datetime.now())
        article_1 = ArticleFactory.create(issue=issue_1, type='article')
        author_1 = AuthorFactory.create(lastname='btest')
        article_1.authors.add(author_1)

        url = reverse('public:journal:journal_authors_list', kwargs={'code': self.journal.code})

        response = self.client.get(url, {"article_type": 'compterendu', 'letter': 'A'})

        # Check
        self.assertEqual(response.status_code, 200)

    def test_inserts_the_current_letter_in_the_context(self):
        # Setup
        issue_1 = IssueFactory.create(journal=self.journal, date_published=dt.datetime.now())
        article_1 = ArticleFactory.create(issue=issue_1)

        author_1 = AuthorFactory.create(lastname='btest')
        author_2 = AuthorFactory.create(lastname='ctest1')
        author_3 = AuthorFactory.create(lastname='ctest2')

        article_1.authors.add(author_1)
        article_1.authors.add(author_2)
        article_1.authors.add(author_3)
        url = reverse('public:journal:journal_authors_list', kwargs={'code': self.journal.code})

        # Run
        response_1 = self.client.get(url)
        response_2 = self.client.get(url, {'letter': 'C'})
        response_3 = self.client.get(url, {'letter': 'invalid'})

        # Check
        self.assertEqual(response_1.status_code, 200)
        self.assertEqual(response_2.status_code, 200)
        self.assertEqual(response_3.status_code, 200)
        self.assertEqual(response_1.context['letter'], 'B')
        self.assertEqual(response_2.context['letter'], 'C')
        self.assertEqual(response_3.context['letter'], 'B')

    def test_inserts_a_dict_with_the_letters_counts_in_the_context(self):
        # Setup
        issue_1 = IssueFactory.create(journal=self.journal, date_published=dt.datetime.now())
        article_1 = ArticleFactory.create(issue=issue_1)

        author_1 = AuthorFactory.create(lastname='btest')
        author_2 = AuthorFactory.create(lastname='ctest1')
        author_3 = AuthorFactory.create(lastname='ctest2')

        article_1.authors.add(author_1)
        article_1.authors.add(author_2)
        article_1.authors.add(author_3)
        url = reverse('public:journal:journal_authors_list', kwargs={'code': self.journal.code})

        # Run
        response = self.client.get(url)

        # Check
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['letters_exists']), 26)
        self.assertEqual(response.context['letters_exists']['B'], 1)
        self.assertEqual(response.context['letters_exists']['C'], 2)
        for letter in 'adefghijklmnopqrstuvwxyz':
            self.assertEqual(response.context['letters_exists'][letter.upper()], 0)


@override_settings(DEBUG=True)
class TestIssueDetailView(BaseEruditTestCase):

    @unittest.mock.patch.object(FedoraMixin, 'get_erudit_object')
    def test_works_with_pks(self, mock_fedora_mixin):
        mock_fedora_mixin.return_value = get_mocked_erudit_object(None)
        # Setup
        issue = IssueFactory.create(journal=self.journal, date_published=dt.datetime.now())
        url = issue_detail_url(issue)
        # Run
        response = self.client.get(url)
        # Check
        self.assertEqual(response.status_code, 200)

    @unittest.mock.patch.object(FedoraMixin, 'get_erudit_object')
    def test_works_with_localidentifiers(self, mock_fedora_mixin):
        # Setup
        mock_fedora_mixin.return_value = get_mocked_erudit_object(None)
        issue = IssueFactory.create(
            journal=self.journal, date_published=dt.datetime.now(), localidentifier='test')
        url = issue_detail_url(issue)
        # Run
        response = self.client.get(url)
        # Check
        self.assertEqual(response.status_code, 200)

    def test_fedora_issue_with_external_url_redirects(self):
        # When we have an issue with a fedora localidentifier *and* external_url set, we redirect
        # to that external url when we hit the detail view.
        # ref #1651
        issue = IssueFactory.create(
            journal=self.journal, date_published=dt.datetime.now(), localidentifier='test',
            external_url='http://example.com')
        url = issue_detail_url(issue)
        response = self.client.get(url)
        assert response.status_code == 302
        assert response.url == 'http://example.com'


@override_settings(DEBUG=True)
class TestArticleDetailView(BaseEruditTestCase):
    def setUp(self):
        super(TestArticleDetailView, self).setUp()
        self.factory = RequestFactory()

    @unittest.mock.patch.object(FedoraMixin, 'get_erudit_object')
    def test_works_with_localidentifiers(self, mock_fedora_mixin):
        # Setup
        mock_fedora_mixin.return_value = get_mocked_erudit_object(None)
        self.journal.open_access = True
        self.journal.save()
        issue = IssueFactory.create(
            journal=self.journal, date_published=dt.datetime.now(), localidentifier='test_article')
        article = ArticleFactory.create(issue=issue)
        url = article_detail_url(article)
        request = self.factory.get(url)
        request.subscriptions = UserSubscriptions()
        request.saved_citations = []
        # Run
        response = ArticleDetailView.as_view()(
            request, localid=article.localidentifier)
        # Check
        self.assertEqual(response.status_code, 200)

    def test_fedora_issue_with_external_url_redirects(self):
        # When we have an article with a fedora localidentifier *and* external_url set, we redirect
        # to that external url when we hit the detail view.
        # ref #1651
        issue = IssueFactory.create(
            journal=self.journal, date_published=dt.datetime.now(), localidentifier='test')
        article = ArticleFactory.create(issue=issue, localidentifier='articleid',
            external_url='http://example.com')
        url = article_detail_url(article)
        response = self.client.get(url)
        assert response.status_code == 302
        assert response.url == 'http://example.com'


@override_settings(DEBUG=True)
class TestArticleRawPdfView(BaseEruditTestCase):
    @pytest.fixture(autouse=True)
    def monkeypatch_get_erudit_article(self, monkeypatch):
        monkeypatch.setattr(FedoraMixin, "get_erudit_object", get_mocked_erudit_object)

    def setUp(self):
        super(TestArticleRawPdfView, self).setUp()
        self.factory = RequestFactory()

    @unittest.mock.patch.object(ArticleDigitalObject, 'pdf')
    @unittest.mock.patch.object(ArticleDigitalObject, 'ds_list')
    @unittest.mock.patch.object(subprocess, 'check_call')
    def test_can_retrieve_the_pdf_of_existing_articles(self, mock_check_call, mock_ds, mock_pdf):
        # Setup
        with open(os.path.join(FIXTURE_ROOT, 'dummy.pdf'), 'rb') as f:
            mock_pdf.content = io.BytesIO()
            mock_pdf.content.write(f.read())
        mock_ds = ['ERUDITXSD300', ]  # noqa
        journal = JournalFactory()
        issue = IssueFactory.create(
            journal=journal, year=2010,
            date_published=dt.datetime.now() - dt.timedelta(days=1000))
        IssueFactory.create(
            journal=journal, year=2010,
            date_published=dt.datetime.now())
        article = ArticleFactory.create(issue=issue)
        journal_id = journal.localidentifier
        issue_id = issue.localidentifier
        article_id = article.localidentifier
        url = article_raw_pdf_url(article)
        request = self.factory.get(url)
        request.user = AnonymousUser()
        request.subscriptions = UserSubscriptions()

        # Run
        response = ArticleRawPdfView.as_view()(
            request, journal_code=journal_id, issue_slug=issue.volume_slug, issue_localid=issue_id,
            localid=article_id)

        # Check
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/pdf')

    def test_cannot_retrieve_the_pdf_of_inexistant_articles(self):
        # Note: as there is no Erudit fedora repository used during the
        # test, any tentative of retrieving the PDF of an article should
        # fail.

        # Setup
        journal_id = 'dummy139'
        issue_slug = 'test'
        issue_id = 'dummy1515298'
        article_id = '1001942du'
        url = reverse('public:journal:article_raw_pdf', args=(
            journal_id, issue_slug, issue_id, article_id
        ))
        # Run
        response = self.client.get(url)
        # Check that we are redirected
        self.assertEqual(response.status_code, 302)

    def test_cannot_be_accessed_if_the_article_is_not_in_open_access(self):
        # Setup
        self.journal.open_access = False
        self.journal.save()
        issue = IssueFactory.create(
            journal=self.journal, year=dt.datetime.now().year, date_published=dt.datetime.now(), use_fedora=False)
        article = ArticleFactory.create(issue=issue)
        journal_id = self.journal.localidentifier
        issue_id = issue.localidentifier
        article_id = article.localidentifier
        url = article_raw_pdf_url(article)

        request = self.factory.get(url)
        request.user = AnonymousUser()
        request.subscriptions = UserSubscriptions()

        # Run & check
        response = ArticleRawPdfView.as_view()(
            request, journal_code=journal_id, issue_slug=issue.volume_slug,
            issue_localid=issue_id, localid=article_id)

        assert isinstance(response, HttpResponseRedirect)
        assert response.url == reverse('public:journal:article_detail', args=(
            journal_id, issue.volume_slug, issue_id, article_id
        ))

    def test_cannot_be_accessed_if_the_publication_of_the_article_is_not_allowed_by_its_authors(self):  # noqa
        # Setup
        self.journal.open_access = False
        self.journal.save()
        issue = IssueFactory.create(
            journal=self.journal, year=2010, date_published=dt.datetime.now())
        article = ArticleFactory.create(issue=issue, publication_allowed=False)
        journal_id = self.journal.localidentifier
        issue_id = issue.localidentifier
        article_id = article.localidentifier
        url = article_raw_pdf_url(article)
        request = self.factory.get(url)
        request.user = AnonymousUser()

        # Run & check
        response = ArticleRawPdfView.as_view()(
            request, journal_code=journal_id, issue_slug=issue.volume_slug,
            issue_localid=issue_id, localid=article_id)

        assert isinstance(response, HttpResponseRedirect)
        assert response.url == reverse('public:journal:article_detail', args=(
            journal_id, issue.volume_slug, issue_id, article_id
        ))

    def test_fedora_issue_with_external_url_redirects(self):
        # When we have an article with a fedora localidentifier *and* external_url set, we redirect
        # to that external url when we hit the raw PDF view.
        # ref #1651
        issue = IssueFactory.create(
            journal=self.journal, date_published=dt.datetime.now(), localidentifier='test')
        article = ArticleFactory.create(issue=issue, localidentifier='articleid',
            external_url='http://example.com')
        url = article_raw_pdf_url(article)
        response = self.client.get(url)
        assert response.status_code == 302
        assert response.url == 'http://example.com'


class TestLegacyUrlsRedirection(BaseEruditTestCase):

    def test_can_redirect_issue_support_only_volume_and_year(self):
        journal = JournalFactory(code='test')
        issue = IssueFactory(journal=journal, volume="1", number="1", year="2017")
        issue_2 = IssueFactory(journal=issue.journal, volume="1", number="2", year="2017")
        article = ArticleFactory()
        article.issue.volume = "1"
        article.issue.number = "1"
        article.issue.year = "2017"
        article.issue.save()

        article2 = ArticleFactory()
        article2.issue.journal = article.issue.journal
        article2.issue.volume = "1"
        article2.issue.number = "2"
        article2.issue.year = "2017"
        article2.issue.save()
        url = "/revue/{journal_code}/{year}/v{volume}/n/".format(
            journal_code=article.issue.journal.code,
            year=article.issue.year,
            volume=article.issue.volume,
        )

        resp = self.client.get(url)

        assert resp.url == reverse('public:journal:issue_detail', kwargs=dict(
            journal_code=article2.issue.journal.code,
            issue_slug=article2.issue.volume_slug,
            localidentifier=article2.issue.localidentifier,
        ))

    def test_can_redirect_issue_detail_with_empty_volume(self):
        from django.utils.translation import deactivate_all
        issue = IssueFactory(number="1", volume="1", year="2017")
        issue2 = IssueFactory(journal=issue.journal, volume="2", number="1", year="2017")
        url = "/revue/{journal_code}/{year}/v/n{number}/".format(
            journal_code=issue.journal.code,
            number=issue.number,
            year=issue.year,
        )

        resp = self.client.get(url)

        assert resp.url == reverse('public:journal:issue_detail', kwargs=dict(
            journal_code=issue2.journal.code,
            issue_slug=issue2.volume_slug,
            localidentifier=issue2.localidentifier,
        ))

    def test_can_redirect_article_from_legacy_urls(self):
        from django.utils.translation import deactivate_all

        article = ArticleFactory()
        url = '/revue/{journal_code}/{issue_year}/v/n{issue_number}/{article_localidentifier}.html'.format(  # noqa
            journal_code=article.issue.journal.code,
            issue_year=article.issue.year,
            issue_number=article.issue.number,
            article_localidentifier=article.localidentifier
        )

        resp = self.client.get(url)

        assert resp.url == reverse('public:journal:article_detail', kwargs=dict(
            journal_code=article.issue.journal.code,
            issue_slug=article.issue.volume_slug,
            issue_localid=article.issue.localidentifier,
            localid=article.localidentifier
        ))
        assert "/fr/" in resp.url
        assert resp.status_code == 301

        deactivate_all()
        resp = self.client.get(url + "?lang=en")

        assert resp.url == reverse('public:journal:article_detail', kwargs=dict(
            journal_code=article.issue.journal.code,
            issue_slug=article.issue.volume_slug,
            issue_localid=article.issue.localidentifier,
            localid=article.localidentifier
        ))
        assert "/en/" in resp.url
        assert resp.status_code == 301

        url = '/en/revue/{journal_code}/{issue_year}/v/n{issue_number}/{article_localidentifier}.html'.format(  # noqa
            journal_code=article.issue.journal.code,
            issue_year=article.issue.year,
            issue_number=article.issue.number,
            article_localidentifier=article.localidentifier
        )
        deactivate_all()
        resp = self.client.get(url)

        assert resp.url == reverse('public:journal:article_detail', kwargs=dict(
            journal_code=article.issue.journal.code,
            issue_slug=article.issue.volume_slug,
            issue_localid=article.issue.localidentifier,
            localid=article.localidentifier
        ))

        assert "/en/" in resp.url
        assert resp.status_code == 301

    def test_can_redirect_issues_from_legacy_urls(self):
        article = ArticleFactory()
        article.issue.volume = "1"
        article.issue.number = "1"
        article.issue.save()
        url = "/revue/{journal_code}/{year}/v{volume}/n{number}/".format(
            journal_code=article.issue.journal.code,
            year=article.issue.year,
            volume=article.issue.volume,
            number=article.issue.number
        )
        resp = self.client.get(url)

        assert resp.url == reverse('public:journal:issue_detail', kwargs=dict(
            journal_code=article.issue.journal.code,
            issue_slug=article.issue.volume_slug,
            localidentifier=article.issue.localidentifier
        ))
        assert resp.status_code == 301

    def test_can_redirect_journals_from_legacy_urls(self):
        article = ArticleFactory(use_fedora=False)
        article.issue.volume = "1"
        article.issue.number = "1"
        article.issue.save()
        url = "/revue/{code}/".format(
            code=article.issue.journal.code,
        )
        resp = self.client.get(url)

        assert resp.url == reverse('public:journal:journal_detail', kwargs=dict(
            code=article.issue.journal.code,
        ))
        assert resp.status_code == 301


class TestArticleFallbackRedirection(EruditClientTestCase):

    FALLBACK_URL = settings.FALLBACK_BASE_URL

    @pytest.fixture(params=itertools.product([
        {'code': 'nonexistent'}], ['legacy_journal:legacy_journal_detail', 'legacy_journal:legacy_journal_detail_index',
        'legacy_journal:legacy_journal_authors', 'legacy_journal:legacy_journal_detail_culture',
        'legacy_journal:legacy_journal_detail_culture_index', 'legacy_journal:legacy_journal_authors_culture'
    ]))
    def journal_url(self, request):
        kwargs = request.param[0]
        url = request.param[1]
        return reverse(url, kwargs=kwargs)

    @pytest.fixture(params=itertools.chain(
            itertools.product(
                [{
                    'journal_code': 'nonexistent',
                    'year': "1974",
                    'v': "7",
                    'n': "1",
                }],
                ["legacy_journal:legacy_issue_detail", "legacy_journal:legacy_issue_detail_index"]
            ),
            itertools.product([{
                'journal_code': 'nonexistent',
                'year': "1974",
                'v': "7",
                }], ["legacy_journal:legacy_issue_detail_no_number",
                     "legacy_journal:legacy_issue_detail_index_no_number"],
            ),
            itertools.product([{
                'journal_code': 'nonexistent',
                'year': "1974",
                'v': "7",
                }], ["legacy_journal:legacy_issue_detail_no_number",
                     "legacy_journal:legacy_issue_detail_index_no_number"],
            ),
            itertools.product([{
                'journal_code': 'nonexistent',
                'localidentifier': 'nonexistent'
            }], ["legacy_journal:legacy_issue_detail_culture",
                 "legacy_journal:legacy_issue_detail_culture_index"],
            )
    ))
    def issue_url(self, request):
        kwargs = request.param[0]
        url = request.param[1]
        return reverse(url, kwargs=kwargs)

    @pytest.fixture(params=itertools.chain(
            itertools.product([{
                'journal_code': 'nonexistent', 'year': 2004, 'v': 1, 'issue_number': 'nonexistent',
                'localid': 'nonexistent', 'format_identifier': 'html', 'lang': 'fr'
                }], ["legacy_journal:legacy_article_detail",
                     "legacy_journal:legacy_article_detail_culture"],
            ),
            [
                ({'localid': 'nonexistent'}, 'legacy_journal:legacy_article_id'),
                ({'journal_code': 'nonexistent',
                  'issue_localid': 'nonexistent', 'localid': 'nonexistent',
                  'format_identifier': 'html'},
                 'legacy_journal:legacy_article_detail_culture_localidentifier')
            ]
        ),
    )
    def article_url(self, request):
        kwargs = request.param[0]
        url = request.param[1]
        return reverse(url, kwargs=kwargs)

    def test_legacy_url_for_nonexistent_journals_redirects_to_fallback_website(self, journal_url):
        response = self.client.get(journal_url)
        redirect_url = response.url
        assert self.FALLBACK_URL in redirect_url


    def test_legacy_url_for_nonexistent_issues_redirect_to_fallback_website(self, issue_url):
        response = self.client.get(issue_url)
        redirect_url = response.url
        assert self.FALLBACK_URL in redirect_url

    def test_legacy_url_for_nonexistent_article_redirect_to_fallback_website(self, article_url):
        response = self.client.get(article_url)
        redirect_url = response.url
        assert self.FALLBACK_URL in redirect_url


@override_settings(DEBUG=True)
class TestArticleXmlView(BaseEruditTestCase):
    def setUp(self):
        super(TestArticleXmlView, self).setUp()
        self.factory = RequestFactory()

    @unittest.mock.patch.object(ArticleDigitalObject, 'erudit_xsd300')
    @unittest.mock.patch.object(ArticleDigitalObject, 'ds_list')
    def test_can_retrieve_xml_of_existing_articles(self, mock_ds, mock_pdf):

        with open(os.path.join(FIXTURE_ROOT, '1023796ar.xml'), 'r') as f:
            from eulxml.xmlmap import load_xmlobject_from_file
            mock_pdf.content = load_xmlobject_from_file(f)
        mock_ds = ['ERUDITXSD300', ]  # noqa

        issue = IssueFactory.create(
            journal=self.journal, year=2010,
            date_published=dt.datetime.now() - dt.timedelta(days=1000))
        IssueFactory.create(
            journal=self.journal, year=2010,
            date_published=dt.datetime.now())
        article = ArticleFactory.create(issue=issue)
        journal_id = self.journal.localidentifier
        issue_id = issue.localidentifier
        article_id = article.localidentifier
        url = reverse('public:journal:article_raw_xml', args=(
            journal_id, issue.volume_slug, issue_id, article_id
        ))
        request = self.factory.get(url)
        request.user = AnonymousUser()
        request.subscriptions = UserSubscriptions()

        # Run
        response = ArticleXmlView.as_view()(
            request, journal_code=journal_id, issue_slug=issue.volume_slug, issue_localid=issue_id,
            localid=article_id)

        # Check
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/xml')


class TestArticleMediaView(BaseEruditTestCase):
    def setUp(self):
        super(TestArticleMediaView, self).setUp()
        self.factory = RequestFactory()

    @unittest.mock.patch.object(MediaDigitalObject, 'content')
    def test_can_retrieve_the_pdf_of_existing_articles(self, mock_content):
        # Setup
        with open(os.path.join(FIXTURE_ROOT, 'pixel.png'), 'rb') as f:
            mock_content.content = io.BytesIO()
            mock_content.content.write(f.read())
        mock_content.mimetype = 'image/png'

        issue = IssueFactory.create(journal=self.journal, date_published=dt.datetime.now())
        article = ArticleFactory.create(issue=issue)
        issue_id = issue.localidentifier
        article_id = article.localidentifier
        request = self.factory.get('/')

        # Run
        response = ArticleMediaView.as_view()(
            request, journal_code=self.journal.code, issue_localid=issue_id,
            localid=article_id, media_localid='test')

        # Check
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'image/png')


class TestExternalURLRedirectViews(BaseEruditTestCase):

    def setUp(self):
        super().setUp()
        self.client = Client()

    def test_can_redirect_to_article_external_url(self):
        issue = IssueFactory.create(journal=self.journal, date_published=dt.datetime.now())
        article = ArticleFactory.create(issue=issue, external_url='http://www.erudit.org')
        response = self.client.get(
            reverse(
                'public:journal:article_external_redirect',
                kwargs={'localidentifier': article.localidentifier}
            )
        )
        assert response.status_code == 302

    def test_can_redirect_to_issue_external_url(self):
        issue = IssueFactory.create(
            journal=self.journal,
            date_published=dt.datetime.now(),
            external_url="http://www.erudit.org"
        )

        response = self.client.get(
            reverse(
                'public:journal:issue_external_redirect',
                kwargs={'localidentifier': issue.localidentifier}
            )
        )
        assert response.status_code == 302

    def test_can_redirect_to_journal_external_url(self):
        journal = JournalFactory(code='journal1', external_url='http://www.erudit.org')
        response = self.client.get(
            reverse(
                'public:journal:journal_external_redirect',
                kwargs={'code': journal.code}
            )
        )
        assert response.status_code == 302
