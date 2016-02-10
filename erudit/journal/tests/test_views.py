# -*- coding: utf-8 -*-

import io
import os
import unittest.mock

from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.test import RequestFactory

from erudit.factories import JournalFactory
from erudit.fedora.objects import ArticleDigitalObject
from erudit.tests import BaseEruditTestCase
from journal.models import JournalInformation
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
        self.assertTrue(last_url.endswith(reverse('journal:journal-information-list')))

    def test_redirects_to_the_update_view_of_a_journal_if_the_user_can_edit_one_journal(self):
        # Setup
        self.client.login(username='david', password='top_secret')
        url = reverse('journal:journal-information')
        # Run
        response = self.client.get(url, follow=True)
        # Check
        last_url, status_code = response.redirect_chain[-1]
        self.assertTrue(last_url.endswith(
            reverse('journal:journal-information-update', kwargs={'code': self.journal.code})))

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


class TestJournalInformationListView(BaseEruditTestCase):
    def test_includes_only_journals_that_can_be_edited_by_the_current_user(self):
        # Setup
        for _ in range(6):
            JournalFactory.create(publishers=[self.publisher])
        self.client.login(username='david', password='top_secret')
        url = reverse('journal:journal-information-list')
        # Run
        response = self.client.get(url)
        # Check
        self.assertEqual(response.status_code, 200)
        self.assertEqual(list(response.context['journals']), [self.journal, ])


class TestJournalInformationUpdateView(BaseEruditTestCase):
    def test_cannot_be_accessed_by_users_who_cannot_edit_journals(self):
        # Setup
        User.objects.create_user(
            username='test', email='admin@xyz.com', password='top_secret')
        self.client.login(username='test', password='top_secret')
        url = reverse('journal:journal-information-update', kwargs={'code': self.journal.code})
        # Run
        response = self.client.get(url)
        # Check
        self.assertEqual(response.status_code, 403)

    def test_embed_the_selected_language_into_the_context(self):
        # Setup
        self.client.login(username='david', password='top_secret')
        url = reverse('journal:journal-information-update', kwargs={'code': self.journal.code})
        # Run
        response_1 = self.client.get(url)
        response_2 = self.client.get(url, {'lang': 'en'})
        # Check
        self.assertEqual(response_1.status_code, 200)
        self.assertEqual(response_2.status_code, 200)
        self.assertEqual(response_1.context['selected_language'], 'fr-ca')
        self.assertEqual(response_2.context['selected_language'], 'en')

    def test_can_be_used_to_update_journal_information_using_the_current_lang(self):
        # Setup
        self.client.login(username='david', password='top_secret')
        post_data = {
            'about_fr_ca': 'Ceci est un test',
        }
        url = reverse('journal:journal-information-update', kwargs={'code': self.journal.code})
        # Run
        response = self.client.post(url, post_data, follow=False)
        # Check
        self.assertEqual(response.status_code, 302)
        info = JournalInformation.objects.get(journal=self.journal)
        self.assertEqual(info.about_fr_ca, post_data['about_fr_ca'])

    def test_can_be_used_to_update_journal_information_using_a_specific_lang(self):
        # Setup
        self.client.login(username='david', password='top_secret')
        post_data = {
            'about_en': 'This is a test',
        }
        url = '{}?lang=en'.format(
            reverse('journal:journal-information-update', kwargs={'code': self.journal.code}))
        # Run
        response = self.client.post(url, post_data, follow=False)
        # Check
        self.assertEqual(response.status_code, 302)
        info = JournalInformation.objects.get(journal=self.journal)
        self.assertEqual(info.about_en, post_data['about_en'])


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
