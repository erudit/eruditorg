import os
import pytest

from django.core.management import call_command
from django.contrib.auth import get_user_model
from core.subscription.models import JournalAccessSubscription

from erudit.test.factories import JournalFactory, OrganisationFactory
from core.subscription.test.factories import JournalManagementSubscriptionFactory

FIXTURE_ROOT = os.path.join(os.path.dirname(__file__), "fixtures")


@pytest.mark.django_db
def test_can_import_batch_to_journal_plan():
    journal = JournalFactory()
    journal_management_subscription = JournalManagementSubscriptionFactory(journal=journal)

    call_command(
        "import_individual_subscriptions_batch",
        *[],
        **{
            "filename": FIXTURE_ROOT + "/subscriptions.csv",
            "shortname": journal.code,
            "use_journal_plan": True,
        }
    )

    assert get_user_model().objects.count() == 5
    assert JournalAccessSubscription.objects.count() == 5

    for subscription in JournalAccessSubscription.objects.all():
        assert journal in subscription.journals.all()


@pytest.mark.django_db
def test_can_import_with_parameters():
    journal = JournalFactory()
    journal_management_subscription = JournalManagementSubscriptionFactory(journal=journal)
    organisation = OrganisationFactory()

    call_command(
        "import_individual_subscriptions_batch",
        *[],
        **{
            "filename": FIXTURE_ROOT + "/subscriptions.csv",
            "shortname": journal.code,
            "sponsor_id": organisation.pk,
            "plan_id": journal_management_subscription.pk,
        }
    )

    assert get_user_model().objects.count() == 5
    assert JournalAccessSubscription.objects.count() == 5

    for subscription in JournalAccessSubscription.objects.all():
        assert subscription.sponsor.pk == organisation.pk
        assert journal in subscription.journals.all()
