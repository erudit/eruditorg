from django.core.cache import cache
from django.test import TestCase, RequestFactory
from django.contrib.auth.models import User

from erudit.models import Publisher, Collection
from erudit.factories import JournalFactory


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

        erudit = Collection(code="erudit", name="Érudit")
        erudit.save()

        # Add a journal with a member
        self.journal = JournalFactory.create(publishers=[self.publisher])
        self.journal.members.add(self.user)
        self.journal.collection = erudit
        self.journal.save()

        # Add a second journal with another member
        self.other_journal = JournalFactory.create(publishers=[self.other_publisher])
        self.other_journal.members.add(self.other_user)
        self.other_journal.save()

    def tearDown(self):
        super(BaseEruditTestCase, self).tearDown()
        cache.clear()

    def extract_post_args(self, dom_elem):
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
