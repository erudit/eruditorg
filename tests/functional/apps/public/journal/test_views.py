from typing import List

from bs4 import BeautifulSoup
from lxml import etree as et

import datetime as dt
import io
import os
import unittest.mock
import subprocess
import itertools
from hashlib import md5

from django.contrib.auth.models import AnonymousUser
from django.urls import reverse
from django.http.response import HttpResponseRedirect
from django.test import Client
from django.test import TestCase, RequestFactory
from django.conf import settings
from django.test.utils import override_settings
import pytest

from apps.public.journal.viewmixins import SolrDataMixin
from core.subscription.test.utils import generate_casa_token
from erudit.models import JournalType, Issue, Article
from erudit.test.factories import ArticleFactory
from erudit.test.factories import CollectionFactory
from erudit.test.factories import DisciplineFactory
from erudit.test.factories import IssueFactory
from erudit.test.factories import EmbargoedIssueFactory
from erudit.test.factories import OpenAccessIssueFactory
from erudit.test.factories import JournalFactory
from erudit.test.factories import JournalInformationFactory
from erudit.fedora.objects import JournalDigitalObject
from erudit.fedora.objects import ArticleDigitalObject
from erudit.fedora.objects import MediaDigitalObject
from erudit.fedora import repository

from base.test.factories import UserFactory
from core.subscription.test.factories import JournalAccessSubscriptionFactory
from core.subscription.models import UserSubscriptions
from core.subscription.test.factories import JournalManagementSubscriptionFactory
from core.metrics.conf import settings as metrics_settings

from apps.public.journal.views import ArticleMediaView
from apps.public.journal.views import ArticleRawPdfView
from apps.public.journal.views import ArticleRawPdfFirstPageView

FIXTURE_ROOT = os.path.join(os.path.dirname(__file__), 'fixtures')


pytestmark = pytest.mark.django_db


def journal_detail_url(journal):
    return reverse('public:journal:journal_detail', kwargs={'code': journal.code})


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


class TestJournalListView:

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
        JournalFactory.create_with_issue(collection=collection)
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

    def test_can_filter_the_journals_by_disciplines(self):
        j1 = JournalFactory.create_with_issue(disciplines=['d1', 'd2'])
        j2 = JournalFactory.create_with_issue(disciplines=['d2'])
        j3 = JournalFactory.create_with_issue(disciplines=['d3'])
        JournalFactory.create_with_issue(disciplines=['d4'])
        url = reverse('public:journal:journal_list')
        response = self.client.get(url, data={'disciplines': ['d2', 'd3']})
        assert set(response.context['journals']) == {j1, j2, j3}


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
        journal_info = JournalInformationFactory(journal=JournalFactory())
        url_1 = journal_detail_url(journal_info.journal)
        journal_2 = JournalFactory()
        url_2 = journal_detail_url(journal_2)

        # Run
        response_1 = self.client.get(url_1)
        response_2 = self.client.get(url_2)

        # Check
        assert response_1.status_code == response_2.status_code == 200

        assert response_1.context['journal_info'] == journal_info
        assert response_2.context['journal_info'] == {'updated': None}

    def test_can_display_when_issues_have_a_space_in_their_number(self, monkeypatch):
        monkeypatch.setattr(Issue, 'has_coverpage', unittest.mock.Mock(return_value=True))
        monkeypatch.setattr(Issue, 'erudit_object', unittest.mock.MagicMock())
        issue = IssueFactory(number='2 bis')
        url_1 = journal_detail_url(issue.journal)
        # Run
        response_1 = self.client.get(url_1)
        assert response_1.status_code == 200

    def test_can_embed_the_published_issues_in_the_context(self):
        # Setup

        journal = JournalFactory(collection=CollectionFactory(localidentifier='erudit'))

        issue = IssueFactory(journal=journal)
        IssueFactory(journal=journal, is_published=False)

        url = journal_detail_url(journal)
        # Run
        response = self.client.get(url)
        # Check
        assert response.status_code == 200
        assert list(response.context['issues']) == [issue]

    def test_can_embed_the_current_issue_in_the_context(self):
        issue1 = IssueFactory.create()
        issue2 = IssueFactory.create_published_after(issue1)

        url = journal_detail_url(issue1.journal)
        response = self.client.get(url)

        assert response.status_code == 200
        assert response.context['current_issue'] == issue2

    def test_can_embed_the_current_issue_external_url_in_the_context(self):
        # If the latest issue has an external URL, it's link properly reflects that (proper href,
        # blank target.
        external_url = 'https://example.com'
        issue1 = IssueFactory.create()
        issue2 = IssueFactory.create_published_after(issue1, external_url=external_url)

        url = journal_detail_url(issue1.journal)
        response = self.client.get(url)

        assert response.status_code == 200
        assert response.context['current_issue'] == issue2
        link_attrs = response.context['current_issue'].extra.detail_link_attrs()
        assert external_url in link_attrs
        assert '_blank' in link_attrs

    def test_external_issues_are_never_locked(self):
        # when an issue has an external url, we never show a little lock icon next to it.
        external_url = 'https://example.com'
        collection = CollectionFactory.create(code='erudit')
        journal = JournalFactory(open_access=False, collection=collection)  # embargoed
        issue1 = IssueFactory.create(journal=journal, external_url=external_url)

        url = journal_detail_url(issue1.journal)
        response = self.client.get(url)

        assert not response.context['current_issue'].extra.is_locked()

    def test_embeds_subscription_info_to_context(self):
        subscription = JournalAccessSubscriptionFactory(
            type='individual',
            user=self.user,
            valid=True,
        )
        self.client.login(username='foobar', password='notsecret')
        url = journal_detail_url(subscription.journal_management_subscription.journal)
        response = self.client.get(url)
        assert response.status_code == 200
        assert response.context['content_access_granted']
        assert response.context['subscription_type'] == 'individual'

    def test_journal_detail_has_elements_for_anchors(self):
        issue = IssueFactory()
        url = journal_detail_url(issue.journal)
        response = self.client.get(url)
        content = response.content
        assert b'<li role="presentation"' in content
        assert b'<section role="tabpanel"' in content
        assert b'<li role="presentation" id="journal-info-about-li"' not in content
        assert b'<section role="tabpanel" class="tab-pane journal-info-block" id="journal-info-about"' not in content

    @pytest.mark.parametrize('charges_apc', (True, False))
    def test_journal_detail_has_no_apc_mention_if_it_charges_apc(self, charges_apc):
        journal = JournalFactory(charges_apc=charges_apc)
        url = journal_detail_url(journal)
        response = self.client.get(url)
        content = response.content

        if not charges_apc:
            assert b'Frais de publication' in content
        else:
            assert b'Frais de publication' not in content


