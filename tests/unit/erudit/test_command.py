import mock
from erudit.test.factories import IssueFactory
import pytest

from eruditarticle.objects.person import Person

from erudit.management.commands.import_journals_from_fedora import _create_issue_contributor_object


@pytest.mark.django_db
class TestCommand:

    def test_can_create_issue_contributor_from_ea_output(self, eruditpublication):

        # Test that this does not crash
        for director in eruditpublication.directors:
            _create_issue_contributor_object(
                director, IssueFactory()
            )

    def test_can_raise_valueerror_when_both_roles_are_specified(self):
        issue = IssueFactory()

        issue_contributor = mock.MagicMock(
            Person,
            role={'fr': 'directeur', 'en': 'director'},
            firstname='A',
            lastname='B',
        )

        with pytest.raises(ValueError):
            _create_issue_contributor_object(
                issue_contributor,
                issue,
            )

    def test_can_find_other_language_only_when_french_and_english_are_absent(self):
        issue = IssueFactory()

        issue_contributor = mock.MagicMock(
            Person,
            role={'fr': 'directeur', 'es': 'director'},
            firstname='A',
            lastname='B',
        )

        contributor = _create_issue_contributor_object(
            issue_contributor,
            issue,
            is_director=True
        )

        assert contributor.role_name == 'directeur'

        issue_contributor = mock.MagicMock(
            Person,
            role={'es': 'director'},
            firstname='A',
            lastname='B',
        )

        contributor = _create_issue_contributor_object(
            issue_contributor,
            issue,
            is_director=True
        )

        assert contributor.role_name == 'director'

    def test_can_create_director(self):
        issue = IssueFactory()
        issue_contributor = mock.MagicMock(
            Person,
            role={'fr': 'directeur'},
            firstname='A',
            lastname='B',
        )

        contributor = _create_issue_contributor_object(
            issue_contributor,
            issue,
            is_director=True
        )

        assert contributor.is_director
        assert not contributor.is_editor

    def test_can_create_editor(self):
        issue = IssueFactory()
        issue_contributor = mock.MagicMock(
            Person,
            role={'fr': 'directeur'},
            firstname='A',
            lastname='B',
        )

        contributor = _create_issue_contributor_object(
            issue_contributor,
            issue,
            is_editor=True
        )

        assert not contributor.is_director
        assert contributor.is_editor
