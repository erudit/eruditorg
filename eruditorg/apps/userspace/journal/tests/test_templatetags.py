# -*- coding: utf-8 -*-

from django.core.urlresolvers import resolve
from django.core.urlresolvers import reverse
from django.test import RequestFactory

from erudit.factories import JournalFactory
from erudit.tests import BaseEruditTestCase
from ..templatetags.userspace_journal_tags import journal_url


class TestJournalUrlSimpleTag(BaseEruditTestCase):
    def test_can_resolve_the_current_url_for_another_journal(self):
        # Setup
        journal_2 = JournalFactory.create(collection=self.collection, publishers=[self.publisher])
        factory = RequestFactory()
        base_url = reverse(
            'userspace:journal:information:update', kwargs={'journal_pk': self.journal.pk})
        request = factory.get(base_url)
        request.resolver_match = resolve(base_url)
        # Run
        url = journal_url({'request': request}, journal_2)
        # Check
        self.assertEqual(
            url,
            reverse('userspace:journal:information:update', kwargs={'journal_pk': journal_2.pk}))
