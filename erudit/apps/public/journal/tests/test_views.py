# -*- coding: utf-8 -*-

import datetime as dt
import io
import os
import unittest.mock

from django.core.urlresolvers import reverse
from django.test import RequestFactory
from django.test.utils import override_settings

from apps.public.journal.views import ArticleDetailView
from apps.public.journal.views import ArticleRawPdfView
from erudit.factories import ArticleFactory
from erudit.factories import AuthorFactory
from erudit.factories import CollectionFactory
from erudit.factories import IssueFactory
from erudit.factories import JournalFactory
from erudit.factories import JournalInformationFactory
from erudit.fedora.objects import ArticleDigitalObject
from erudit.tests import BaseEruditTestCase

FIXTURE_ROOT = os.path.join(os.path.dirname(__file__), 'fixtures')


@override_settings(DEBUG=True)
class TestJournalDetailView(BaseEruditTestCase):
    def test_can_embed_the_journal_information_in_the_context_if_available(self):
        # Setup
        collection = CollectionFactory.create()
        journal_1 = JournalFactory.create(collection=collection)
        journal_2 = JournalFactory.create(collection=collection)
        journal_info = JournalInformationFactory.create(journal=journal_1)
        url_1 = reverse('public:journal:journal-detail', kwargs={'code': journal_1.code})
        url_2 = reverse('public:journal:journal-detail', kwargs={'code': journal_2.code})
        # Run
        response_1 = self.client.get(url_1)
        response_2 = self.client.get(url_2)
        # Check
        self.assertEqual(response_1.status_code, 200)
        self.assertEqual(response_2.status_code, 200)
        self.assertEqual(response_1.context['journal_info'], journal_info)
        self.assertTrue('journal_info' not in response_2.context)

    def test_can_embed_the_publicated_issues_in_the_context(self):
        # Setup
        collection = CollectionFactory.create()
        journal = JournalFactory.create(collection=collection)
        JournalInformationFactory.create(journal=journal)
        issue_1 = IssueFactory.create(
            journal=journal, date_published=dt.datetime.now() - dt.timedelta(days=1))
        issue_2 = IssueFactory.create(journal=journal, date_published=dt.datetime.now())
        IssueFactory.create(journal=journal, date_published=None)
        url = reverse('public:journal:journal-detail', kwargs={'code': journal.code})
        # Run
        response = self.client.get(url)
        # Check
        self.assertEqual(response.status_code, 200)
        self.assertEqual(list(response.context['issues']), [issue_2, issue_1])

    def test_can_embed_the_latest_issue_in_the_context(self):
        # Setup
        collection = CollectionFactory.create()
        journal = JournalFactory.create(collection=collection)
        JournalInformationFactory.create(journal=journal)
        IssueFactory.create(
            journal=journal, date_published=dt.datetime.now() - dt.timedelta(days=1))
        issue_2 = IssueFactory.create(journal=journal, date_published=dt.datetime.now())
        IssueFactory.create(journal=journal, date_published=None)
        url = reverse('public:journal:journal-detail', kwargs={'code': journal.code})
        # Run
        response = self.client.get(url)
        # Check
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['latest_issue'], issue_2)


class TestJournalAuthorsListView(BaseEruditTestCase):
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
        url = reverse('public:journal:journal-authors-list', kwargs={'code': self.journal.code})

        # Run
        response = self.client.get(url)

        # Check
        self.assertEqual(response.status_code, 200)
        self.assertEqual(list(response.context['authors']), [author_1, ])

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
        url = reverse('public:journal:journal-authors-list', kwargs={'code': self.journal.code})

        # Run
        response_1 = self.client.get(url)
        response_2 = self.client.get(url, {'letter': 'c'})
        response_3 = self.client.get(url, {'letter': 'invalid'})

        # Check
        self.assertEqual(response_1.status_code, 200)
        self.assertEqual(response_2.status_code, 200)
        self.assertEqual(response_3.status_code, 200)
        self.assertEqual(response_1.context['letter'], 'b')
        self.assertEqual(response_2.context['letter'], 'c')
        self.assertEqual(response_3.context['letter'], 'b')

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
        url = reverse('public:journal:journal-authors-list', kwargs={'code': self.journal.code})

        # Run
        response = self.client.get(url)

        # Check
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['letters_counts']), 26)
        self.assertEqual(response.context['letters_counts']['b'], 1)
        self.assertEqual(response.context['letters_counts']['c'], 2)
        for letter in 'adefghijklmnopqrstuvwxyz':
            self.assertEqual(response.context['letters_counts'][letter], 0)


