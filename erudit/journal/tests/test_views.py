# -*- coding: utf-8 -*-

import io
import os
import unittest.mock

from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.test import RequestFactory

from erudit.fedora.objects import ArticleDigitalObject
from erudit.tests import BaseEruditTestCase
from journal.views import ArticleRawPdfView

FIXTURE_ROOT = os.path.join(os.path.dirname(__file__), 'fixtures')


class TestJournalInformationDispatchView(BaseEruditTestCase):
    def test_redirects_to_the_list_of_journals_if_the_user_can_edit_many_journals(self):
        # Setup
        User.objects.create_superuser(
            username='admin', email='admin@xyz.com', password='top_secret')
        self.client.login(username='admin', password='top_secret')
        url = reverse('journal:journal-information')
        # Run
        response = self.client.get(url, follow=True)
        # Check
        last_url, status_code = response.redirect_chain[-1]
        self.assertTrue(last_url.endswith(reverse('journal:journal-list')))

    def test_redirects_to_the_update_view_of_a_journal_if_the_user_can_edit_one_journal(self):
        # Setup
        self.client.login(username='david', password='top_secret')
        url = reverse('journal:journal-information')
        # Run
        response = self.client.get(url, follow=True)
        # Check
        last_url, status_code = response.redirect_chain[-1]
        self.assertTrue(last_url.endswith(
            reverse('journal:journal-update', kwargs={'code': self.journal.code})))

    def test_returns_a_403_error_if_the_user_cannot_edit_any_journal(self):
        # Setup
        User.objects.create_user(
            username='test', email='admin@xyz.com', password='top_secret')
        self.client.login(username='test', password='top_secret')
        url = reverse('journal:journal-information')
        # Run
        response = self.client.get(url, follow=True)
        # Check
        self.assertEqual(response.status_code, 403)


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
