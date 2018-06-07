from django.test import Client as ClientBase
from django.test import RequestFactory
import pytest

from erudit.test.factories import CollectionFactory
from erudit.test.factories import JournalFactory
from erudit.test.factories import PublisherFactory

from .factories import UserFactory


class Client(ClientBase):
    def __init__(self, logged_user=None, **kwargs):
        super().__init__(**kwargs)
        if logged_user:
            assert self.login(
                username=logged_user.username, password=logged_user._plaintext_password)


def extract_post_args(dom_elem):
    """Returns a ``post()``-ready dict of all input/select values in ``dom_elem``.

    ``dom_elem`` being an element extracted from an etree-parsed DOM.

    If you have multiple forms in your response, be sure to supply a sub-element if you don't
    want all inputs in the page to be included.
    """
    result = {}
    for input in dom_elem.iterdescendants('input'):
        if input.attrib['type'] == 'checkbox':
            value = 'on' if input.attrib.get('checked') else ''
        else:
            value = input.attrib.get('value', '')
        result[input.attrib['name']] = value
    for select in dom_elem.iterdescendants('select'):
        options = list(select.xpath('option[@selected=\'selected\']'))
        if 'multiple' in select.attrib:
            value = [elem.get('value') for elem in options]
        else:
            try:
                value = options[0].get('value')
            except IndexError:
                value = ''
        result[select.attrib['name']] = value
    return result


@pytest.mark.django_db
class DBRequiredTestCase:
    pass


class EruditTestCase(DBRequiredTestCase):
    @pytest.fixture(autouse=True)
    def _setup_erudit(self):
        # Setup a User instance
        self.user = UserFactory.create(username='foo', email='foobar@erudit.org')
        self.user.set_password('notreallysecret')
        self.user.save()

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
