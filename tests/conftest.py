import os
import pytest
import pysolr

from django.core.cache import cache

from eruditarticle.objects.article import EruditArticle
from eruditarticle.objects.publication import EruditPublication
from eruditarticle.objects.journal import EruditJournal
from erudit.test.fedora import FakeAPI
from erudit.test.solr import FakeSolrClient

import erudit.fedora.repository
import erudit.fedora.modelmixins
import erudit.fedora.utils
import erudit.management.commands.import_journals_from_fedora


@pytest.fixture(autouse=True)
def clear_cache():
    # We don't want cache from tests to pollute each others
    cache.clear()


@pytest.fixture(autouse=True)
def mock_fedora_api(monkeypatch):
    def shouldnt_call(*args, **kwargs):
        raise AssertionError("Never supposed to be called")

    monkeypatch.setattr(erudit.fedora.repository.repo.api, "_make_request", shouldnt_call)
    mocked_api = FakeAPI()
    monkeypatch.setattr(erudit.fedora.cache.requests, "get", mocked_api.get)
    monkeypatch.setattr(erudit.fedora.repository.repo.api, "get", mocked_api.get)
    monkeypatch.setattr(erudit.fedora.repository.repo, "api", mocked_api)
    monkeypatch.setattr(erudit.fedora.repository, "api", mocked_api)
    monkeypatch.setattr(erudit.fedora.modelmixins.requests, "get", mocked_api.get)
    monkeypatch.setattr(erudit.fedora.modelmixins, "api", mocked_api)
    monkeypatch.setattr(erudit.fedora.utils, "api", mocked_api)
    monkeypatch.setattr(erudit.management.commands.import_journals_from_fedora, "api", mocked_api)


@pytest.fixture(autouse=True)
def mock_solr_client(monkeypatch):
    import erudit.solr.models

    client = FakeSolrClient()
    monkeypatch.setattr(pysolr, "Solr", lambda *a, **kw: client)
    monkeypatch.setattr(erudit.solr.models, "client", client)


@pytest.fixture
def solr_client():
    return pysolr.Solr()


@pytest.fixture(scope="session", params=os.listdir("./tests/fixtures/article/"))
def eruditarticle(request):
    with open("./tests/fixtures/article/{}".format(request.param), "rb") as xml:
        return EruditArticle(xml.read())


@pytest.fixture(
    scope="session",
    params=[entry for entry in os.scandir("./tests/fixtures/issue/") if entry.is_file()],
)
def eruditpublication(request):
    with open("./tests/fixtures/issue/{}".format(request.param.name), "rb") as xml:
        return EruditPublication(xml.read())


@pytest.fixture(scope="session", params=os.listdir("./tests/fixtures/journal/"))
def eruditjournal(request):
    with open("./tests/fixtures/journal/{}".format(request.param), "rb") as xml:
        return EruditJournal(xml.read())
