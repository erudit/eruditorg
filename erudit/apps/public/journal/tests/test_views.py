# -*- coding: utf-8 -*-

import io
import os
import unittest.mock

from django.core.urlresolvers import reverse
from django.test import RequestFactory

from apps.public.journal.views import ArticleRawPdfView
from erudit.factories import CollectionFactory
from erudit.factories import JournalFactory
from erudit.factories import JournalInformationFactory
from erudit.fedora.objects import ArticleDigitalObject
from erudit.tests import BaseEruditTestCase

FIXTURE_ROOT = os.path.join(os.path.dirname(__file__), 'fixtures')


class TestJournalDetailView(BaseEruditTestCase):
    def test_can_embed_the_journal_information_in_the_context_if_available(self):
        # Setup
        collection = CollectionFactory.create()
        journal_1 = JournalFactory.create(collection=collection)
        journal_2 = JournalFactory.create(collection=collection)
        journal_info = JournalInformationFactory.create(journal=journal_1)
        url_1 = reverse('journal:journal-detail', kwargs={'code': journal_1.code})
        url_2 = reverse('journal:journal-detail', kwargs={'code': journal_2.code})
        # Run
        response_1 = self.client.get(url_1)
        response_2 = self.client.get(url_2)
        # Check
        self.assertEqual(response_1.status_code, 200)
        self.assertEqual(response_2.status_code, 200)
        self.assertEqual(response_1.context['journal_info'], journal_info)
        self.assertTrue('journal_info' not in response_2.context)


class TestArticlePdfView(BaseEruditTestCase):
    def test_embed_the_localidentifiers_in_the_context(self):
        # Setup
        journal_id = 'arbo139'
        issue_id = 'arbo1515298'
        article_id = '1001942ar'
        url = reverse('journal:article-pdf', args=(
            journal_id, issue_id, article_id
        ))
        # Run
        response = self.client.get(url)
        # Check
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['journal_id'], journal_id)
        self.assertEqual(response.context['issue_id'], issue_id)
        self.assertEqual(response.context['article_id'], article_id)


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
        url = reverse('journal:article-raw-pdf', args=(
            journal_id, issue_id, article_id
        ))
        request = self.factory.get(url)

        # Run
        response = ArticleRawPdfView.as_view()(request, journal_id, issue_id, article_id)

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
        url = reverse('journal:article-raw-pdf', args=(
            journal_id, issue_id, article_id
        ))
        # Run
        response = self.client.get(url)
        # Check
        self.assertEqual(response.status_code, 404)
