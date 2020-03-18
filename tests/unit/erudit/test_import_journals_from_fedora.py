import datetime as dt
import pytest
import unittest

from django.core.management import call_command
from erudit.fedora import repository

from erudit.test.factories import IssueFactory, CollectionFactory, JournalTypeFactory
from erudit.models import Journal


pytestmark = pytest.mark.django_db


@unittest.mock.patch('erudit.fedora.modelmixins.cache')
@pytest.mark.parametrize('kwargs', [
    ({}),
    ({'full': True}),
    ({'pid': 'erudit:erudit.journal_test'}),
    ({'mdate': dt.datetime.now().date().isoformat()}),
])
def test_import_journals_from_fedora(mock_cache, kwargs):

    # Issue in fedora & already published, should stay published.
    issue_1 = IssueFactory(journal__localidentifier='journal_test', is_published=True, add_to_fedora_journal=True)
    # Issue no longer in fedora & already unpublished, should stay unpublished.
    issue_2 = IssueFactory(journal=issue_1.journal, is_published=False, add_to_fedora_journal=False)
    # Issue in fedora but unpublished, should be published.
    issue_3 = IssueFactory(journal=issue_1.journal, is_published=False, add_to_fedora_journal=True)
    # Issue no longer in fedora but still published, should be unpublished.
    issue_4 = IssueFactory(journal=issue_1.journal, is_published=True, add_to_fedora_journal=False)

    # Before the import command is run, only issue 1 & 4 are published.
    published_issues = issue_1.journal.issues.filter(is_published=True).values_list('localidentifier', flat=True)
    assert list(published_issues) == [
        issue_1.localidentifier,
        issue_4.localidentifier,
    ]

    # Run the import command.
    call_command("import_journals_from_fedora", *[], **kwargs)

    # Check that we don't use cached objects during import.
    assert mock_cache.get.call_count == 0

    # After the import command is run, only issue 1 & 3 should now be published.
    published_issues = issue_1.journal.issues.filter(is_published=True).values_list('localidentifier', flat=True)
    assert list(published_issues) == [
        issue_1.localidentifier,
        issue_3.localidentifier,
    ]


def test_import_nonexisting_journal_creates_code():
    JournalTypeFactory(id=2)
    CollectionFactory(code='erudit')

    repository.api.register_pid('erudit:erudit.bc1000004')
    repository.api.register_datastream(
        'erudit:erudit.bc1000004',
        '/PUBLICATIONS/content',
        open('./tests/fixtures/journal/publications.xml').read()
    )

    repository.api.register_datastream(
        'erudit:erudit.bc1000004',
        '/OAISET_INFO/content',
        open('./tests/fixtures/journal/oaiset_info.xml').read()
    )

    repository.api.register_datastream(
        'erudit:erudit.bc1000004',
        '/RELS-EXT/content',
        open('./tests/fixtures/journal/rels_ext.xml').read()
    )

    repository.api.register_pid('erudit:erudit.bc1000004.bc1000451')
    call_command("import_journals_from_fedora", *[], **{'pid': 'erudit:erudit.bc1000004'})
    assert Journal.objects.filter(code='bc').exists()


@unittest.mock.patch('erudit.management.commands.import_journals_from_fedora.cache')
@pytest.mark.parametrize('kwargs, expected_count', [
    # There should be 2 delete cache calls, one for the journal and one for the issue.
    ({'pid': 'erudit:erudit.journal_test'}, 2),
    # There should be 1 delete cache call, for the issue.
    ({'issue_pid': 'erudit:erudit.journal_test.issue_test'}, 1),
])
def test_import_journals_from_fedora_delete_cache(mock_cache, kwargs, expected_count):
    issue = IssueFactory(
        journal__localidentifier='journal_test',
        localidentifier='issue_test',
        is_published=False,
        add_to_fedora_journal=True,
    )
    call_command("import_journals_from_fedora", *[], **kwargs)
    assert mock_cache.delete.call_count == expected_count