class TestJournalAuthorsListView:
    def test_provides_only_authors_for_the_first_available_letter_by_default(self):
        issue_1 = IssueFactory.create(date_published=dt.datetime.now())
        ArticleFactory.create(issue=issue_1, authors=['btest', 'ctest1', 'ctest2'])

        url = reverse('public:journal:journal_authors_list', kwargs={'code': issue_1.journal.code})
        response = Client().get(url)

        assert response.status_code == 200
        assert set(response.context['authors_dicts'].keys()) == {'btest', }

    def test_only_provides_authors_for_the_given_letter(self):
        issue_1 = IssueFactory.create(date_published=dt.datetime.now())
        ArticleFactory.create(issue=issue_1, authors=['btest', 'ctest1'])
        url = reverse('public:journal:journal_authors_list', kwargs={'code': issue_1.journal.code})
        response = Client().get(url, letter='b')

        assert response.status_code == 200
        authors_dicts = response.context['authors_dicts']
        assert len(authors_dicts) == 1
        assert authors_dicts.keys() == {'btest', }

    def test_can_provide_contributors_of_article(self):
        issue_1 = IssueFactory.create(date_published=dt.datetime.now())
        ArticleFactory.create(issue=issue_1, authors=['btest', 'ctest1'])
        url = reverse('public:journal:journal_authors_list', kwargs={'code': issue_1.journal.code})
        response = Client().get(url, letter='b')

        assert response.status_code == 200
        authors_dicts = response.context['authors_dicts']
        contributors = authors_dicts['btest'][0]['contributors']
        assert contributors == ['ctest1']

    def test_dont_show_unpublished_articles(self):
        issue1 = IssueFactory.create(is_published=False)
        issue2 = IssueFactory.create(journal=issue1.journal, is_published=True)
        ArticleFactory.create(issue=issue1, authors=['foo'])
        ArticleFactory.create(issue=issue2, authors=['foo'])

        # Unpublished articles aren't in solr
        url = reverse('public:journal:journal_authors_list', kwargs={'code': issue1.journal.code})
        response = Client().get(url, letter='f')

        authors_dicts = response.context['authors_dicts']
        # only one of the two articles are there
        assert len(authors_dicts['foo']) == 1

    def test_can_filter_by_article_type(self):
        issue_1 = IssueFactory.create(date_published=dt.datetime.now())
        ArticleFactory.create(issue=issue_1, type='article', authors=['btest'])
        ArticleFactory.create(issue=issue_1, type='compterendu', authors=['btest'])

        url = reverse('public:journal:journal_authors_list', kwargs={'code': issue_1.journal.code})
        response = Client().get(url, article_type='article')
        assert response.status_code == 200
        authors_dicts = response.context['authors_dicts']
        assert len(authors_dicts) == 1

    def test_can_filter_by_article_type_when_no_article_of_type(self):
        issue_1 = IssueFactory.create(date_published=dt.datetime.now())
        ArticleFactory.create(issue=issue_1, type='article', authors=['atest'])
        url = reverse('public:journal:journal_authors_list', kwargs={'code': issue_1.journal.code})
        response = Client().get(url, {"article_type": 'compterendu'})

        assert response.status_code == 200

    def test_only_letters_with_results_are_active(self):
        """ Test that for a given selection in the authors list view, only the letters for which
        results are present are shown """
        issue_1 = IssueFactory.create(journal=JournalFactory(), date_published=dt.datetime.now())
        ArticleFactory.create(issue=issue_1, type='article', authors=['atest'])
        ArticleFactory.create(issue=issue_1, type='compterendu', authors=['btest'])
        url = reverse('public:journal:journal_authors_list', kwargs={'code': issue_1.journal.code})
        response = Client().get(url, {"article_type": 'compterendu'})

        assert response.status_code == 200
        assert not response.context['letters_exists'].get('A')

    def test_do_not_fail_when_user_requests_a_letter_with_no_articles(self):
        issue_1 = IssueFactory.create(date_published=dt.datetime.now())
        ArticleFactory.create(issue=issue_1, type='article', authors=['btest'])

        url = reverse('public:journal:journal_authors_list', kwargs={'code': issue_1.journal.code})
        response = Client().get(url, {"article_type": 'compterendu', 'letter': 'A'})

        assert response.status_code == 200

    def test_inserts_the_current_letter_in_the_context(self):
        issue_1 = IssueFactory.create(date_published=dt.datetime.now())
        ArticleFactory.create(issue=issue_1, authors=['btest', 'ctest1', 'ctest2'])

        url = reverse('public:journal:journal_authors_list', kwargs={'code': issue_1.journal.code})
        response_1 = Client().get(url)
        response_2 = Client().get(url, {'letter': 'C'})
        response_3 = Client().get(url, {'letter': 'invalid'})

        assert response_1.status_code == 200
        assert response_1.status_code == 200
        assert response_1.status_code == 200
        assert response_1.context['letter'] == 'B'
        assert response_2.context['letter'] == 'C'
        assert response_3.context['letter'] == 'B'

    def test_inserts_a_dict_with_the_letters_counts_in_the_context(self):
        issue_1 = IssueFactory.create(date_published=dt.datetime.now())
        ArticleFactory.create(issue=issue_1, authors=['btest', 'ctest1', 'ctest2'])

        url = reverse('public:journal:journal_authors_list', kwargs={'code': issue_1.journal.code})
        response = Client().get(url)

        assert response.status_code == 200
        assert len(response.context['letters_exists']) == 26
        assert response.context['letters_exists']['B']
        assert response.context['letters_exists']['C']
        for letter in 'adefghijklmnopqrstuvwxyz':
            assert not response.context['letters_exists'][letter.upper()]

    @pytest.mark.parametrize('article_type,expected', [('compterendu', True), ('article', False)])
    def test_view_has_multiple_article_types(self, article_type, expected):
        article1 = ArticleFactory.create(type='article', authors=['btest'])
        ArticleFactory.create(issue=article1.issue, type=article_type, authors=['btest'])

        url = reverse(
            'public:journal:journal_authors_list',
            kwargs={'code': article1.issue.journal.code})
        response = Client().get(url)

        assert response.context['view'].has_multiple_article_types == expected


class TestIssueDetailView:
    def test_works_with_pks(self):
        issue = IssueFactory.create(date_published=dt.datetime.now())
        url = issue_detail_url(issue)
        response = Client().get(url)
        assert response.status_code == 200

    @pytest.mark.parametrize("is_published,has_ticket,expected_code", [
        (True, False, 200),
        (True, True, 200),
        (False, False, 302),
        (False, True, 200),
    ])
    def test_can_accept_prepublication_ticket(self, is_published, has_ticket, expected_code):
        localidentifier = "espace03368"
        issue = IssueFactory(localidentifier=localidentifier, is_published=is_published)
        url = issue_detail_url(issue)
        data = None
        if has_ticket:
            ticket = md5(localidentifier.encode()).hexdigest()
            data = {'ticket': ticket}
        response = Client().get(url, data=data)
        assert response.status_code == expected_code

    def test_works_with_localidentifiers(self):
        issue = IssueFactory.create(
            date_published=dt.datetime.now(), localidentifier='test')
        url = issue_detail_url(issue)
        response = Client().get(url)
        assert response.status_code == 200

    def test_fedora_issue_with_external_url_redirects(self):
        # When we have an issue with a fedora localidentifier *and* external_url set, we redirect
        # to that external url when we hit the detail view.
        # ref #1651
        issue = IssueFactory.create(
            date_published=dt.datetime.now(), localidentifier='test',
            external_url='http://example.com')
        url = issue_detail_url(issue)
        response = Client().get(url)
        assert response.status_code == 302
        assert response.url == 'http://example.com'

    def test_can_render_issue_summary_when_db_contains_articles_not_in_summary(self):
        # Articles in the issue view are ordered according to the list specified in the erudit
        # object. If an article isn't referenced in the erudit object list, then it will not be
        # shown. We rely on the fact that the default patched issue points to liberte1035607
        # ref support#216
        issue = IssueFactory.create()
        a1 = ArticleFactory.create(issue=issue, localidentifier='31492ac')
        a2 = ArticleFactory.create(issue=issue, localidentifier='31491ac')
        ArticleFactory.create(issue=issue, localidentifier='not-there', add_to_fedora_issue=False)
        url = issue_detail_url(issue)
        response = Client().get(url)
        articles = response.context['articles']
        assert articles == [a1, a2]

    @pytest.mark.parametrize("factory, expected_lock", [
        (EmbargoedIssueFactory, True),
        (OpenAccessIssueFactory, False),
    ])
    def test_embargo_lock_icon(self, factory, expected_lock):
        issue = factory(is_published=False)
        url = issue_detail_url(issue)
        response = Client().get(url, {'ticket': issue.prepublication_ticket})
        # The embargo lock icon should never be displayed when a prepublication ticket is provided.
        assert b'ion-ios-lock' not in response.content
        issue.is_published = True
        issue.save()
        response = Client().get(url)
        # The embargo lock icon should only be displayed on embargoed issues.
        assert (b'ion-ios-lock' in response.content) == expected_lock

    def test_article_items_are_not_cached_for_unpublished_issues(self):
        issue = IssueFactory(is_published=False)
        article = ArticleFactory(issue=issue, title="thisismyoldtitle")

        url = issue_detail_url(issue)
        resp = Client().get(url, {'ticket': issue.prepublication_ticket})
        assert "thisismyoldtitle" in resp.content.decode('utf-8')

        with repository.api.open_article(article.pid) as wrapper:
            wrapper.set_title('thisismynewtitle')
        resp = Client().get(url, {'ticket': issue.prepublication_ticket})
        assert "thisismynewtitle" in resp.content.decode('utf-8')

    @override_settings(CACHES=settings.LOCMEM_CACHES)
    def test_article_items_are_cached_for_published_issues(self):
        issue = IssueFactory(is_published=True)
        article = ArticleFactory(issue=issue, title="thisismyoldtitle")

        url = issue_detail_url(issue)
        resp = Client().get(url)
        assert "thisismyoldtitle" in resp.content.decode('utf-8')

        with repository.api.open_article(article.pid) as wrapper:
            wrapper.set_title('thisismynewtitle')
        resp = Client().get(url, {'ticket': issue.prepublication_ticket})
        assert "thisismyoldtitle" in resp.content.decode('utf-8')


    def test_can_return_301_when_issue_doesnt_exist(self):
        issue = IssueFactory.create(
            date_published=dt.datetime.now(), localidentifier='test')
        issue.localidentifier = 'fail'
        url = issue_detail_url(issue)
        response = Client().get(url)
        assert response.status_code == 301


class FakeSolrData:
    # noinspection PyMethodMayBeStatic,PyUnusedLocal
    def get_all_journal_articles(self, journal_code: str) -> List[Article]:
        return []


