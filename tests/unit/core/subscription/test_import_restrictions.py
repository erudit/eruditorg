import datetime
import pytest

from django.core.management import call_command
from django.contrib.auth import get_user_model

from erudit.models import Organisation
from erudit.test.factories import OrganisationFactory
from core.accounts.models import LegacyAccountProfile
from core.subscription.models import (
    JournalAccessSubscription,
    JournalAccessSubscriptionPeriod,
    InstitutionReferer,
)
from core.subscription.restriction.models import Revueabonne
from core.subscription.test.factories import (
    JournalAccessSubscriptionFactory,
    InstitutionIPAddressRange,
)
from core.subscription.restriction.test.factories import (
    AbonneFactory,
    RevueFactory,
    RevueabonneFactory,
    IpabonneFactory,
)
from core.subscription.management.commands import import_restrictions

from core.accounts.test.factories import LegacyAccountProfileFactory
from erudit.test.factories import JournalFactory


@pytest.mark.django_db
def test_import_subscriber():
    # Verify that we properly import subscriber information
    # Setup
    abonne1 = AbonneFactory.create()

    subscription_qs = Revueabonne.objects
    command = import_restrictions.Command()
    command.import_restriction_subscriber(abonne1, subscription_qs)

    # Run & check
    accprofile = LegacyAccountProfile.objects.get(legacy_id=abonne1.abonneid)
    org = accprofile.organisation
    assert org.name == abonne1.abonne
    assert org.account_id == str(abonne1.abonneid)
    assert org.sushi_requester_id == abonne1.requesterid
    assert accprofile.user.username == "restriction-{}".format(abonne1.abonneid)
    assert accprofile.user.email == abonne1.courriel
    assert accprofile.legacy_id == str(abonne1.abonneid)


@pytest.mark.django_db
def test_import_journal():
    # Verify that journal subscriptions are properly imported
    # Setup
    journal1 = JournalFactory.create()
    abonne1 = AbonneFactory.create()
    revue1 = RevueFactory.create(titrerevabr=journal1.code)
    RevueabonneFactory.create(
        abonneid=abonne1.abonneid, revueid=revue1.revueid, anneeabonnement=2018
    )

    subscription_qs = Revueabonne.objects
    command = import_restrictions.Command()
    command.import_restriction_subscriber(abonne1, subscription_qs)

    # Run & check
    assert JournalAccessSubscription.objects.count() == 1
    sub = JournalAccessSubscription.objects.first()
    assert sub.get_subscription_type() == JournalAccessSubscription.TYPE_INSTITUTIONAL
    assert sub.journals.filter(pk=journal1.pk).exists()
    assert sub.organisation.name == abonne1.abonne


@pytest.mark.django_db
def test_assign_user_to_existing_organisation():
    """If an organisation has the LegacyOrganisationId of the restriction user to import,
    add the created user to this organisation"""
    org = OrganisationFactory()
    journal1 = JournalFactory.create()
    abonne1 = AbonneFactory.create()
    abonne1.abonneid = org.account_id
    revue1 = RevueFactory.create(titrerevabr=journal1.code)
    RevueabonneFactory.create(
        abonneid=abonne1.abonneid, revueid=revue1.revueid, anneeabonnement=2018
    )

    subscription_qs = Revueabonne.objects
    command = import_restrictions.Command()
    command.import_restriction_subscriber(abonne1, subscription_qs)

    # test that no new organisation has been created
    assert Organisation.objects.count() == 1
    assert Organisation.objects.first().members.count() == 1


@pytest.mark.django_db
def test_import_can_rename_organisation():
    organisation = OrganisationFactory()
    organisation.name = "old name"
    organisation.save()
    journal1 = JournalFactory.create()
    abonne1 = AbonneFactory.create()
    abonne1.abonne = "new name"
    abonne1.abonneid = organisation.account_id

    revue1 = RevueFactory.create(titrerevabr=journal1.code)
    RevueabonneFactory.create(
        abonneid=abonne1.abonneid, revueid=revue1.revueid, anneeabonnement=2018
    )

    subscription_qs = Revueabonne.objects
    command = import_restrictions.Command()
    command.import_restriction_subscriber(abonne1, subscription_qs)

    assert Organisation.objects.count() == 1
    organisation = Organisation.objects.first()
    assert organisation.name == "new name"


