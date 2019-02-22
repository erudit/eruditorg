import datetime as dt
import pytest

from django.core.management import call_command

from erudit.test.factories import IssueFactory


pytestmark = pytest.mark.django_db


@pytest.mark.parametrize('kwargs', [
    ({}),
    ({'full': True}),
    ({'pid': 'erudit:erudit.journal_test'}),
    ({'mdate': dt.datetime.now().date().isoformat()}),
])
def test_import_journals_from_fedora(kwargs):
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

    # After the import command is run, only issue 1 & 3 should now be published.
    published_issues = issue_1.journal.issues.filter(is_published=True).values_list('localidentifier', flat=True)
    assert list(published_issues) == [
        issue_1.localidentifier,
        issue_3.localidentifier,
    ]
