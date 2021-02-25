import pytest

from erudit.models import Journal
from base.test.factories import UserFactory
from erudit.test.factories import JournalFactory, CollectionFactory
from core.editor.test.factories import ProductionTeamFactory

from core.journal.rules_helpers import get_editable_journals


@pytest.fixture
def managed_collection():
    return CollectionFactory(code="managed")


@pytest.mark.django_db
class TestGetEditableJournals:
    @pytest.fixture(autouse=True)
    def init_settings(self, settings):
        settings.MANAGED_COLLECTIONS = ("managed",)

    def test_a_superuser_can_edit_everything(self, managed_collection):
        journals = JournalFactory.create_batch(2, collection=managed_collection)
        superuser = UserFactory(is_superuser=True)
        assert set(get_editable_journals(superuser)) == set(journals)

    def test_a_staff_user_can_edit_everything(self, managed_collection):
        journals = JournalFactory.create_batch(2, collection=managed_collection)
        superuser = UserFactory(is_staff=True)
        assert set(get_editable_journals(superuser)) == set(journals)

    def test_a_user_can_edit_journals_he_is_a_member_of(self):
        user = UserFactory()
        journal = JournalFactory(members=[user])
        assert list(get_editable_journals(user)) == [journal]

    def test_a_production_team_member_can_edit_the_teams_journals(self):
        production_team = ProductionTeamFactory()

        production_team.journals.add(JournalFactory())
        production_team.save()

        # Create another journal, to be sure it doesn't show up in the list
        JournalFactory()

        user = UserFactory()
        user.groups.add(production_team.group)
        user.save()

        assert set(get_editable_journals(user)) == set(production_team.journals.all())

    def test_a_production_team_member_can_edit_the_teams_journals_and_its_journals(self):

        production_team = ProductionTeamFactory()

        production_team.journals.add(JournalFactory())
        production_team.save()

        # Create another journal, to be sure it doesn't show up in the list
        journal = JournalFactory()

        user = UserFactory()
        user.groups.add(production_team.group)
        user.save()

        journal.members.add(user)
        journal.save()

        assert set(get_editable_journals(user)) == set(Journal.objects.all())
