# -*- coding: utf-8 -*-

from django.contrib.auth.models import User
from django.core.urlresolvers import reverse

from erudit.factories import JournalFactory
from erudit.models import JournalInformation
from erudit.tests import BaseEruditTestCase


class TestJournalInformationDispatchView(BaseEruditTestCase):
    def test_redirects_to_the_list_of_journals_if_the_user_can_edit_many_journals(self):
        # Setup
        User.objects.create_superuser(
            username='admin', email='admin@xyz.com', password='top_secret')
        self.client.login(username='admin', password='top_secret')
        url = reverse('userspace:journal:journal-information')
        # Run
        response = self.client.get(url, follow=True)
        # Check
        last_url, status_code = response.redirect_chain[-1]
        self.assertTrue(last_url.endswith(reverse('userspace:journal:journal-information-list')))

    def test_redirects_to_the_update_view_of_a_journal_if_the_user_can_edit_one_journal(self):
        # Setup
        self.client.login(username='david', password='top_secret')
        url = reverse('userspace:journal:journal-information')
        # Run
        response = self.client.get(url, follow=True)
        # Check
        last_url, status_code = response.redirect_chain[-1]
        self.assertTrue(last_url.endswith(
            reverse('userspace:journal:journal-information-update',
                    kwargs={'code': self.journal.code})))

    def test_returns_a_403_error_if_the_user_cannot_edit_any_journal(self):
        # Setup
        User.objects.create_user(
            username='test', email='admin@xyz.com', password='top_secret')
        self.client.login(username='test', password='top_secret')
        url = reverse('userspace:journal:journal-information')
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
        url = reverse('userspace:journal:journal-information-list')
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
        url = reverse('userspace:journal:journal-information-update',
                      kwargs={'code': self.journal.code})
        # Run
        response = self.client.get(url)
        # Check
        self.assertEqual(response.status_code, 403)

    def test_embed_the_selected_language_into_the_context(self):
        # Setup
        self.client.login(username='david', password='top_secret')
        url = reverse('userspace:journal:journal-information-update',
                      kwargs={'code': self.journal.code})
        # Run
        response_1 = self.client.get(url)
        response_2 = self.client.get(url, {'lang': 'en'})
        # Check
        self.assertEqual(response_1.status_code, 200)
        self.assertEqual(response_2.status_code, 200)
        self.assertEqual(response_1.context['selected_language'], 'fr')
        self.assertEqual(response_2.context['selected_language'], 'en')

    def test_can_be_used_to_update_journal_information_using_the_current_lang(self):
        # Setup
        self.client.login(username='david', password='top_secret')
        post_data = {
            'about_fr': 'Ceci est un test',
        }
        url = reverse('userspace:journal:journal-information-update',
                      kwargs={'code': self.journal.code})
        # Run
        response = self.client.post(url, post_data, follow=False)
        # Check
        self.assertEqual(response.status_code, 302)
        info = JournalInformation.objects.get(journal=self.journal)
        self.assertEqual(info.about_fr, post_data['about_fr'])

    def test_can_be_used_to_update_journal_information_using_a_specific_lang(self):
        # Setup
        self.client.login(username='david', password='top_secret')
        post_data = {
            'about_en': 'This is a test',
        }
        url = '{}?lang=en'.format(
            reverse('userspace:journal:journal-information-update',
                    kwargs={'code': self.journal.code}))
        # Run
        response = self.client.post(url, post_data, follow=False)
        # Check
        self.assertEqual(response.status_code, 302)
        info = JournalInformation.objects.get(journal=self.journal)
        self.assertEqual(info.about_en, post_data['about_en'])
