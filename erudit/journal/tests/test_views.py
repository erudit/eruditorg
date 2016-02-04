# -*- coding: utf-8 -*-

import codecs
import os
import unittest.mock

from django.core.urlresolvers import reverse
from django.test import RequestFactory

from erudit.fedora.objects import ArticleDigitalObject
from erudit.tests import BaseEruditTestCase
from journal.views import ArticleRawPdfView

FIXTURE_ROOT = os.path.join(os.path.dirname(__file__), 'fixtures')


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
    def test_can_retrieve_the_pdf_of_existing_articles(self, pdfm):
        # Setup
        with codecs.open(
                os.path.join(FIXTURE_ROOT, 'dummy.pdf'),
                encoding='ISO8859-1', mode='rb') as f:
            pdfm.content = f.read()

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
