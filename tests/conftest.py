import os
import pytest

from erudit.test.utils import (
    get_erudit_article, get_erudit_publication, get_erudit_journal
)


@pytest.fixture(
    scope="session",
    params=os.listdir('./tests/fixtures/article/')
)
def eruditarticle(request):
    return get_erudit_article(request.param)


@pytest.fixture(
    scope="session",
    params=os.listdir('./tests/fixtures/issue/')
)
def eruditpublication(request):
    return get_erudit_publication(request.param)


@pytest.fixture(
    scope="session",
    params=os.listdir('./tests/fixtures/journal/')
)
def eruditjournal(request):
    return get_erudit_journal(request.param)
