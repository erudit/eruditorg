import os
import pytest
import pysolr

from django.core.cache import cache

from base.viewmixins import FedoraServiceRequiredMixin, SolrServiceRequiredMixin
from eruditarticle.objects.article import EruditArticle
from eruditarticle.objects.publication import EruditPublication
from eruditarticle.objects.journal import EruditJournal
from erudit.test.fedora import FakeAPI
from erudit.test.solr import FakeSolrClient
import erudit.fedora.repository
import erudit.fedora.modelmixins


@pytest.fixture(autouse=True)
def clear_cache():
    # We don't want cache from tests to pollute each others
    cache.clear()


@pytest.fixture(autouse=True)
def mock_fedora_api(monkeypatch):
    mocked_api = FakeAPI()
    monkeypatch.setattr(erudit.fedora.repository.repo, 'api', mocked_api)
    monkeypatch.setattr(erudit.fedora.repository, 'api', mocked_api)
    monkeypatch.setattr(erudit.fedora.modelmixins, 'api', mocked_api)
    FedoraServiceRequiredMixin._pytest_check_fedora_status_result = True
    monkeypatch.setattr(
        FedoraServiceRequiredMixin,
        'check_fedora_status',
        lambda self, request: self._pytest_check_fedora_status_result)
    FedoraServiceRequiredMixin._pytest_check_solr_status_result = True
    monkeypatch.setattr(
        SolrServiceRequiredMixin,
        'check_solr_status',
        lambda self, request: self._pytest_check_solr_status_result)


@pytest.fixture(autouse=True)
def mock_solr_client(monkeypatch):
    import erudit.solr.models
    client = FakeSolrClient()
    monkeypatch.setattr(pysolr, 'Solr', lambda *a, **kw: client)
    monkeypatch.setattr(erudit.solr.models, 'client', client)


@pytest.fixture
def solr_client():
    return pysolr.Solr()


@pytest.fixture(
    scope="session",
    params=os.listdir('./tests/fixtures/article/')
)
def eruditarticle(request):
    with open('./tests/fixtures/article/{}'.format(request.param), 'rb') as xml:
        return EruditArticle(xml.read())


@pytest.fixture(
    scope="session",
    params=[entry for entry in os.scandir('./tests/fixtures/issue/') if entry.is_file()]
)
def eruditpublication(request):
    with open('./tests/fixtures/issue/{}'.format(request.param.name), 'rb') as xml:
        return EruditPublication(xml.read())


@pytest.fixture(
    scope="session",
    params=os.listdir('./tests/fixtures/journal/')
)
def eruditjournal(request):
    with open('./tests/fixtures/journal/{}'.format(request.param), 'rb') as xml:
        return EruditJournal(xml.read())