@pytest.mark.django_db
def test_user_email_is_updated_when_updated_at_the_source():
    profile = LegacyAccountProfileFactory()
    abonne = AbonneFactory()
    profile.organisation = OrganisationFactory()
    profile.legacy_id = abonne.abonneid
    abonne.courriel = "test@courriel.com"
    profile.save()

    journal = JournalFactory()
    revue1 = RevueFactory.create(titrerevabr=journal.code)
    RevueabonneFactory.create(
        abonneid=abonne.abonneid, revueid=revue1.revueid, anneeabonnement=2018
    )

    subscription_qs = Revueabonne.objects
    command = import_restrictions.Command()
    command.import_restriction_subscriber(abonne, subscription_qs)

    profile = LegacyAccountProfile.objects.first()
    assert profile.user.email == abonne.courriel


@pytest.mark.django_db
def test_import_deletions():
    # Verify that subscription deletions are properly imported, that is, that deletions propagate.
    # Setup
    journal1 = JournalFactory.create()
    abonne1 = AbonneFactory.create()
    revue1 = RevueFactory.create(titrerevabr=journal1.code)
    sub1 = RevueabonneFactory.create(
        abonneid=abonne1.abonneid,
        revueid=revue1.revueid,
        anneeabonnement=datetime.datetime.now().year,
    )

    assert JournalAccessSubscriptionPeriod.objects.count() == 0
    call_command("import_restrictions", *[], **{})
    subscription = JournalAccessSubscription.objects.first()

    assert subscription.journals.count() == 1
    assert subscription.journalaccesssubscriptionperiod_set.count() == 1

    sub1.delete()
    call_command("import_restrictions", *[], **{})

    # Run & check
    assert JournalAccessSubscription.objects.count() == 1
    assert JournalAccessSubscription.objects.first().journals.count() == 0


@pytest.mark.django_db
def test_delete_existing_subscriptions():
    journal = JournalFactory()

    organisation = OrganisationFactory()

    JournalAccessSubscriptionFactory(valid=True, type="individual")

    LegacyAccountProfileFactory(legacy_id=1179, organisation=organisation)

    subscription = JournalAccessSubscriptionFactory(
        organisation=organisation,
        valid=True,
    )
    subscription.journals.add(journal)
    subscription.save()

    call_command("import_restrictions", *[], **{})

    assert subscription.journals.count() == 0


@pytest.mark.django_db
def test_import_deletion_will_not_modify_individual_subscriptions():
    individual_subscription = JournalAccessSubscriptionFactory(valid=True, type="individual")
    assert individual_subscription.journals.count() == 1
    call_command("import_restrictions", *[], **{})
    assert individual_subscription.journals.count() == 1


@pytest.mark.django_db
def test_existing_organisation_is_renamed_properly():

    abonne1 = AbonneFactory.create()
    abonne1.save()
    revue1 = RevueFactory.create(titrerevabr=JournalFactory())

    RevueabonneFactory.create(abonneid=abonne1.abonneid, revueid=revue1.revueid)

    call_command("import_restrictions", *[], **{})
    assert Organisation.objects.filter(name=abonne1.abonne).count() == 1

    abonne1.abonne = "new name"
    abonne1.save()

    call_command("import_restrictions", *[], **{})
    assert Organisation.objects.filter(name=abonne1.abonne).count() == 1


@pytest.mark.django_db
def test_can_skip_subscribers_with_no_email():
    journal = JournalFactory()
    abonne1 = AbonneFactory.create(courriel="")
    abonne1.save()

    IpabonneFactory.create(abonneid=abonne1.pk)
    revue1 = RevueFactory.create(titrerevabr=journal.code)

    RevueabonneFactory.create(abonneid=abonne1.abonneid, revueid=revue1.revueid)

    call_command("import_restrictions", *[], **{"dry_run": False})

    assert LegacyAccountProfile.objects.count() == 0
    assert JournalAccessSubscriptionPeriod.objects.count() == 0


@pytest.mark.django_db
def test_dry_run_mode_does_not_create_anything():
    journal = JournalFactory()
    abonne1 = AbonneFactory.create(referer="http://www.erudit.org/")
    abonne1.save()

    IpabonneFactory.create(abonneid=abonne1.pk)
    revue1 = RevueFactory.create(titrerevabr=journal.code)

    RevueabonneFactory.create(abonneid=abonne1.abonneid, revueid=revue1.revueid)

    call_command("import_restrictions", *[], **{"dry_run": True})

    assert get_user_model().objects.count() == 0
    assert InstitutionReferer.objects.count() == 0
    assert LegacyAccountProfile.objects.count() == 0
    assert JournalAccessSubscriptionPeriod.objects.count() == 0
    assert Organisation.objects.count() == 0
    assert JournalAccessSubscription.objects.count() == 0
    assert InstitutionIPAddressRange.objects.count() == 0
