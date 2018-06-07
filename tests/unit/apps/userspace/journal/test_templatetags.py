import pytest
from django.core.urlresolvers import resolve
from django.core.urlresolvers import reverse
from django.test import RequestFactory

from erudit.test.factories import JournalFactory, PublisherFactory

from apps.userspace.journal.templatetags.userspace_journal_tags import journal_url

pytestmark = pytest.mark.django_db


def test_can_resolve_the_current_url_for_another_journal():
    publisher = PublisherFactory()
    journal1 = JournalFactory(publishers=[publisher])
    journal2 = JournalFactory(publishers=[publisher])
    factory = RequestFactory()
    base_url = reverse(
        'userspace:journal:information:update', kwargs={'journal_pk': journal1.pk})
    request = factory.get(base_url)
    request.resolver_match = resolve(base_url)
    url = journal_url({'request': request}, journal2)
    EXPECTED = reverse('userspace:journal:information:update', kwargs={'journal_pk': journal2.pk})
    assert url == EXPECTED
