# -*- coding: utf-8 -*-

import datetime as dt
import io
import os
import unittest.mock

from django.contrib.auth.models import AnonymousUser
from django.core.exceptions import PermissionDenied
from django.core.urlresolvers import reverse
from django.http.response import HttpResponseRedirect
from django.test import Client
from django.test import RequestFactory
from django.test.utils import override_settings
from PyPDF2 import PdfFileReader
import pytest

from erudit.models import JournalType
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
from core.subscription.test.factories import JournalAccessSubscriptionPeriodFactory

from apps.public.journal.views import ArticleDetailView
from apps.public.journal.views import ArticleMediaView
from apps.public.journal.views import ArticleRawPdfFirstPageView
from apps.public.journal.views import ArticleRawPdfView
from apps.public.journal.views import ArticleXmlView

FIXTURE_ROOT = os.path.join(os.path.dirname(__file__), 'fixtures')


@pytest.mark.django_db
class TestJournalListView(object):
    @pytest.fixture(autouse=True)
    def setup(self):
        self.client = Client()
        self.user = UserFactory.create(username='foobar')
        self.user.set_password('notsecret')
        self.user.save()

    def test_can_sort_journals_by_name(self):
        # Setup
        collection = CollectionFactory.create()
        journal_1 = JournalFactory.create(collection=collection, name='ABC journal')
        journal_2 = JournalFactory.create(collection=collection, name='ACD journal')
        journal_3 = JournalFactory.create(collection=collection, name='DEF journal')
        journal_4 = JournalFactory.create(collection=collection, name='GHI journal')
        journal_5 = JournalFactory.create(collection=collection, name='GIJ journal')
        journal_6 = JournalFactory.create(collection=collection, name='GJK journal')
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
        journal_1 = JournalFactory.create(collection=collection)
        journal_1.disciplines.add(discipline_1)
        journal_2 = JournalFactory.create(collection=collection)
        journal_2.disciplines.add(discipline_1)
        journal_3 = JournalFactory.create(collection=collection)
        journal_3.disciplines.add(discipline_2)
        journal_4 = JournalFactory.create(collection=collection)
        journal_4.disciplines.add(discipline_3)
        journal_5 = JournalFactory.create(collection=collection)
        journal_5.disciplines.add(discipline_3)
        journal_6 = JournalFactory.create(collection=collection)
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
        journal1 = JournalFactory.create(collection=collection)
        journal2 = JournalFactory.create(collection=main_collection)
        url = reverse('public:journal:journal_list')
        response = self.client.get(url)

        assert list(response.context['journals']) == [journal2]

    def test_can_filter_the_journals_by_open_access(self):
        # Setup
        collection = CollectionFactory.create()
        journal_1 = JournalFactory.create(collection=collection, open_access=True)
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
        journal_2 = JournalFactory.create(collection=collection, type=jtype_2)
        url = reverse('public:journal:journal_list')
        # Run
        response = self.client.get(url, data={'types': ['T2', ]})
        # Check
        assert list(response.context['journals']) == [journal_2, ]

    def test_can_filter_the_journals_by_collections(self):
        # Setup
        col_1 = CollectionFactory(code='col1')
        col_2 = CollectionFactory(code='col2')
        JournalFactory.create(collection=col_1)
        journal_2 = JournalFactory.create(collection=col_2)
        url = reverse('public:journal:journal_list')
        # Run
        response = self.client.get(url, data={'collections': ['col2', ]})
        # Check
        assert list(response.context['journals']) == [journal_2, ]