class TestArticleDetailView:

    @pytest.fixture(autouse=True)
    def article_detail_solr_data(self, monkeypatch):
        monkeypatch.setattr(SolrDataMixin, 'solr_data', FakeSolrData())

    @pytest.mark.parametrize('method', [
        'get', 'options'
    ])
    def test_can_render_erudit_articles(self, monkeypatch, eruditarticle, method):
        # The goal of this test is to verify that out erudit article mechanism doesn't crash for
        # all kinds of articles. We have many articles in our fixtures and the `eruditarticle`
        # argument here is a parametrization argument which causes this test to run for each
        # fixture we have.
        monkeypatch.setattr(metrics_settings, 'ACTIVATED', False)
        monkeypatch.setattr(Article, 'get_erudit_object', lambda *a, **kw: eruditarticle)
        journal = JournalFactory.create(open_access=True)
        issue = IssueFactory.create(
            journal=journal, date_published=dt.datetime.now(), localidentifier='test_issue')
        article = ArticleFactory.create(issue=issue, localidentifier='test_article')
        url = article_detail_url(article)
        response = getattr(Client(), method)(url)
        assert response.status_code == 200

    @pytest.mark.parametrize("is_published,has_ticket,expected_code", [
        (True, False, 200),
        (True, True, 200),
        (False, False, 302),
        (False, True, 200),
    ])
    def test_can_accept_prepublication_ticket(self, is_published, has_ticket, expected_code):
        localidentifier = "espace03368"
        issue = IssueFactory(localidentifier=localidentifier, is_published=is_published)
        article = ArticleFactory(issue=issue)
        url = article_detail_url(article)
        data = None
        if has_ticket:
            ticket = md5(localidentifier.encode()).hexdigest()
            data = {'ticket': ticket}
        response = Client().get(url, data=data)
        assert response.status_code == expected_code

    @pytest.mark.parametrize("is_published,ticket_expected", [
        (True, False),
        (False, True),
    ])
    def test_prepublication_ticket_is_propagated_to_other_pages(self, is_published, ticket_expected):
        localidentifier = "espace03368"
        issue = IssueFactory(localidentifier=localidentifier, is_published=is_published)
        articles = ArticleFactory.create_batch(issue=issue, size=3)
        article = articles[1]
        url = article_detail_url(article)
        ticket = md5(localidentifier.encode()).hexdigest()
        response = Client().get(url, data={'ticket': ticket})

        from io import StringIO
        tree = et.parse(StringIO(response.content.decode()), et.HTMLParser())

        # Test that the ticket is in the breadcrumbs
        bc_hrefs = [e.get('href') for e in tree.findall('.//nav[@id="breadcrumbs"]//a')]
        pa_hrefs = [e.get('href') for e in tree.findall('.//div[@class="pagination-arrows"]/a')]

        # This is easier to debug than a generator
        for href in bc_hrefs + pa_hrefs:
            assert ('ticket' in href) == ticket_expected

    def test_dont_cache_html_of_articles_of_unpublished_issues(self):
        issue = IssueFactory.create(is_published=False)
        article = ArticleFactory.create(issue=issue, title='thiswillendupinhtml')
        url = '{}?ticket={}'.format(article_detail_url(article), issue.prepublication_ticket)
        response = Client().get(url)
        assert response.status_code == 200
        assert b'thiswillendupinhtml' in response.content

        with repository.api.open_article(article.pid) as wrapper:
            wrapper.set_title('thiswillreplaceoldinhtml')
        response = Client().get(url)
        assert response.status_code == 200
        assert b'thiswillendupinhtml' not in response.content
        assert b'thiswillreplaceoldinhtml' in response.content

    def test_dont_cache_fedora_objects_of_articles_of_unpublished_issues(self):

        with unittest.mock.patch('erudit.fedora.modelmixins.cache') as cache_mock:
            cache_mock.get.return_value = None
            issue = IssueFactory.create(is_published=False)
            article = ArticleFactory.create(issue=issue)
            url = '{}?ticket={}'.format(article_detail_url(article), issue.prepublication_ticket)
            response = Client().get(url)
            assert response.status_code == 200
            # Assert that the cache has not be called.
            assert cache_mock.get.call_count == 0

    def test_allow_ephemeral_articles(self):
        # When receiving a request for an article that doesn't exist in the DB, try querying fedora
        # for the requested PID before declaring a failure.
        issue = IssueFactory.create()
        article_localidentifier = 'foo'
        repository.api.register_article(
            '{}.{}'.format(issue.get_full_identifier(), article_localidentifier)
        )
        url = reverse('public:journal:article_detail', kwargs={
            'journal_code': issue.journal.code, 'issue_slug': issue.volume_slug,
            'issue_localid': issue.localidentifier, 'localid': article_localidentifier})
        response = Client().get(url)
        assert response.status_code == 200

    def test_querystring_doesnt_mess_media_urls(self):
        journal = JournalFactory(open_access=True)  # so we see the whole article
        issue = IssueFactory(journal=journal)
        article = ArticleFactory(issue=issue, from_fixture='1003446ar')  # this article has media
        url = '{}?foo=bar'.format(article_detail_url(article))
        response = Client().get(url)
        # we have some media urls
        assert b'media/' in response.content
        # We don't have any messed up media urls, that is, an URL with our querystring in the
        # middle
        assert b'barmedia/' not in response.content

    @unittest.mock.patch('erudit.fedora.cache.cache')
    @unittest.mock.patch('erudit.fedora.cache.get_datastream_file_cache')
    @unittest.mock.patch('erudit.fedora.cache.get_cached_datastream_content')
    @pytest.mark.parametrize('is_published, expected_count', [
        # When an issue is not published, we should not get any cache.get() calls when displaying
        # an article's PDF.
        (False, 0),
        # When an issue is published, we should get one cache.get() calls when displaying an
        # article's PDF.
        (True, 1),
    ])
    def test_pdf_datastream_caching(self, mock_cache, mock_get_datastream_file_cache,
                                    mock_get_cached_datastream_content, is_published,
                                    expected_count):
        mock_cache.get.return_value = None
        mock_get_datastream_file_cache.return_value = mock_cache
        mock_get_cached_datastream_content.return_value = None

        article = ArticleFactory(
            issue__is_published=is_published,
            issue__journal__open_access=True,
        )
        url = reverse('public:journal:article_raw_pdf', kwargs={
            'journal_code': article.issue.journal.code,
            'issue_slug': article.issue.volume_slug,
            'issue_localid': article.issue.localidentifier,
            'localid': article.localidentifier,
        })
        mock_cache.get.reset_mock()

        response = Client().get(url, {
            'ticket': article.issue.prepublication_ticket,
        })
        assert mock_cache.get.call_count == expected_count

    @unittest.mock.patch('erudit.fedora.modelmixins.cache')
    @pytest.mark.parametrize('is_published, expected_count', [
        # When an issue is not published, we should not get any cache.get() calls when displaying
        # an article's XML.
        (False, 0),
        # When an issue is published, we should get one cache.get() calls when displaying an
        # article's XML.
        (True, 1),
    ])
    def test_xml_datastream_caching(self, mock_cache, is_published, expected_count):
        mock_cache.get.return_value = None

        article = ArticleFactory(
            issue__is_published=is_published,
            issue__journal__open_access=True,
        )
        url = reverse('public:journal:article_raw_xml', kwargs={
            'journal_code': article.issue.journal.code,
            'issue_slug': article.issue.volume_slug,
            'issue_localid': article.issue.localidentifier,
            'localid': article.localidentifier,
        })
        mock_cache.get.reset_mock()

        response = Client().get(url, {
            'ticket': article.issue.prepublication_ticket,
        })
        assert mock_cache.get.call_count == expected_count

    def test_that_article_titles_are_truncated_in_breadcrumb(self):
        article = ArticleFactory(
            from_fixture='1056823ar',
            localidentifier='article',
            issue__localidentifier='issue',
            issue__year='2000',
            issue__journal__code='journal',
        )
        url = reverse('public:journal:article_detail', kwargs={
            'journal_code': article.issue.journal.code,
            'issue_slug': article.issue.volume_slug,
            'issue_localid': article.issue.localidentifier,
            'localid': article.localidentifier,
        })
        response = Client().get(url)
        html = response.content.decode()
        assert '<a href="/fr/revues/journal/2000-issue/article/">Jean-Guy Desjardins, Traité de ' \
               'l’évaluation foncière, Montréal, Wilson &amp; Lafleur ...</a>' in html

    def test_keywords_html_tags(self):
        article = ArticleFactory(from_fixture='1055883ar')
        url = reverse('public:journal:article_detail', kwargs={
            'journal_code': article.issue.journal.code,
            'issue_slug': article.issue.volume_slug,
            'issue_localid': article.issue.localidentifier,
            'localid': article.localidentifier,
        })
        response = Client().get(url)
        html = response.content.decode()
        # Check that HTML tags are displayed in the body.
        assert '<ul>\n<li class="keyword">Charles Baudelaire, </li>\n<li class="keyword">\n' \
               '<em>Fleurs du Mal</em>, </li>\n<li class="keyword">Seine, </li>\n' \
               '<li class="keyword">mythe et réalité de Paris, </li>\n' \
               '<li class="keyword">poétique du miroir</li>\n</ul>' in html
        # Check that HTML tags are not displayed in the head.
        assert '<meta name="citation_keywords" lang="fr" content="Charles Baudelaire, Fleurs du ' \
               'Mal, Seine, mythe et réalité de Paris, poétique du miroir" />' in html

    def test_article_pdf_links(self):
        article = ArticleFactory(
            with_pdf=True,
            from_fixture='602354ar',
            localidentifier='602354ar',
            issue__year='2000',
            issue__localidentifier='issue',
            issue__is_published=False,
            issue__journal__code='journal',
            issue__journal__open_access=True,
        )
        url = reverse('public:journal:article_detail', kwargs={
            'journal_code': article.issue.journal.code,
            'issue_slug': article.issue.volume_slug,
            'issue_localid': article.issue.localidentifier,
            'localid': article.localidentifier,
        })
        response = Client().get(url, {
            'ticket': article.issue.prepublication_ticket if not article.issue.is_published else '',
        })
        html = response.content.decode()

        # Check that the PDF download button URL has the prepublication ticket if the issue is not
        # published.
        assert '<a class="tool-btn tool-download" ' \
               'data-href="/fr/revues/journal/2000-issue/602354ar.pdf?' \
               'ticket=0aae4c8f3cc35693d0cbbe631f2e8b52"><span class="toolbox-pdf">PDF</span>' \
               '<span class="tools-label">Télécharger</span></a>' in html
        # Check that the PDF menu link URL has the prepublication ticket if the issue is not
        # published.
        assert '<a href="#pdf-viewer" id="pdf-viewer-menu-link">Texte intégral (PDF)</a>' \
               '<a href="/fr/revues/journal/2000-issue/602354ar.pdf?' \
               'ticket=0aae4c8f3cc35693d0cbbe631f2e8b52" id="pdf-download-menu-link" ' \
               'target="_blank">Texte intégral (PDF)</a>' in html
        # Check that the embeded PDF URL has the prepublication ticket if the issue is not
        # published.
        assert '<object id="pdf-viewer" data="/fr/revues/journal/2000-issue/602354ar.pdf?' \
               'embed&amp;ticket=0aae4c8f3cc35693d0cbbe631f2e8b52" type="application/pdf" ' \
               'width="100%" height="700px"></object>' in html
        # Check that the PDF download link URL has the prepublication ticket if the issue is not
        # published.
        assert '<a href="/fr/revues/journal/2000-issue/602354ar.pdf?' \
               'ticket=0aae4c8f3cc35693d0cbbe631f2e8b52" class="btn btn-secondary" ' \
               'target="_blank">Télécharger</a>' in html

        article.issue.is_published = True
        article.issue.save()
        response = Client().get(url)
        html = response.content.decode()

        # Check that the PDF download button URL does not have the prepublication ticket if the
        # issue is published.
        assert '<a class="tool-btn tool-download" data-href="/fr/revues/journal/2000-issue/' \
               '602354ar.pdf"><span class="toolbox-pdf">PDF</span><span ' \
               'class="tools-label">Télécharger</span></a>' in html
        # Check that the PDF menu link URL does not have the prepublication ticket if the issue
        # is published.
        assert '<a href="#pdf-viewer" id="pdf-viewer-menu-link">Texte intégral (PDF)</a>' \
               '<a href="/fr/revues/journal/2000-issue/602354ar.pdf" id="pdf-download-menu-link" ' \
               'target="_blank">Texte intégral (PDF)</a>' in html
        # Check that the embeded PDF URL does not have the prepublication ticket if the issue is
        # published.
        assert '<object id="pdf-viewer" data="/fr/revues/journal/2000-issue/602354ar.pdf?' \
               'embed" type="application/pdf" width="100%" height="700px"></object>' in html
        # Check that the PDF download link URL does not have the prepublication ticket if the issue
        # is published.
        assert '<a href="/fr/revues/journal/2000-issue/602354ar.pdf" class="btn btn-secondary" ' \
               'target="_blank">Télécharger</a>' in html

    @pytest.mark.parametrize('kwargs, nonce_count, authorized', (
        # Valid token
        ({}, 1, True),
        # Badly formed token
        ({'token_separator': '!'}, 1, False),
        # Invalid nonce
        ({'invalid_nonce': True}, 1, False),
        # Invalid message
        ({'invalid_message': True}, 1, False),
        # Invalid signature
        ({'invalid_signature': True}, 1, False),
        # Nonce seen more than 3 times
        ({}, 4, False),
        # Badly formatted payload
        ({'payload_separator': '!'}, 1, False),
        # Expired token
        ({'time_delta': 3600000001}, 1, False),
        # Wrong IP
        ({'ip_subnet': '8.8.8.0/24'}, 1, False),
        # Invalid subscription
        ({'subscription_id': 2}, 1, False),
    ))
    @pytest.mark.parametrize('url_name', (
        ('public:journal:article_detail'),
        ('public:journal:article_raw_pdf'),
    ))
    @unittest.mock.patch('core.subscription.middleware.SubscriptionMiddleware._nonce_count')
    @override_settings(GOOGLE_CASA_KEY='74796E8FF6363EFF91A9308D1D05335E')
    def test_article_detail_with_google_casa_token(self, mock_nonce_count, url_name, kwargs,
                                                   nonce_count, authorized):
        mock_nonce_count.return_value = nonce_count
        article = ArticleFactory()
        JournalAccessSubscriptionFactory(
            pk=1,
            post__valid=True,
            post__journals=[article.issue.journal],
        )
        url = reverse(url_name, kwargs={
            'journal_code': article.issue.journal.code,
            'issue_slug': article.issue.volume_slug,
            'issue_localid': article.issue.localidentifier,
            'localid': article.localidentifier,
        })
        response = Client().get(url, {
            'casa_token': generate_casa_token(**kwargs),
        }, follow=True)
        html = response.content.decode()
        if authorized:
            assert 'Seuls les 600 premiers mots du texte seront affichés.' not in html
        else:
            assert 'Seuls les 600 premiers mots du texte seront affichés.' in html

    @pytest.mark.parametrize('url_name, fixture, display_biblio, display_pdf_first_page', (
        # Complete treatment articles should always display a bibliography
        ('public:journal:article_biblio', '009256ar', 1, 0),
        ('public:journal:article_summary', '009256ar', 1, 0),
        ('public:journal:article_detail', '009256ar', 1, 0),
        # Retro minimal treatment articles should only display a bibliography in article_biblio view
        ('public:journal:article_biblio', '1058447ar', 1, 0),
        ('public:journal:article_summary', '1058447ar', 0, 1),
        ('public:journal:article_detail', '1058447ar', 0, 1),
    ))
    def test_biblio_references_display(self, url_name, fixture, display_biblio,
                                       display_pdf_first_page):
        article = ArticleFactory(
            from_fixture=fixture,
            with_pdf=True,
        )
        url = reverse(url_name, kwargs={
            'journal_code': article.issue.journal.code,
            'issue_slug': article.issue.volume_slug,
            'issue_localid': article.issue.localidentifier,
            'localid': article.localidentifier,
        })
        html = Client().get(url).content.decode()
        assert html.count('<section id="grbiblio" class="article-section grbiblio" '
                          'role="complementary">') == display_biblio
        # Minimal treatment articles should not display PDF first page when displaying references.
        assert html.count('<object id="pdf-viewer"') == display_pdf_first_page

    def test_article_detail_marquage_in_toc_nav(self):
        issue = IssueFactory(
            journal__code='journal',
            localidentifier='issue',
            year='2000',
        )
        ArticleFactory(
            from_fixture='1054008ar',
            localidentifier='prev_article',
            issue=issue,
        )
        article = ArticleFactory(
            issue=issue,
        )
        ArticleFactory(
            from_fixture='1054008ar',
            localidentifier='next_article',
            issue=issue,
        )
        url = reverse('public:journal:article_detail', kwargs={
            'journal_code': article.issue.journal.code,
            'issue_slug': article.issue.volume_slug,
            'issue_localid': article.issue.localidentifier,
            'localid': article.localidentifier,
        })
        response = Client().get(url)
        html = response.content.decode()
        # Check that TOC navigation titles include converted marquage.
        assert '<a href="/fr/revues/journal/2000-issue/prev_article/" class="toc-nav__prev" ' \
               'title="Article précédent"><span class="toc-nav__arrow">&lt;--</span>' \
               '<h4 class="toc-nav__title">\n        L’action et le verbe dans ' \
               '<em>Feuillets d’Hypnos</em>\n</h4></a>' in html
        assert '<a href="/fr/revues/journal/2000-issue/next_article/" class="toc-nav__next" ' \
               'title="Article suivant"><span class="toc-nav__arrow">--&gt;</span><h4 ' \
               'class="toc-nav__title">\n        L’action et le verbe dans ' \
               '<em>Feuillets d’Hypnos</em>\n</h4></a>' in html

    def test_surtitre_not_split_in_multiple_spans(self):
        article = ArticleFactory(
            from_fixture='1056389ar',
        )
        url = reverse('public:journal:article_detail', kwargs={
            'journal_code': article.issue.journal.code,
            'issue_slug': article.issue.volume_slug,
            'issue_localid': article.issue.localidentifier,
            'localid': article.localidentifier,
        })
        response = Client().get(url)
        html = response.content.decode()
        assert '<span class="surtitre">Cahier commémoratif : ' \
               '25<sup>e</sup> anniversaire</span>' in html

    def test_title_and_paral_title_are_displayed(self):
        article = ArticleFactory(
            from_fixture='1058368ar',
        )
        url = reverse('public:journal:article_detail', kwargs={
            'journal_code': article.issue.journal.code,
            'issue_slug': article.issue.volume_slug,
            'issue_localid': article.issue.localidentifier,
            'localid': article.localidentifier,
        })
        response = Client().get(url)
        html = response.content.decode()
        assert '<span class="titre">Les Parcs Nationaux de Roumanie : considérations sur les ' \
               'habitats Natura 2000 et sur les réserves IUCN</span>' in html
        assert '<span class="titreparal">The National Parks of Romania: considerations on Natura ' \
               '2000 habitats and IUCN reserves</span>' in html

    def test_article_detail_view_with_untitled_article(self):
        article = ArticleFactory(
            from_fixture='1042058ar',
            localidentifier='article',
            issue__year='2000',
            issue__localidentifier='issue',
            issue__journal__code='journal',
            issue__journal__name='Revue',
        )
        url = reverse('public:journal:article_detail', kwargs={
            'journal_code': article.issue.journal.code,
            'issue_slug': article.issue.volume_slug,
            'issue_localid': article.issue.localidentifier,
            'localid': article.localidentifier,
        })
        html = Client().get(url).content.decode()
        # Check that "[Article sans titre]" is displayed in the header title.
        assert '<title>[Article sans titre] – Revue – Érudit</title>' in html
        # Check that "[Article sans titre]" is displayed in the body title.
        assert '<h1 class="doc-head__title"><span class="titre">[Article sans titre]</span></h1>' in html
        # Check that "[Article sans titre]" is displayed in the breadcrumbs.
        assert '<li>\n  <a href="/fr/revues/journal/2000-issue/article/">[Article sans titre]</a>' \
               '\n</li>' in html

    def test_article_authors_with_suffixes(self):
        article = ArticleFactory(
            from_fixture='1058611ar',
        )
        url = reverse('public:journal:article_detail', kwargs={
            'journal_code': article.issue.journal.code,
            'issue_slug': article.issue.volume_slug,
            'issue_localid': article.issue.localidentifier,
            'localid': article.localidentifier,
        })
        html = Client().get(url).content.decode()
        # Check that authors' suffixes are not displayed on the the author list under the article
        # title.
        assert '<li class="auteur doc-head__author">\n<span class="nompers">André\n      ' \
               'Ngamini-Ngui</span> et </li>' in html
        # Check that authors' suffixes are displayed on the 'more information' section.
        assert '<li class="auteur-affiliation"><p><strong>André\n      Ngamini-Ngui, †</strong>' \
               '</p></li>' in html

    def test_figure_groups_source_display(self):
        article = ArticleFactory(
            from_fixture='1058470ar',
            localidentifier='article',
            issue__year='2000',
            issue__localidentifier='issue',
            issue__journal__code='journal',
            issue__journal__open_access=True,
        )
        url = reverse('public:journal:article_detail', kwargs={
            'journal_code': article.issue.journal.code,
            'issue_slug': article.issue.volume_slug,
            'issue_localid': article.issue.localidentifier,
            'localid': article.localidentifier,
        })
        html = Client().get(url).content.decode()
        # Check that the source is displayed under both figures 1 & 2 which are in the same
        # figure group.
        assert '<figure class="figure" id="fi1"><figcaption></figcaption>' \
               '<div class="figure-wrapper">\n<div class="figure-object">' \
               '<a href="/fr/revues/journal/2000-issue/article/media/" ' \
               'class="lightbox objetmedia" title="">' \
               '<img src="/fr/revues/journal/2000-issue/article/media/" alt="" ' \
               'class="img-responsive"></a></div>\n<div class="figure-legende-notes-source">' \
               '<cite class="source">Avec l’aimable autorisation de l’artiste et kamel mennour, ' \
               'Paris/London. © <em>ADAGP Mohamed Bourouissa</em></cite></div>\n</div>\n' \
               '<p class="voirliste"><a href="#ligf1">-&gt; Voir la liste des figures</a></p>' \
               '</figure>' in html
        assert '<figure class="figure" id="fi2"><figcaption></figcaption><div ' \
               'class="figure-wrapper">\n<div class="figure-object">' \
               '<a href="/fr/revues/journal/2000-issue/article/media/" ' \
               'class="lightbox objetmedia" title="">' \
               '<img src="/fr/revues/journal/2000-issue/article/media/" alt="" ' \
               'class="img-responsive"></a></div>\n<div class="figure-legende-notes-source">' \
               '<cite class="source">Avec l’aimable autorisation de l’artiste et kamel mennour, ' \
               'Paris/London. © <em>ADAGP Mohamed Bourouissa</em></cite></div>\n</div>\n' \
               '<p class="voirliste"><a href="#ligf1">-&gt; Voir la liste des figures</a></p>' \
               '</figure>' in html

    def test_table_groups_display(self):
        article = ArticleFactory(
            from_fixture='1061713ar',
            localidentifier='article',
            issue__year='2000',
            issue__localidentifier='issue',
            issue__journal__code='journal',
            issue__journal__open_access=True,
        )
        url = reverse('public:journal:article_detail', kwargs={
            'journal_code': article.issue.journal.code,
            'issue_slug': article.issue.volume_slug,
            'issue_localid': article.issue.localidentifier,
            'localid': article.localidentifier,
        })
        html = Client().get(url).content.decode()
        dom = BeautifulSoup(html, 'html.parser')
        grtableau = dom.find_all('div', {'class': 'grtableau'})[0]
        figures = grtableau.find_all('figure')
        # Check that the table group is displayed.
        assert grtableau.attrs.get('id') == 'gt1'
        # Check that the tables are displayed inside the table group.
        assert figures[0].attrs.get('id') == 'ta2'
        assert figures[1].attrs.get('id') == 'ta3'
        assert figures[2].attrs.get('id') == 'ta4'
        # Check that the table images are displayed inside the tables.
        assert len(figures[0].find_all('img', {'class': 'img-responsive'})) == 1
        assert len(figures[1].find_all('img', {'class': 'img-responsive'})) == 1
        assert len(figures[2].find_all('img', {'class': 'img-responsive'})) == 1
        # Check that the table legends are displayed inside the tables.
        assert len(figures[0].find_all('p', {'class': 'alinea'})) == 1
        assert len(figures[1].find_all('p', {'class': 'alinea'})) == 2
        assert len(figures[2].find_all('p', {'class': 'alinea'})) == 4

    def test_table_groups_display_with_table_no(self):
        article = ArticleFactory(
            from_fixture='1060065ar',
            localidentifier='article',
            issue__year='2000',
            issue__localidentifier='issue',
            issue__journal__code='journal',
            issue__journal__open_access=True,
        )
        url = reverse('public:journal:article_detail', kwargs={
            'journal_code': article.issue.journal.code,
            'issue_slug': article.issue.volume_slug,
            'issue_localid': article.issue.localidentifier,
            'localid': article.localidentifier,
        })
        html = Client().get(url).content.decode()
        dom = BeautifulSoup(html, 'html.parser')
        grtableau = dom.find_all('div', {'class': 'grtableau'})[0]
        figures = grtableau.find_all('figure')
        # Check that the table group is displayed.
        assert grtableau.attrs.get('id') == 'gt1'
        # Check that the tables are displayed inside the table group.
        assert figures[0].attrs.get('id') == 'ta2'
        assert figures[1].attrs.get('id') == 'ta3'
        # Check that the table numbers are displayed.
        assert figures[0].find_all('p', {'class': 'no'})[0].text == '2A'
        assert figures[1].find_all('p', {'class': 'no'})[0].text == '2B'

    def test_figure_back_arrow_is_displayed_when_theres_no_number_or_title(self):
        article = ArticleFactory(
            from_fixture='1031003ar',
            issue__journal__open_access=True,
        )
        url = reverse('public:journal:article_detail', kwargs={
            'journal_code': article.issue.journal.code,
            'issue_slug': article.issue.volume_slug,
            'issue_localid': article.issue.localidentifier,
            'localid': article.localidentifier,
        })
        html = Client().get(url).content.decode()
        # Check that the arrow to go back to the figure is present event if there's no figure
        # number or caption.
        assert '<figure class="tableau" id="lita7"><figcaption><p class="allertexte">' \
               '<a href="#ta7">|^</a></p></figcaption>' in html

    def test_figure_groups_numbers_display_in_figure_list(self):
        article = ArticleFactory(
            from_fixture='1058470ar',
            localidentifier='article',
            issue__year='2000',
            issue__localidentifier='issue',
            issue__journal__code='journal',
            issue__journal__open_access=True,
        )
        url = reverse('public:journal:article_detail', kwargs={
            'journal_code': article.issue.journal.code,
            'issue_slug': article.issue.volume_slug,
            'issue_localid': article.issue.localidentifier,
            'localid': article.localidentifier,
        })
        html = Client().get(url).content.decode()
        # Check that the figure numbers are displayed in the figure list for figure groups.
        assert '<div class="grfigure" id="ligf1">\n<div class="grfigure-caption">\n' \
               '<p class="allertexte"><a href="#gf1">|^</a></p>\n' \
               '<p class="no">Figures 1 - 2</p>' in html

    def test_figcaption_display_for_figure_groups_and_figures(self):
        article = ArticleFactory(
            from_fixture='1060169ar',
            issue__journal__open_access=True,
        )
        url = reverse('public:journal:article_detail', kwargs={
            'journal_code': article.issue.journal.code,
            'issue_slug': article.issue.volume_slug,
            'issue_localid': article.issue.localidentifier,
            'localid': article.localidentifier,
        })
        html = Client().get(url).content.decode()
        # Check that figure group caption and the figure captions are displayed.
        assert '<div class="grfigure-caption">\n<p class="allertexte"><a href="#gf1">|^</a></p>\n' \
               '<p class="no">Figure 1</p>\n<div class="legende"><p class="legende">' \
               '<strong class="titre">RMF frequencies in German data</strong>' \
               '</p></div>\n</div>' in html
        assert '<figcaption><p class="legende"><strong class="titre">German non-mediated</strong>' \
               '</p></figcaption>' in html
        assert '<figcaption><p class="legende"><strong class="titre">German interpreted' \
               '</strong></p></figcaption>' in html

    def test_article_multilingual_titles(self):
        article = ArticleFactory(
            from_fixture='1059303ar',
        )
        url = reverse('public:journal:article_detail', kwargs={
            'journal_code': article.issue.journal.code,
            'issue_slug': article.issue.volume_slug,
            'issue_localid': article.issue.localidentifier,
            'localid': article.localidentifier,
        })
        html = Client().get(url).content.decode()
        # Check that paral titles are displayed in the article header.
        assert '<span class="titreparal">Détection d’ADN d’<em>Ophiostoma ulmi</em> ' \
               'introgressé naturellement        dans les régions entourant les loci contrôlant ' \
               'la pathogénie et le type sexuel chez        <em>O. novo-ulmi</em></span>' in html
        # Check that paral titles are not displayed in summary section.
        assert '<h4><span class="title">Détection d’ADN d’<em>Ophiostoma ulmi</em> introgressé ' \
               'naturellement dans les régions entourant les loci contrôlant la pathogénie et le ' \
               'type sexuel chez <em>O. novo-ulmi</em></span></h4>' not in html

    def test_authors_more_information_for_author_with_suffix_and_no_affiliation(self):
        article = ArticleFactory(
            from_fixture='1059571ar',
        )
        url = reverse('public:journal:article_detail', kwargs={
            'journal_code': article.issue.journal.code,
            'issue_slug': article.issue.volume_slug,
            'issue_localid': article.issue.localidentifier,
            'localid': article.localidentifier,
        })
        html = Client().get(url).content.decode()
        # Check that more information akkordion is displayed for author with suffix and
        # no affiliation.
        assert '<ul class="akkordion-content unstyled"><li class="auteur-affiliation"><p>' \
               '<strong>Guy\n      Sylvestre, o.c.</strong></p></li></ul>' in html

    def test_journal_multilingual_titles_in_citations(self):
        issue = IssueFactory()
        repository.api.set_publication_xml(
            issue.get_full_identifier(),
            open('tests/fixtures/issue/ri04376.xml', 'rb').read(),
        )
        article = ArticleFactory(
            localidentifier='article',
            issue=issue,
        )
        url = reverse('public:journal:article_detail', kwargs={
            'journal_code': article.issue.journal.code,
            'issue_slug': article.issue.volume_slug,
            'issue_localid': article.issue.localidentifier,
            'localid': article.localidentifier,
        })
        html = Client().get(url).content.decode()
        # Check that the journal name is displayed in French and English (Relations industrielles
        # / Industrial Relations).
        assert '<dd id="id_cite_mla_article" class="cite-mla">\n        Pratt, Lynda. ' \
               '«&nbsp;Robert Southey, Writing and Romanticism.&nbsp;» <em>Relations ' \
               'industrielles / Industrial Relations</em>, volume 73, numéro 4, automne 2018. ' \
               'https://doi.org/10.7202/009255ar\n      </dd>' in html
        assert '<dd id="id_cite_apa_article" class="cite-apa">\n        ' \
               'Pratt, L. (2019). Robert Southey, Writing and Romanticism. ' \
               '<em>Relations industrielles / Industrial Relations</em>. ' \
               'https://doi.org/10.7202/009255ar\n      </dd>' in html
        assert '<dd id="id_cite_chicago_article" class="cite-chicago">\n        ' \
               'Pratt, Lynda «&nbsp;Robert Southey, Writing and Romanticism&nbsp;». ' \
               '<em>Relations industrielles / Industrial Relations</em> (2019). ' \
               'https://doi.org/10.7202/009255ar\n      </dd>' in html

    @pytest.mark.parametrize('fixture, url_name, expected_result', (
        # Multilingual journals should have all titles in citations.
        ('ri04376', 'public:journal:article_citation_enw',
         '%J Relations industrielles / Industrial Relations'),
        ('ri04376', 'public:journal:article_citation_ris',
         'JO  - Relations industrielles / Industrial Relations'),
        ('ri04376', 'public:journal:article_citation_bib',
         'journal="Relations industrielles / Industrial Relations",'),
        # Sub-titles should not be in citations.
        ('im03868', 'public:journal:article_citation_enw', '%J Intermédialités / Intermediality'),
        ('im03868', 'public:journal:article_citation_ris',
         'JO  - Intermédialités / Intermediality'),
        ('im03868', 'public:journal:article_citation_bib',
         'journal="Intermédialités / Intermediality'),
    ))
    def test_journal_multilingual_titles_in_article_citation_views(self, fixture, url_name,
                                                                   expected_result):
        issue = IssueFactory()
        repository.api.set_publication_xml(
            issue.get_full_identifier(),
            open('tests/fixtures/issue/{}.xml'.format(fixture), 'rb').read(),
        )
        article = ArticleFactory(
            issue=issue,
        )
        url = reverse(url_name, kwargs={
            'journal_code': article.issue.journal.code,
            'issue_slug': article.issue.volume_slug,
            'issue_localid': article.issue.localidentifier,
            'localid': article.localidentifier,
        })
        citation = Client().get(url).content.decode()
        # Check that the journal name is displayed in French and English (Relations industrielles /
        # Industrial Relations).
        assert expected_result in citation

    def test_doi_with_extra_space(self):
        article = ArticleFactory(
            from_fixture='1009368ar',
        )
        url = reverse('public:journal:article_detail', kwargs={
            'journal_code': article.issue.journal.code,
            'issue_slug': article.issue.volume_slug,
            'issue_localid': article.issue.localidentifier,
            'localid': article.localidentifier,
        })
        html = Client().get(url).content.decode()
        # Check that extra space around DOIs is stripped.
        assert '<meta name="citation_doi" content="https://doi.org/10.7202/1009368ar" />' in html
        assert '<a href="https://doi.org/10.7202/1009368ar" class="clipboard-data">' in html

    def test_unicode_combining_characters(self):
        article = ArticleFactory(
            from_fixture='1059577ar',
        )
        url = reverse('public:journal:article_detail', kwargs={
            'journal_code': article.issue.journal.code,
            'issue_slug': article.issue.volume_slug,
            'issue_localid': article.issue.localidentifier,
            'localid': article.localidentifier,
        })
        html = Client().get(url).content.decode()
        # Pre-combined character is present (ă = ă)
        assert '<em>Studii de lingvistică</em>' in html
        # Combining character is not present (ă = a + ˘)
        assert '<em>Studii de lingvistică</em>' not in html

    def test_acknowledgements_and_footnotes_sections_order(self):
        article = ArticleFactory(
            from_fixture='1060048ar',
            issue__journal__open_access=True,
        )
        url = reverse('public:journal:article_detail', kwargs={
            'journal_code': article.issue.journal.code,
            'issue_slug': article.issue.volume_slug,
            'issue_localid': article.issue.localidentifier,
            'localid': article.localidentifier,
        })
        html = Client().get(url).content.decode()
        dom = BeautifulSoup(html, 'html.parser')
        partiesann = dom.find_all('section', {'class': 'partiesann'})[0]
        sections = partiesann.find_all('section')
        # Check that acknowledgements are displayed before footnotes.
        assert sections[0].attrs['id'] == 'merci'
        assert sections[1].attrs['id'] == 'grnote'

    def test_abstracts_and_keywords(self):
        article = ArticleFactory()
        with repository.api.open_article(article.pid) as wrapper:
            wrapper.set_abstracts([{'lang': 'fr', 'content': 'Résumé français'}])
            wrapper.set_abstracts([{'lang': 'en', 'content': 'English abstract'}])
            wrapper.add_keywords('es', ['Palabra clave en español'])
            wrapper.add_keywords('fr', ['Mot-clé français'])
        url = reverse('public:journal:article_detail', kwargs={
            'journal_code': article.issue.journal.code,
            'issue_slug': article.issue.volume_slug,
            'issue_localid': article.issue.localidentifier,
            'localid': article.localidentifier,
        })
        html = Client().get(url).content.decode()
        dom = BeautifulSoup(html, 'html.parser')
        grresume = dom.find_all('section', {'class': 'grresume'})[0]
        resumes = grresume.find_all('section', {'class': 'resume'})
        keywords = grresume.find_all('div', {'class': 'keywords'})
        # Make sure the main abstract (English) appears first, even though it's in second position
        # in the XML.
        assert resumes[0].decode() == '<section class="resume" id="resume-en"><h3>Abstract</h3>\n' \
                                      '<p class="alinea"><em>English abstract</em></p></section>'
        # Make sure the French keywords appear in the French abstract section.
        assert resumes[1].decode() == '<section class="resume" id="resume-fr"><h3>Résumé</h3>\n' \
                                      '<p class="alinea"><em>Résumé français</em></p>\n' \
                                      '<div class="keywords">\n<p><strong>Mots-clés :</strong>' \
                                      '</p>\n<ul><li class="keyword">Mot-clé français</li></ul>' \
                                      '\n</div></section>'
        # Make sure the French keywords appear first since there is no English keywords and no
        # Spanish abstract.
        assert keywords[0].decode() == '<div class="keywords">\n<p><strong>Mots-clés :</strong>' \
                                       '</p>\n<ul><li class="keyword">Mot-clé français</li>' \
                                       '</ul>\n</div>'
        # Make sure the Spanish keywords are displayed even though there is no Spanish abstract.
        assert keywords[1].decode() == '<div class="keywords">\n<p><strong>Palabras clave:' \
                                       '</strong></p>\n<ul><li class="keyword">Palabra clave en ' \
                                       'español</li></ul>\n</div>'

    @pytest.mark.parametrize('article_type, expected_string', (
        ('compterendu', 'Un compte rendu de la revue'),
        ('article', 'Un article de la revue'),
    ))
    def test_review_article_explanatory_note(self, article_type, expected_string):
        article = ArticleFactory(type=article_type)
        url = reverse('public:journal:article_detail', kwargs={
            'journal_code': article.issue.journal.code,
            'issue_slug': article.issue.volume_slug,
            'issue_localid': article.issue.localidentifier,
            'localid': article.localidentifier,
        })
        html = Client().get(url).content.decode()
        dom = BeautifulSoup(html, 'html.parser')
        div = dom.find_all('div', {'class': 'doc-head__metadata'})[1]
        note = 'Ce document est le compte-rendu d\'une autre oeuvre tel qu\'un livre ou un ' \
               'film. L\'oeuvre originale discutée ici n\'est pas disponible sur cette plateforme.'
        assert expected_string in div.decode()
        if article_type == 'compterendu':
            assert note in div.decode()
        else:
            assert note not in div.decode()

    def test_verbatim_poeme_lines(self):
        article = ArticleFactory(
            from_fixture='1062061ar',
            issue__journal__open_access=True,
        )
        url = reverse('public:journal:article_detail', kwargs={
            'journal_code': article.issue.journal.code,
            'issue_slug': article.issue.volume_slug,
            'issue_localid': article.issue.localidentifier,
            'localid': article.localidentifier,
        })
        html = Client().get(url).content.decode()
        dom = BeautifulSoup(html, 'html.parser')
        poeme = dom.find('blockquote', {'class': 'verbatim poeme'})
        # Check that poems lines are displayed in <p>.
        assert poeme.decode() == '<blockquote class="verbatim poeme">\n<p class="ligne">Jour de ' \
                                 'larme, </p>\n<p class="ligne">jour où les coupables se ' \
                                 'réveilleront</p>\n<p class="ligne">pour entendre leur jugement,' \
                                 '</p>\n<p class="ligne">alors, ô Dieu, pardonne-leur et leur ' \
                                 'donne le repos.</p>\n<p class="ligne">Jésus, accorde-leur le ' \
                                 'repos.</p>\n</blockquote>'

    def test_grfigure_caption_position(self):
        article = ArticleFactory(
            from_fixture='1062105ar',
            issue__journal__open_access=True,
        )
        url = reverse('public:journal:article_detail', kwargs={
            'journal_code': article.issue.journal.code,
            'issue_slug': article.issue.volume_slug,
            'issue_localid': article.issue.localidentifier,
            'localid': article.localidentifier,
        })
        html = Client().get(url).content.decode()
        dom = BeautifulSoup(html, 'html.parser')
        grfigure = dom.find('div', {'id': 'gf1'})
        grfigure_caption = grfigure.find_all('div', {'class': 'grfigure-caption'})[0]
        grfigure_legende = grfigure.find_all('div', {'class': 'grfigure-legende'})[0]
        assert grfigure_caption.decode() == '<div class="grfigure-caption">\n<p class="no">' \
                                            'Figure 1</p>\n<div class="legende"></div>\n</div>'
        assert grfigure_legende.decode() == '<div class="grfigure-legende">\n<p class="alinea">' \
                                            '<sup>a</sup> Hommes et femmes des générations ' \
                                            'enquêtées       (1930-1950 résidant en ' \
                                            'Île-de-France en 1999) et leurs parents.</p>\n' \
                                            '<p class="alinea"><sup>b</sup> L’interprétation de ' \
                                            'cette figure se fait par       exemple de la ' \
                                            'manière suivante : Parmi les Ego hommes de ' \
                                            'profession       « indépendants », 44 % ont déclaré ' \
                                            'que la profession principale de leur père       ' \
                                            'était indépendant, 22,5 % ouvrier, 11,9 % cadre, ' \
                                            'etc. L’origine « père       indépendant » est ' \
                                            'nettement surreprésentée chez les Ego hommes ' \
                                            'indépendants.       C’est aussi l’origine la plus ' \
                                            'fréquente pour les Ego femmes indépendantes       ' \
                                            '(31,5 %), suivie par un père cadre (28,7 %).</p>\n' \
                                            '</div>'


