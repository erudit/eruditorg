# -*- coding: utf-8 -*-

from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.core.urlresolvers import reverse

from core.authorization.defaults import AuthorizationConfig as AC
from core.authorization.factories import AuthorizationFactory
from erudit.models import JournalInformation
from erudit.test import BaseEruditTestCase


class TestJournalInformationUpdateView(BaseEruditTestCase):
    def test_cannot_be_accessed_by_users_who_cannot_edit_journals(self):
        # Setup
        User.objects.create_user(
            username='test', email='admin@xyz.com', password='top_secret')
        self.client.login(username='test', password='top_secret')
        url = reverse('userspace:journal:information:update',
                      kwargs={'journal_pk': self.journal.pk})
        # Run
        response = self.client.get(url)
        # Check
        self.assertEqual(response.status_code, 403)

    def test_embed_the_selected_language_into_the_context(self):
        # Setup
        AuthorizationFactory.create(
            content_type=ContentType.objects.get_for_model(self.journal), object_id=self.journal.id,
            user=self.user, authorization_codename=AC.can_edit_journal_information.codename)
        self.client.login(username='david', password='top_secret')
        url = reverse('userspace:journal:information:update',
                      kwargs={'journal_pk': self.journal.pk})
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
        AuthorizationFactory.create(
            content_type=ContentType.objects.get_for_model(self.journal), object_id=self.journal.id,
            user=self.user, authorization_codename=AC.can_edit_journal_information.codename)
        self.client.login(username='david', password='top_secret')
        post_data = {
            'about_fr': 'Ceci est un test',
        }
        url = reverse('userspace:journal:information:update',
                      kwargs={'journal_pk': self.journal.pk})
        # Run
        response = self.client.post(url, post_data, follow=False)
        # Check
        self.assertEqual(response.status_code, 302)
        info = JournalInformation.objects.get(journal=self.journal)
        self.assertEqual(info.about_fr, post_data['about_fr'])

    def test_can_be_used_to_update_journal_information_using_a_specific_lang(self):
        # Setup
        AuthorizationFactory.create(
            content_type=ContentType.objects.get_for_model(self.journal), object_id=self.journal.id,
            user=self.user, authorization_codename=AC.can_edit_journal_information.codename)
        self.client.login(username='david', password='top_secret')
        post_data = {
            'about_en': 'This is a test',
        }
        url = '{}?lang=en'.format(
            reverse('userspace:journal:information:update',
                    kwargs={'journal_pk': self.journal.pk}))
        # Run
        response = self.client.post(url, post_data, follow=False)
        # Check
        self.assertEqual(response.status_code, 302)
        info = JournalInformation.objects.get(journal=self.journal)
        self.assertEqual(info.about_en, post_data['about_en'])
