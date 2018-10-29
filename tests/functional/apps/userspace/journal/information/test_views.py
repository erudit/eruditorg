from django.contrib.contenttypes.models import ContentType
from django.core.urlresolvers import reverse
from django.test import TestCase

from base.test.factories import UserFactory
from base.test.testcases import Client
from erudit.models import JournalInformation
from erudit.test.factories import JournalFactory
from apps.userspace.journal.information.forms import ContributorInlineFormset

from core.authorization.defaults import AuthorizationConfig as AC
from core.authorization.test.factories import AuthorizationFactory


class TestJournalInformationUpdateView(TestCase):
    def test_cannot_be_accessed_by_users_who_cannot_edit_journals(self):
        # Setup
        journal = JournalFactory()
        user = UserFactory()
        client = Client(logged_user=user)
        url = reverse('userspace:journal:information:update',
                      kwargs={'journal_pk': journal.pk})
        # Run
        response = client.get(url)
        # Check
        self.assertEqual(response.status_code, 403)

    def test_embed_the_selected_language_into_the_context(self):
        # Setup
        journal = JournalFactory()
        user = UserFactory()
        journal.members.add(user)
        AuthorizationFactory.create(
            content_type=ContentType.objects.get_for_model(journal), object_id=journal.id,
            user=user, authorization_codename=AC.can_edit_journal_information.codename)
        client = Client(logged_user=user)
        url = reverse('userspace:journal:information:update',
                      kwargs={'journal_pk': journal.pk})
        # Run
        response_1 = client.get(url)
        response_2 = client.get(url, {'lang': 'en'})
        # Check
        self.assertEqual(response_1.status_code, 200)
        self.assertEqual(response_2.status_code, 200)
        self.assertEqual(response_1.context['selected_language'], 'fr')
        self.assertEqual(response_2.context['selected_language'], 'en')

    def test_can_be_used_to_update_journal_information_using_the_current_lang(self):
        # Setup
        user = UserFactory()
        journal = JournalFactory(members=[user])
        AuthorizationFactory.create(
            content_type=ContentType.objects.get_for_model(journal), object_id=journal.id,
            user=user, authorization_codename=AC.can_edit_journal_information.codename)
        client = Client(logged_user=user)
        post_data = {
            'about_fr': 'Ceci est un test',
            'contributor_set-TOTAL_FORMS': 0,
            'contributor_set-INITIAL_FORMS':  0,
            'contributor_set-MAX_FORMS': 1,
            'contributor_set-MIN_FORMS': 0

        }
        formset = ContributorInlineFormset()
        url = reverse('userspace:journal:information:update',
                      kwargs={'journal_pk': journal.pk})
        # Run
        response = client.post(url, post_data, follow=False)
        # Check
        self.assertEqual(response.status_code, 302)
        info = JournalInformation.objects.get(journal=journal)
        self.assertEqual(info.about_fr, post_data['about_fr'])

    def test_can_be_used_to_update_journal_information_using_a_specific_lang(self):
        # Setup
        user = UserFactory()
        journal = JournalFactory(members=[user])
        AuthorizationFactory.create(
            content_type=ContentType.objects.get_for_model(journal), object_id=journal.id,
            user=user, authorization_codename=AC.can_edit_journal_information.codename)
        client = Client(logged_user=user)
        post_data = {
            'about_en': 'This is a test',
            'contributor_set-TOTAL_FORMS': 0,
            'contributor_set-INITIAL_FORMS': 0,
            'contributor_set-MAX_FORMS': 1,
            'contributor_set-MIN_FORMS': 0
        }
        url = '{}?lang=en'.format(
            reverse('userspace:journal:information:update',
                    kwargs={'journal_pk': journal.pk}))
        # Run
        response = client.post(url, post_data, follow=False)
        # Check
        self.assertEqual(response.status_code, 302)
        info = JournalInformation.objects.get(journal=journal)
        self.assertEqual(info.about_en, post_data['about_en'])