class TestArticleRawPdfView:
    @unittest.mock.patch.object(JournalDigitalObject, 'logo')
    @unittest.mock.patch.object(ArticleDigitalObject, 'pdf')
    @unittest.mock.patch.object(subprocess, 'check_call')
    def test_can_retrieve_the_pdf_of_existing_articles(self, mock_check_call, mock_pdf, mock_logo):
        with open(os.path.join(FIXTURE_ROOT, 'dummy.pdf'), 'rb') as f:
            mock_pdf.content = io.BytesIO()
            mock_pdf.content.write(f.read())
        with open(os.path.join(FIXTURE_ROOT, 'logo.jpg'), 'rb') as f:
            mock_logo.content = io.BytesIO()
            mock_logo.content.write(f.read())
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
        request = RequestFactory().get(url)
        request.user = AnonymousUser()
        request.subscriptions = UserSubscriptions()

        response = ArticleRawPdfView.as_view()(
            request, journal_code=journal_id, issue_slug=issue.volume_slug, issue_localid=issue_id,
            localid=article_id)

        assert response.status_code == 200
        assert response['Content-Type'] == 'application/pdf'

    def test_cannot_retrieve_the_pdf_of_inexistant_articles(self):
        # Note: as there is no Erudit fedora repository used during the
        # test, any tentative of retrieving the PDF of an article should
        # fail.

        journal_id = 'dummy139'
        issue_slug = 'test'
        issue_id = 'dummy1515298'
        article_id = '1001942du'
        url = reverse('public:journal:article_raw_pdf', args=(
            journal_id, issue_slug, issue_id, article_id
        ))
        response = Client().get(url)
        assert response.status_code == 302

    class TestArticleRawPdfView:
        @unittest.mock.patch.object(ArticleDigitalObject, 'pdf')
        @unittest.mock.patch.object(subprocess, 'check_call')
        def test_can_retrieve_the_firstpage_pdf_of_existing_articles(self, mock_check_call, mock_pdf):
            with open(os.path.join(FIXTURE_ROOT, 'dummy.pdf'), 'rb') as f:
                mock_pdf.content = io.BytesIO()
                mock_pdf.content.write(f.read())
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
            request = RequestFactory().get(url)
            request.user = AnonymousUser()
            request.subscriptions = UserSubscriptions()

            response = ArticleRawPdfFirstPageView.as_view()(
                request, journal_code=journal_id, issue_slug=issue.volume_slug, issue_localid=issue_id,
                localid=article_id)

            assert response.status_code == 200
            assert response['Content-Type'] == 'application/pdf'


    def test_cannot_be_accessed_if_the_article_is_not_in_open_access(self):
        journal = JournalFactory(open_access=False)
        issue = IssueFactory.create(
            journal=journal, year=dt.datetime.now().year, date_published=dt.datetime.now())
        article = ArticleFactory.create(issue=issue)
        journal_id = journal.localidentifier
        issue_id = issue.localidentifier
        article_id = article.localidentifier
        url = article_raw_pdf_url(article)

        request = RequestFactory().get(url)
        request.user = AnonymousUser()
        request.subscriptions = UserSubscriptions()

        response = ArticleRawPdfView.as_view()(
            request, journal_code=journal_id, issue_slug=issue.volume_slug,
            issue_localid=issue_id, localid=article_id)

        assert isinstance(response, HttpResponseRedirect)
        assert response.url == reverse('public:journal:article_detail', args=(
            journal_id, issue.volume_slug, issue_id, article_id
        ))

    def test_cannot_be_accessed_if_the_publication_of_the_article_is_not_allowed_by_its_authors(self):  # noqa
        journal = JournalFactory(open_access=False)
        issue = IssueFactory.create(
            journal=journal, year=2010, date_published=dt.datetime.now())
        article = ArticleFactory.create(issue=issue, publication_allowed=False)
        journal_id = journal.localidentifier
        issue_id = issue.localidentifier
        article_id = article.localidentifier
        url = article_raw_pdf_url(article)
        request = RequestFactory().get(url)
        request.user = AnonymousUser()

        response = ArticleRawPdfView.as_view()(
            request, journal_code=journal_id, issue_slug=issue.volume_slug,
            issue_localid=issue_id, localid=article_id)

        assert isinstance(response, HttpResponseRedirect)
        assert response.url == reverse('public:journal:article_detail', args=(
            journal_id, issue.volume_slug, issue_id, article_id
        ))


