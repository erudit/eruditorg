import pytest

from erudit.fedora.utils import localidentifier_from_pid, get_journal_issue_pids_to_sync
from erudit.test.factories import IssueFactory


def test_localidentifier_from_pid():
    assert localidentifier_from_pid("erudit:erudit.ae49.ae03128") == "ae03128"


@pytest.mark.django_db
def test_get_journal_issue_pids_to_sync():
    # Issue in fedora & already published, no synchronization needed.
    issue_1 = IssueFactory(is_published=True, add_to_fedora_journal=True)
    # Issue no longer in fedora & already unpublished, no synchronization needed.
    IssueFactory(journal=issue_1.journal, is_published=False, add_to_fedora_journal=False)
    # Issue in fedora but unpublished, synchronization needed.
    issue_3 = IssueFactory(journal=issue_1.journal, is_published=False, add_to_fedora_journal=True)
    # Issue no longer in fedora but still published, synchronization needed.
    issue_4 = IssueFactory(journal=issue_1.journal, is_published=True, add_to_fedora_journal=False)

    assert get_journal_issue_pids_to_sync(
        issue_1.journal, issue_1.journal.erudit_object.get_published_issues_pids()
    ) == set([issue_3.pid, issue_4.pid])
