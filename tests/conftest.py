import os
import unittest
import pytest

from eruditarticle.objects.article import EruditArticle
from eruditarticle.objects.publication import EruditPublication
from eruditarticle.objects.journal import EruditJournal
from erudit.models import Article, Issue, Journal


def _get_mock_fedora_object(fixturepath):
    m = unittest.mock.MagicMock()
    m.pid = 'foo'
    m.pdf.exists = False
    m.coverpage.content = None
    with open('./tests/fixtures/{}'.format(fixturepath), 'rb') as xml:
        m.xml_content = xml.read()
    return m


@pytest.fixture(
    scope="session",
    params=os.listdir('./tests/fixtures/article/')
)
def eruditarticle(request):
    with open('./tests/fixtures/article/{}'.format(request.param), 'rb') as xml:
        return EruditArticle(xml.read())


@pytest.fixture()
def patch_erudit_article(monkeypatch):
    fedora = _get_mock_fedora_object('article/009255ar.xml')
    monkeypatch.setattr(Article, 'fedora_object', fedora)


@pytest.fixture(
    scope="session",
    params=os.listdir('./tests/fixtures/issue/')
)
def eruditpublication(request):
    with open('./tests/fixtures/issue/{}'.format(request.param), 'rb') as xml:
        return EruditPublication(xml.read())


@pytest.fixture()
def patch_erudit_publication(monkeypatch):
    fedora = _get_mock_fedora_object('issue/liberte1035607.xml')
    monkeypatch.setattr(Issue, 'fedora_object', fedora)


@pytest.fixture(
    scope="session",
    params=os.listdir('./tests/fixtures/journal/')
)
def eruditjournal(request):
    with open('./tests/fixtures/journal/{}'.format(request.param), 'rb') as xml:
        return EruditJournal(xml.read())


@pytest.fixture()
def patch_erudit_journal(monkeypatch):
    fedora = _get_mock_fedora_object('journal/mi115.xml')
    monkeypatch.setattr(Journal, 'fedora_object', fedora)