class TestLegacyUrlsRedirection:

    def test_can_redirect_issue_support_only_volume_and_year(self):
        journal = JournalFactory(code='test')
        issue = IssueFactory(journal=journal, volume="1", number="1", year="2017")
        IssueFactory(journal=issue.journal, volume="1", number="2", year="2017")
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

        resp = Client().get(url)

        assert resp.url == reverse('public:journal:issue_detail', kwargs=dict(
            journal_code=article2.issue.journal.code,
            issue_slug=article2.issue.volume_slug,
            localidentifier=article2.issue.localidentifier,
        ))

    def test_can_redirect_issue_detail_with_empty_volume(self):
        issue = IssueFactory(number="1", volume="1", year="2017")
        issue2 = IssueFactory(journal=issue.journal, volume="2", number="1", year="2017")
        url = "/revue/{journal_code}/{year}/v/n{number}/".format(
            journal_code=issue.journal.code,
            number=issue.number,
            year=issue.year,
        )

        resp = Client().get(url)

        assert resp.url == reverse('public:journal:issue_detail', kwargs=dict(
            journal_code=issue2.journal.code,
            issue_slug=issue2.volume_slug,
            localidentifier=issue2.localidentifier,
        ))

    def test_can_redirect_article_from_legacy_urls(self):
        from django.utils.translation import deactivate_all

        article = ArticleFactory()
        article.issue.volume = "1"
        article.issue.save()

        url = '/revue/{journal_code}/{issue_year}/v{issue_volume}/n/{article_localidentifier}.html'.format(  # noqa
            journal_code=article.issue.journal.code,
            issue_year=article.issue.year,
            issue_volume=article.issue.volume,
            article_localidentifier=article.localidentifier
        )

        resp = Client().get(url)
        assert resp.status_code == 301

        url = '/revue/{journal_code}/{issue_year}/v/n/{article_localidentifier}.html'.format(  # noqa
            journal_code=article.issue.journal.code,
            issue_year=article.issue.year,
            article_localidentifier=article.localidentifier
        )

        resp = Client().get(url)
        assert resp.status_code == 301

        url = '/revue/{journal_code}/{issue_year}/v/n{issue_number}/{article_localidentifier}.html'.format(  # noqa
            journal_code=article.issue.journal.code,
            issue_year=article.issue.year,
            issue_number=article.issue.number,
            article_localidentifier=article.localidentifier
        )

        resp = Client().get(url)

        assert resp.url == reverse('public:journal:article_detail', kwargs=dict(
            journal_code=article.issue.journal.code,
            issue_slug=article.issue.volume_slug,
            issue_localid=article.issue.localidentifier,
            localid=article.localidentifier
        ))
        assert "/fr/" in resp.url
        assert resp.status_code == 301

        deactivate_all()
        resp = Client().get(url + "?lang=en")

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
        resp = Client().get(url)

        assert resp.url == reverse('public:journal:article_detail', kwargs=dict(
            journal_code=article.issue.journal.code,
            issue_slug=article.issue.volume_slug,
            issue_localid=article.issue.localidentifier,
            localid=article.localidentifier
        ))

        assert "/en/" in resp.url
        assert resp.status_code == 301

    @pytest.mark.parametrize("pattern", (
        "/revue/{journal_code}/{year}/v{volume}/n{number}/",
        "/culture/{journal_localidentifier}/{issue_localidentifier}/index.html"
    ))
    def test_can_redirect_issues_from_legacy_urls(self, pattern):
        article = ArticleFactory()
        article.issue.volume = "1"
        article.issue.number = "1"
        article.issue.save()
        url = pattern.format(
            journal_code=article.issue.journal.code,
            year=article.issue.year,
            volume=article.issue.volume,
            number=article.issue.number,
            journal_localidentifier=article.issue.journal.localidentifier,
            issue_localidentifier=article.issue.localidentifier,
            article_localidentifier = article.localidentifier,

        )
        resp = Client().get(url)

        assert resp.url == reverse('public:journal:issue_detail', kwargs=dict(
            journal_code=article.issue.journal.code,
            issue_slug=article.issue.volume_slug,
            localidentifier=article.issue.localidentifier
        ))
        assert resp.status_code == 301

    def test_can_redirect_journals_from_legacy_urls(self):
        article = ArticleFactory()
        article.issue.volume = "1"
        article.issue.number = "1"
        article.issue.save()
        url = "/revue/{code}/".format(
            code=article.issue.journal.code,
        )
        resp = Client().get(url)

        assert resp.url == journal_detail_url(article.issue.journal)
        assert resp.status_code == 301


