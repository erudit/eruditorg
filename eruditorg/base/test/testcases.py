# -*- coding: utf-8 -*-

from django.test import Client
from django.test import RequestFactory
import pytest

from erudit.test.factories import CollectionFactory
from erudit.test.factories import JournalFactory
from erudit.test.factories import PublisherFactory

from .factories import UserFactory


@pytest.mark.django_db
class DBRequiredTestCase(object):
    pass


class EruditTestCase(DBRequiredTestCase):
    @pytest.fixture(autouse=True)
    def _setup_erudit(self):
        # Setup a User instance
        self.user = UserFactory.create(username='foo', email='foobar@erudit.org')
        self.user.set_password('notreallysecret')

        # Setup a basic publisher
        self.publisher = PublisherFactory.create(name='Test publisher')

        # Setup a basic collection
        self.collection = CollectionFactory.create(
            code='erudit', localidentifier='erudit', name='Érudit')

        # Add a journal with a single member
        self.journal = JournalFactory.create(
            collection=self.collection, publishers=[self.publisher])
        self.journal.members.add(self.user)


@pytest.mark.django_db
class EruditClientTestCase(EruditTestCase):
    @pytest.fixture(autouse=True)
    def _setup_client(self):
        self.factory = RequestFactory()
        self.client = Client()