@override_settings(DEBUG=True)
class TestJournalDetailView(BaseEruditTestCase):
    def test_can_embed_the_journal_information_in_the_context_if_available(self):
        # Setup
        collection = CollectionFactory.create()
        journal_1 = JournalFactory.create(collection=collection)
        journal_2 = JournalFactory.create(collection=collection)
        journal_info = JournalInformationFactory.create(journal=journal_1)
        url_1 = reverse('public:journal:journal_detail', kwargs={'code': journal_1.code})
        url_2 = reverse('public:journal:journal_detail', kwargs={'code': journal_2.code})
        # Run
        response_1 = self.client.get(url_1)
        response_2 = self.client.get(url_2)
        # Check
        self.assertEqual(response_1.status_code, 200)
        self.assertEqual(response_2.status_code, 200)
        self.assertEqual(response_1.context['journal_info'], journal_info)
        self.assertTrue('journal_info' not in response_2.context)

    @unittest.mock.patch("erudit.models.journal.Issue.has_coverpage", return_value=True)
    @unittest.mock.patch("erudit.models.journal.Issue.fedora_object")
    def test_can_display_when_issues_have_a_space_in_their_number(self, mock_cache, mock_issue):
        issue = IssueFactory(number='2 bis')
        url_1 = reverse('public:journal:journal_detail', kwargs={'code': issue.journal.code})
        # Run
        response_1 = self.client.get(url_1)
        self.assertEqual(response_1.status_code, 200)

    def test_can_embed_the_publicated_issues_in_the_context(self):
        # Setup
        collection = CollectionFactory.create(localidentifier='erudit')
        journal = JournalFactory.create(collection=collection)
        JournalInformationFactory.create(journal=journal)
        issue_1 = IssueFactory.create(
            journal=journal, year=2010, date_published=dt.datetime.now() - dt.timedelta(days=1))
        issue_2 = IssueFactory.create(journal=journal, year=2010, date_published=dt.datetime.now())
        IssueFactory.create(
            journal=journal, year=dt.datetime.now().year + 1,
            is_published=False,
            date_published=dt.datetime.now() + dt.timedelta(days=30))
        url = reverse('public:journal:journal_detail', kwargs={'code': journal.code})
        # Run
        response = self.client.get(url)
        # Check
        self.assertEqual(response.status_code, 200)
        self.assertEqual(list(response.context['issues']), [issue_2, issue_1])

    def test_can_embed_the_latest_issue_in_the_context(self):
        # Setup
        collection = CollectionFactory.create(localidentifier='erudit')
        journal = JournalFactory.create(collection=collection)
        JournalInformationFactory.create(journal=journal)
        IssueFactory.create(
            journal=journal, year=2010, date_published=dt.datetime.now() - dt.timedelta(days=1))
        issue_2 = IssueFactory.create(journal=journal, year=2010, date_published=dt.datetime.now())
        issue_3 = IssueFactory.create(
            is_published=False,
            journal=journal, year=dt.datetime.now().year + 1,
            date_published=dt.datetime.now() + dt.timedelta(days=30))
        url = reverse('public:journal:journal_detail', kwargs={'code': journal.code})
        # Run
        response = self.client.get(url)
        # Check
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['latest_issue'], issue_2)

    def test_embeds_a_boolean_indicating_if_the_user_is_subscribed_to_the_current_journal(self):
        # Setup
        now_dt = dt.datetime.now()
        subscription = JournalAccessSubscriptionFactory.create(user=self.user, journal=self.journal)
        JournalAccessSubscriptionPeriodFactory.create(
            subscription=subscription,
            start=now_dt - dt.timedelta(days=10),
            end=now_dt + dt.timedelta(days=8))
        self.client.login(username='david', password='top_secret')
        url = reverse('public:journal:journal_detail', kwargs={'code': self.journal.code})
        # Run
        response = self.client.get(url)
        # Check
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context['user_has_access_to_journal'])


@override_settings(DEBUG=True)
class TestJournalAuthorsListView(BaseEruditTestCase):

    def test_supports_authors_with_only_special_characters_in_their_name(self):
        # Setup
        issue_1 = IssueFactory.create(journal=self.journal, date_published=dt.datetime.now())
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
        issue_1 = IssueFactory.create(journal=self.journal, date_published=dt.datetime.now())
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
    def test_works_with_pks(self):
        # Setup
        issue = IssueFactory.create(journal=self.journal, date_published=dt.datetime.now())
        url = reverse('public:journal:issue_detail', args=[
            self.journal.code, issue.volume_slug, issue.localidentifier])
        # Run
        response = self.client.get(url)
        # Check
        self.assertEqual(response.status_code, 200)

    def test_works_with_localidentifiers(self):
        # Setup
        issue = IssueFactory.create(
            journal=self.journal, date_published=dt.datetime.now(), localidentifier='test')
        url = reverse('public:journal:issue_detail', args=[
            self.journal.code, issue.volume_slug, issue.localidentifier])
        # Run
        response = self.client.get(url)
        # Check
        self.assertEqual(response.status_code, 200)


@override_settings(DEBUG=True)
class TestArticleDetailView(BaseEruditTestCase):
    def setUp(self):
        super(TestArticleDetailView, self).setUp()
        self.factory = RequestFactory()

    @unittest.mock.patch.object(FedoraMixin, 'get_erudit_object')
    def test_works_with_localidentifiers(self, mock_fedora_mixin):
        # Setup
        self.journal.open_access = True
        self.journal.save()
        issue = IssueFactory.create(
            journal=self.journal, date_published=dt.datetime.now(), localidentifier='test')
        article = ArticleFactory.create(issue=issue)
        url = reverse('public:journal:article_detail', kwargs={
            'journal_code': self.journal.code, 'issue_slug': issue.volume_slug,
            'issue_localid': issue.localidentifier, 'localid': article.localidentifier})
        request = self.factory.get(url)
        request.subscription = None
        request.saved_citations = []
        # Run
        response = ArticleDetailView.as_view()(
            request, localid=article.localidentifier)
        # Check
        self.assertEqual(response.status_code, 200)