class TestArticleFallbackRedirection:

    FALLBACK_URL = settings.FALLBACK_BASE_URL

    @pytest.fixture(params=itertools.product(
        [{'code': 'nonexistent'}],
        [
            'legacy_journal:legacy_journal_detail',
            'legacy_journal:legacy_journal_detail_index',
            'legacy_journal:legacy_journal_authors',
            'legacy_journal:legacy_journal_detail_culture',
            'legacy_journal:legacy_journal_detail_culture_index',
            'legacy_journal:legacy_journal_authors_culture'
        ]
    ))
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
        itertools.product(
            [{
                'journal_code': 'nonexistent',
                'year': "1974",
                'v': "7",
                'n': "",
            }],
            [
                "legacy_journal:legacy_issue_detail",
                "legacy_journal:legacy_issue_detail_index"
            ],
        ),
        itertools.product(
            [{
                'journal_code': 'nonexistent',
                'year': "1974",
                'v': "7",
                'n': "",
            }],
            [
                "legacy_journal:legacy_issue_detail",
                "legacy_journal:legacy_issue_detail_index"
            ],
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
        itertools.product(
            [{
                'journal_code': 'nonexistent', 'year': 2004, 'v': 1, 'issue_number': 'nonexistent',
                'localid': 'nonexistent', 'format_identifier': 'html', 'lang': 'fr'
            }],
            [
                "legacy_journal:legacy_article_detail",
                "legacy_journal:legacy_article_detail_culture"
            ],
        ),
        [
            ({'localid': 'nonexistent'}, 'legacy_journal:legacy_article_id'),
            ({'journal_code': 'nonexistent',
              'issue_localid': 'nonexistent', 'localid': 'nonexistent',
              'format_identifier': 'html'},
             'legacy_journal:legacy_article_detail_culture_localidentifier')
        ]),
    )
    def article_url(self, request):
        kwargs = request.param[0]
        url = request.param[1]
        return reverse(url, kwargs=kwargs)

    def test_legacy_url_for_nonexistent_journals_redirects_to_fallback_website(self, journal_url):
        response = Client().get(journal_url)
        redirect_url = response.url
        assert self.FALLBACK_URL in redirect_url

    def test_legacy_url_for_nonexistent_issues_redirect_to_fallback_website(self, issue_url):
        response = Client().get(issue_url)
        redirect_url = response.url
        assert self.FALLBACK_URL in redirect_url

    def test_legacy_url_for_nonexistent_article_redirect_to_fallback_website(self, article_url):
        response = Client().get(article_url)
        redirect_url = response.url
        assert self.FALLBACK_URL in redirect_url


