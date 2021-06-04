import datetime as dt
import pytest

from django.test.client import Client
from django.urls import reverse

from apps.userspace.library.stats.forms import (
    CounterJR1Form,
    DatesRange,
)

from apps.userspace.library.stats.views import (
    get_stats_form,
    compute_r4_end_month,
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
            JournalAccessSubscriptionFactory(organisation=organisation)
        url = reverse("userspace:library:home", kwargs={"organisation_pk": organisation.pk})
        resp = client.get(url)
        assert resp.status_code == 200


class TestGetStatsForm:
    def test_can_bind_form_if_submitted(self):
        """If counter report form was submitted, then get_stats_form should bind it with the request
        data."""
        form, is_submitted = get_stats_form(
            CounterJR1Form,
            {CounterJR1Form.submit_name(): ""},
            DatesRange(dt.date(2019, 1, 1), dt.date(2019, 12, 1)),
        )
        assert form.is_bound
        assert is_submitted

    def test_wont_bind_form_if_not_submitted(self):
        """If counter report form wasn't submitted, then get_stats_form shouldn't bind it. """
        form, is_submitted = get_stats_form(
            CounterJR1Form, {"year": "2019"}, DatesRange(dt.date(2019, 1, 1), dt.date(2019, 12, 1))
        )
        assert not form.is_bound
        assert not is_submitted


@pytest.mark.parametrize(
    "now,expected",
    (
        (dt.date(2019, 1, 1), dt.date(2018, 12, 1)),
        (dt.date(2019, 5, 1), dt.date(2019, 4, 1)),
    ),
)
def test_compute_end_month(now, expected):
    assert compute_r4_end_month(now) == expected
