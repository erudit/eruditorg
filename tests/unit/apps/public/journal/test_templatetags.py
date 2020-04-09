import pytest

from unittest import mock
from datetime import datetime

from apps.public.journal.templatetags.public_journal_tags import issue_coverpage_url, journal_logo_url

@pytest.mark.parametrize('external_url', (True, False))
def test_issue_coverpage_url(external_url, settings):
    issue = mock.Mock()
    now = datetime(year=2011, month=1, day=1, hour=0, minute=0, second=0)
    issue.fedora_object.coverpage.last_modified.return_value = now
    issue.localidentifier = 1234

    if external_url:
        settings.FEDORA_ASSETS_EXTERNAL_URL = "https://assets.erudit.tech/"

    coverpage_url = issue_coverpage_url(issue)

    if external_url:
        assert 'https://assets.erudit.tech' in coverpage_url
    else:
        assert coverpage_url.index("/couverture") == 0
    assert '20110101000000.jpg' in coverpage_url


@pytest.mark.parametrize('external_url', (True, False))
def test_journal_logo_url(external_url, settings):
    journal = mock.Mock()
    now = datetime(year=2011, month=1, day=1, hour=0, minute=0, second=0)
    journal.fedora_object.logo.last_modified.return_value = now
    journal.code = 1234

    if external_url:
        settings.FEDORA_ASSETS_EXTERNAL_URL = "https://assets.erudit.tech/"

    logo_url = journal_logo_url(journal)

    if external_url:
        assert 'https://assets.erudit.tech' in logo_url
    else:
        assert logo_url.index("/logo") == 0
    assert '20110101000000.jpg' in logo_url