class TestArticleXmlView:
    def test_can_retrieve_xml_of_existing_articles(self):
        journal = JournalFactory(open_access=True)
        issue = IssueFactory.create(
            journal=journal, year=2010, is_published=True,
            date_published=dt.datetime.now() - dt.timedelta(days=1000))
        article = ArticleFactory.create(issue=issue)

        journal_id = issue.journal.localidentifier
        issue_id = issue.localidentifier
        article_id = article.localidentifier
        url = reverse('public:journal:article_raw_xml', args=(
            journal_id, issue.volume_slug, issue_id, article_id
        ))
        response = Client().get(url)

        assert response.status_code == 200
        assert response['Content-Type'] == 'application/xml'


class TestArticleMediaView(TestCase):
    @unittest.mock.patch.object(MediaDigitalObject, 'content')
    def test_can_retrieve_the_pdf_of_existing_articles(self, mock_content):
        # Setup
        with open(os.path.join(FIXTURE_ROOT, 'pixel.png'), 'rb') as f:
            mock_content.content = io.BytesIO()
            mock_content.content.write(f.read())
        mock_content.mimetype = 'image/png'

        issue = IssueFactory.create(date_published=dt.datetime.now())
        article = ArticleFactory.create(issue=issue)
        issue_id = issue.localidentifier
        article_id = article.localidentifier
        request = RequestFactory().get('/')

        # Run
        response = ArticleMediaView.as_view()(
            request, journal_code=issue.journal.code, issue_localid=issue_id,
            localid=article_id, media_localid='test')

        # Check
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'image/png')