@override_settings(DEBUG=True)
class TestArticleRawPdfView(BaseEruditTestCase):
    def setUp(self):
        super(TestArticleRawPdfView, self).setUp()
        self.factory = RequestFactory()

    @unittest.mock.patch.object(ArticleDigitalObject, 'pdf')
    @unittest.mock.patch.object(ArticleDigitalObject, 'ds_list')
    def test_can_retrieve_the_pdf_of_existing_articles(self, mock_ds, mock_pdf):
        # Setup
        with open(os.path.join(FIXTURE_ROOT, 'dummy.pdf'), 'rb') as f:
            mock_pdf.content = io.BytesIO()
            mock_pdf.content.write(f.read())
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
        url = reverse('public:journal:article_raw_pdf', args=(
            journal_id, issue.volume_slug, issue_id, article_id
        ))
        request = self.factory.get(url)
        request.user = AnonymousUser()
        request.subscription = None

        # Run
        response = ArticleRawPdfView.as_view()(
            request, journal_code=journal_id, issue_slug=issue.volume_slug, issue_localid=issue_id,
            localid=article_id)

        # Check
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/pdf')

    def test_cannot_retrieve_the_pdf_of_inexistant_articles(self):
        # Note: as there is no Erudit fedora repository used during the
        # tess, any tentative of retrieving the PDF of an article should
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
        # Check
        self.assertEqual(response.status_code, 404)

    def test_cannot_be_accessed_if_the_article_is_not_in_open_access(self):
        # Setup
        self.journal.open_access = False
        self.journal.save()
        issue = IssueFactory.create(
            journal=self.journal, year=dt.datetime.now().year, date_published=dt.datetime.now())
        article = ArticleFactory.create(issue=issue)
        journal_id = self.journal.localidentifier
        issue_id = issue.localidentifier
        article_id = article.localidentifier
        url = reverse('public:journal:article_raw_pdf', args=(
            journal_id, issue.volume_slug, issue_id, article_id
        ))
        request = self.factory.get(url)
        request.user = AnonymousUser()
        request.subscription = None

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
        article = ArticleFactory.create(issue=issue, publication_allowed_by_authors=False)
        journal_id = self.journal.localidentifier
        issue_id = issue.localidentifier
        article_id = article.localidentifier
        url = reverse('public:journal:article_raw_pdf', args=(
            journal_id, issue.volume_slug, issue_id, article_id
        ))
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
        request.subscription = None

        # Run
        response = ArticleXmlView.as_view()(
            request, journal_code=journal_id, issue_slug=issue.volume_slug, issue_localid=issue_id,
            localid=article_id)

        # Check
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/xml')


@override_settings(DEBUG=True)
class TestArticleRawPdfFirstPageView(BaseEruditTestCase):
    def setUp(self):
        super(TestArticleRawPdfFirstPageView, self).setUp()
        self.factory = RequestFactory()

    @unittest.mock.patch.object(ArticleDigitalObject, 'pdf')
    @unittest.mock.patch.object(ArticleDigitalObject, 'ds_list')
    def test_can_retrieve_the_first_page_of_the_pdf_of_existing_articles(self, mock_ds, mock_pdf):
        # Setup
        with open(os.path.join(FIXTURE_ROOT, 'dummy-multipages.pdf'), 'rb') as f:
            mock_pdf.content = io.BytesIO()
            mock_pdf.content.write(f.read())
        mock_ds = ['ERUDITXSD300', ]  # noqa

        issue = IssueFactory.create(
            journal=self.journal, date_published=dt.datetime.now() - dt.timedelta(days=1000))
        article = ArticleFactory.create(issue=issue)
        journal_id = self.journal.localidentifier
        issue_id = issue.localidentifier
        article_id = article.localidentifier
        url = reverse('public:journal:article_raw_pdf_firstpage', args=(
            journal_id, issue.volume_slug, issue_id, article_id
        ))
        request = self.factory.get(url)
        request.user = AnonymousUser()

        # Run
        response = ArticleRawPdfFirstPageView.as_view()(
            request, journal_code=journal_id, issue_slug=issue.volume_slug,
            issue_localid=issue_id, localid=article_id)

        # Check
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/pdf')
        raw_pdf = io.BytesIO()
        raw_pdf.write(response.content)
        pdf = PdfFileReader(raw_pdf)
        self.assertEqual(pdf.numPages, 1)


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