class TestArticlePdfView(BaseEruditTestCase):
    def test_embed_the_localidentifiers_in_the_context(self):
        # Setup
        journal_id = 'arbo139'
        issue_id = 'arbo1515298'
        article_id = '1001942ar'
        url = reverse('public:journal:article-pdf', args=(
            journal_id, issue_id, article_id
        ))
        # Run
        response = self.client.get(url)
        # Check
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['journal_id'], journal_id)
        self.assertEqual(response.context['issue_id'], issue_id)
        self.assertEqual(response.context['article_id'], article_id)


@override_settings(DEBUG=True)
class TestIssueDetailView(BaseEruditTestCase):
    def test_works_with_pks(self):
        # Setup
        issue = IssueFactory.create(journal=self.journal, date_published=dt.datetime.now())
        url = reverse('public:journal:issue-detail', kwargs={
            'journal_code': self.journal.code, 'pk': issue.pk})
        # Run
        response = self.client.get(url)
        # Check
        self.assertEqual(response.status_code, 200)

    def test_works_with_localidentifiers(self):
        # Setup
        issue = IssueFactory.create(
            journal=self.journal, date_published=dt.datetime.now(), localidentifier='test')
        url = reverse('public:journal:issue-detail', kwargs={
            'journal_code': self.journal.code, 'localidentifier': issue.localidentifier})
        # Run
        response = self.client.get(url)
        # Check
        self.assertEqual(response.status_code, 200)


@override_settings(DEBUG=True)
class TestArticleDetailView(BaseEruditTestCase):
    def setUp(self):
        super(TestArticleDetailView, self).setUp()
        self.factory = RequestFactory()

    def test_works_with_pks(self):
        # Setup
        issue = IssueFactory.create(
            journal=self.journal, date_published=dt.datetime.now(), open_access=True)
        article = ArticleFactory.create(issue=issue)
        url = reverse('public:journal:article-detail', kwargs={
            'journal_code': self.journal.code, 'issue_localid': issue.localidentifier,
            'pk': article.pk})
        request = self.factory.get(url)
        # Run
        response = ArticleDetailView.as_view()(
            request, localid=article.localidentifier)
        # Check
        self.assertEqual(response.status_code, 200)

    def test_works_with_localidentifiers(self):
        # Setup
        issue = IssueFactory.create(
            journal=self.journal, date_published=dt.datetime.now(), localidentifier='test',
            open_access=True)
        article = ArticleFactory.create(issue=issue)
        url = reverse('public:journal:article-detail', kwargs={
            'journal_code': self.journal.code, 'issue_localid': issue.localidentifier,
            'localid': article.localidentifier})
        request = self.factory.get(url)
        # Run
        response = ArticleDetailView.as_view()(
            request, localid=article.localidentifier)
        # Check
        self.assertEqual(response.status_code, 200)


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

        journal_id = 'dummy139'
        issue_id = 'dummy1515298'
        article_id = '1001942du'
        url = reverse('public:journal:article-raw-pdf', args=(
            journal_id, issue_id, article_id
        ))
        request = self.factory.get(url)

        # Run
        response = ArticleRawPdfView.as_view()(
            request, journalid=journal_id, issueid=issue_id, articleid=article_id)

        # Check
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/pdf')

    def test_cannot_retrieve_the_pdf_of_inexistant_articles(self):
        # Note: as there is no Erudit fedora repository used during the
        # tess, any tentative of retrieving the PDF of an article should
        # fail.

        # Setup
        journal_id = 'dummy139'
        issue_id = 'dummy1515298'
        article_id = '1001942du'
        url = reverse('public:journal:article-raw-pdf', args=(
            journal_id, issue_id, article_id
        ))
        # Run
        response = self.client.get(url)
        # Check
        self.assertEqual(response.status_code, 404)
