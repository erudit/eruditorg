import os
import unittest
import pytest

from erudit.models import Article, Issue, Journal
from erudit.test.utils import (
    get_erudit_article, get_erudit_publication, get_erudit_journal
)


@pytest.fixture(
    scope="session",
    params=os.listdir('./tests/fixtures/article/')
)
def eruditarticle(request):
    return get_erudit_article(request.param)


@pytest.fixture()
def patch_erudit_article(monkeypatch):
    article = get_erudit_article('009255ar.xml')
    # We might end up needing an erudit_object during the test and when that
    # happens, we don't want to be fetching stuff from Fedora, we want to
    # return a fake object. For now, we'll just load one of our fixtures. In
    # the vast majority of tests, specific values in the erudit object doesn't
    # matter.
    monkeypatch.setattr(Article, 'erudit_object', article)
    monkeypatch.setattr(Article, 'get_erudit_object', lambda self: article)
    m = unittest.mock.MagicMock()
    m.pid = 'foo'
    m.pdf.exists = False
    monkeypatch.setattr(Article, 'get_fedora_object', lambda self: m)


@pytest.fixture(
    scope="session",
    params=os.listdir('./tests/fixtures/issue/')
)
def eruditpublication(request):
    return get_erudit_publication(request.param)


@pytest.fixture()
def patch_erudit_publication(monkeypatch):
    publication = get_erudit_publication('liberte1035607.xml')
    monkeypatch.setattr(Issue, 'erudit_object', publication)
    monkeypatch.setattr(Issue, 'get_erudit_object', lambda self: publication)
    m = unittest.mock.MagicMock()
    m.pid = 'foo'
    m.coverpage.content = None
    m.pdf.exists = False
    monkeypatch.setattr(Issue, 'get_fedora_object', lambda self: m)


@pytest.fixture(
    scope="session",
    params=os.listdir('./tests/fixtures/journal/')
)
def eruditjournal(request):
    return get_erudit_journal(request.param)


@pytest.fixture()
def patch_erudit_journal(monkeypatch):
    journal = get_erudit_journal('mi115.xml')
    monkeypatch.setattr(Journal, 'erudit_object', journal)
    monkeypatch.setattr(Journal, 'get_erudit_object', lambda self: journal)