class TestExternalURLRedirectViews:
    def test_can_redirect_to_issue_external_url(self):
        issue = IssueFactory.create(
            date_published=dt.datetime.now(),
            external_url="http://www.erudit.org"
        )

        response = Client().get(
            reverse(
                'public:journal:issue_external_redirect',
                kwargs={'localidentifier': issue.localidentifier}
            )
        )
        assert response.status_code == 302

    def test_can_redirect_to_journal_external_url(self):
        journal = JournalFactory(code='journal1', external_url='http://www.erudit.org')
        response = Client().get(
            reverse(
                'public:journal:journal_external_redirect',
                kwargs={'code': journal.code}
            )
        )
        assert response.status_code == 302


@pytest.mark.parametrize('export_type', ['bib', 'enw', 'ris'])
def test_article_citation_doesnt_html_escape(export_type):
    # citations exports don't HTML-escape values (they're not HTML documents).
    # TODO: test authors name. Templates directly refer to `erudit_object` and we we don't have
    # a proper mechanism in the upcoming fake fedora API to fake values on the fly yet.
    title = "rock & rollin'"
    article = ArticleFactory.create(title=title)
    issue = article.issue
    url = reverse('public:journal:article_citation_{}'.format(export_type), kwargs={
        'journal_code': issue.journal.code, 'issue_slug': issue.volume_slug,
        'issue_localid': issue.localidentifier, 'localid': article.localidentifier})
    response = Client().get(url)
    content = response.content.decode()
    assert title in content

