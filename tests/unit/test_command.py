from erudit.test.factories import IssueFactory
import pytest

from erudit.test import BaseEruditTestCase
from erudit.management.commands.import_journals_from_fedora import _create_issue_contributor_object


class TestCommand(BaseEruditTestCase):
    def test_can_raise_valueerror_when_both_roles_are_specified(self):
        issue = IssueFactory(journal=self.journal)
        issue_contributor = {
            'role_fr': 'directeur',
            'role_en': 'director',
            'firstname': 'A',
            'lastname': 'B',
        }

        with pytest.raises(ValueError):
            _create_issue_contributor_object(
                issue_contributor,
                issue,
            )

    def test_can_create_director(self):
        issue = IssueFactory(journal=self.journal)
        issue_contributor = {
            'role_fr': 'directeur',
            'firstname': 'A',
            'lastname': 'B',
        }
        contributor = _create_issue_contributor_object(
            issue_contributor,
            issue,
            is_director=True
        )

        assert contributor.is_director
        assert not contributor.is_editor

    def test_can_create_editor(self):
        issue = IssueFactory(journal=self.journal)
        issue_contributor = {
            'role_fr': 'directeur',
            'firstname': 'A',
            'lastname': 'B',
        }
        contributor = _create_issue_contributor_object(
            issue_contributor,
            issue,
            is_editor=True
        )

        assert not contributor.is_director
        assert contributor.is_editor
