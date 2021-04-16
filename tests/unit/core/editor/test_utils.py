import datetime as dt
import pytest

from django.contrib.auth.models import Group
from core.editor.test.factories import ProductionTeamFactory
from core.editor.utils import get_archive_date, get_production_teams_groups
from erudit.test.factories import JournalFactory


def test_can_calculate_archive_date():
    from core.editor.conf import settings as editor_settings

    editor_settings.ARCHIVE_DAY_OFFSETS = 1
    now = dt.datetime.now()
    assert get_archive_date(now) == now + dt.timedelta(editor_settings.ARCHIVAL_DAY_OFFSET)


@pytest.mark.django_db
class TestGetProductionTeamsGroups:
    def test_get_production_teams_groups_with_one_group(self):
        journal = JournalFactory()
        group = Group.objects.create(name="Production team")
        production_team = ProductionTeamFactory(group=group, identifier="production-team")
        production_team.journals.add(journal)
        assert list(get_production_teams_groups(journal=journal)) == [group]

    def test_get_production_teams_groups_with_multiple_groups(self):
        journal = JournalFactory()
        group_1 = Group.objects.create(name="Production team 1")
        production_team_1 = ProductionTeamFactory(group=group_1, identifier="production-team-1")
        production_team_1.journals.add(journal)
        group_2 = Group.objects.create(name="Production team 2")
        production_team_2 = ProductionTeamFactory(group=group_2, identifier="production-team-2")
        production_team_2.journals.add(journal)
        assert list(get_production_teams_groups(journal=journal)) == [group_1, group_2]

    def test_get_production_teams_groups_with_no_group(self):
        journal = JournalFactory()
        main_group = Group.objects.create(name="Main production team")
        ProductionTeamFactory(group=main_group, identifier="main-production-team")
        assert list(get_production_teams_groups(journal=journal)) == [main_group]
