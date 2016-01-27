from django.test import TestCase, RequestFactory
from django.contrib.auth.models import User

from erudit.models import Journal, Publisher


class BaseEruditTestCase(TestCase):

    def setUp(self):

        self.factory = RequestFactory()

        self.user = User.objects.create_user(
            username='david',
            email='david.cormier@erudit.org',
            password='top_secret'
        )

        self.other_user = User.objects.create_user(
            username='testuser',
            email='testuser@erudit.org',
            password='top_secret'
        )

        self.publisher = Publisher.objects.create(
            name='Éditeur de test',
        )

        self.other_publisher = Publisher.objects.create(
            name='Autre éditeur de test',
        )

        # Add a journal with a member
        self.journal = Journal.objects.create(
            code='test',
            name='Revue de test',
            publisher=self.publisher,
        )
        self.journal.members.add(self.user)
        self.journal.save()

        # Add a second journal with another member
        self.other_journal = Journal.objects.create(
            code='test',
            name='Autre revue de test',
            publisher=self.other_publisher,
        )
        self.other_journal.members.add(self.other_user)
        self.other_journal.save()
