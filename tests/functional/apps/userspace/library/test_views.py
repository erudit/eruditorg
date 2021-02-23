import pytest

from django.test.client import Client
from django.urls import reverse

from apps.userspace.library.stats.forms import (
    CounterJR1Form,
    StatsFormInfo,
)
from apps.userspace.library.stats.views import (
    get_stats_form,
    compute_end_year,
)
from erudit.test.factories import OrganisationFactory
from core.subscription.test.factories import JournalAccessSubscriptionFactory
from base.test.factories import UserFactory


@pytest.mark.django_db
class TestLibraryUserspaceViews:
    @pytest.mark.parametrize("subscription_status_valid", (True, False, None))
    def test_organisation_member_can_access_regardless_of_subscription_status(
        self, subscription_status_valid
    ):

        member = UserFactory(username="test")
        member.set_password("notsecret")
        member.save()

        organisation = OrganisationFactory()
        organisation.members.add(member)
        organisation.save()

        client = Client()
        client.login(username=member.username, password="notsecret")

        if subscription_status_valid in (True, False):
            JournalAccessSubscriptionFactory(
                valid=subscription_status_valid, organisation=organisation
            )
        url = reverse("userspace:library:home", kwargs={"organisation_pk": organisation.pk})
        resp = client.get(url)
        assert resp.status_code == 200


class TestGetStatsForm:
    def test_can_bind_form_if_submitted(self):
        form_info = StatsFormInfo(
            form_class=CounterJR1Form,
            code="formcode",
            tab_label="",
            title="",
            description="",
            counter_release="R4",
        )
        form, is_submitted = get_stats_form(form_info, {form_info.submit_name: ""}, 2019)
        assert form.is_bound
        assert is_submitted

    def test_wont_bind_form_if_not_submitted(self):
        form_info = StatsFormInfo(
            form_class=CounterJR1Form,
            code="formcode",
            tab_label="",
            title="",
            description="",
            counter_release="R4",
        )
        form, is_submitted = get_stats_form(form_info, {"year": "2019"}, 2019)
        assert not form.is_bound
        assert not is_submitted


@pytest.mark.parametrize(
    "current_year,last_sub_year,expected",
    ((2019, None, 2019), (2019, 2018, 2018), (2019, 2020, 2019)),
)
def test_compute_end_year(current_year, last_sub_year, expected):
    assert compute_end_year(current_year, last_sub_year) == expected
