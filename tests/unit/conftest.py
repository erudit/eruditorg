import os
import pytest

from eruditarticle.objects.article import EruditArticle
from eruditarticle.objects.publication import EruditPublication
from eruditarticle.objects.journal import EruditJournal


@pytest.fixture(
    scope="session",
    params=os.listdir('./tests/fixtures/article/')
)
def eruditarticle(request):
    with open('./tests/fixtures/article/{}'.format(request.param), 'rb') as xml:
        return EruditArticle(xml.read())


@pytest.fixture(
    scope="session",
    params=os.listdir('./tests/fixtures/issue/')
)
def eruditpublication(request):
    with open('./tests/fixtures/issue/{}'.format(request.param), 'rb') as xml:
        return EruditPublication(xml.read())


@pytest.fixture(
    scope="session",
    params=os.listdir('./tests/fixtures/journal/')
)
def eruditjournal(request):
    with open('./tests/fixtures/journal/{}'.format(request.param), 'rb') as xml:
        return EruditJournal(xml.read())
