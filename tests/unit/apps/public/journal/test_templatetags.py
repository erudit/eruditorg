import pytest

from erudit.test.factories import IssueFactory, JournalFactory

from apps.public.journal.templatetags.public_journal_tags import (
    issue_coverpage_url,
    journal_logo_url,
)


@pytest.mark.django_db
def test_issue_coverpage_url():
    issue = IssueFactory()
    coverpage_url = issue_coverpage_url(issue)
    assert "coverpage.jpg" in coverpage_url


@pytest.mark.django_db
def test_journal_logo_url():
    journal = JournalFactory()
    logo_url = journal_logo_url(journal)
    assert "logo.jpg" in logo_url
