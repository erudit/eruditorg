from django.test import TestCase
from django.contrib.auth.models import User

from erudit.models import Journal, Publisher


class BaseEruditTestCase(TestCase):

    def setUp(self):

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

        # Add a publisher
        self.publisher.members.add(self.user)
        self.publisher.save()

        self.other_publisher = Publisher.objects.create(
            name='Autre éditeur de test',
        )

        # Add a second publisher
        self.other_publisher.members.add(self.other_user)
        self.other_publisher.save()

        # Add a journal
        self.journal = Journal.objects.create(
            code='test',
            name='Revue de test',
            publisher=self.publisher,
        )

        # Add a second journal
        self.other_journal = Journal.objects.create(
            code='test',
            name='Autre revue de test',
            publisher=self.other_publisher,
        )
