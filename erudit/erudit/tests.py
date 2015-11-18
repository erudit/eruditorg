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

        self.publisher = Publisher.objects.create(
            name='Éditeur de test',
        )

        self.publisher.members.add(self.user)
        self.publisher.save()

        self.journal = Journal.objects.create(
            code='test',
            name='Revue de test',
            publisher=self.publisher,
        )
