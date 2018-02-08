import pytest

from erudit.test.factories import JournalFactory, LegacyOrganisationProfileFactory

from core.accounts.models import LegacyAccountProfile
from core.subscription.models import JournalAccessSubscription, Organisation
from core.subscription.restriction.models import Revueabonne
from core.subscription.restriction.test.factories import (
    AbonneFactory, RevueFactory, RevueabonneFactory
)
from core.subscription.management.commands import import_restrictions


@pytest.mark.django_db
def test_import_subscriber():
    # Verify that we properly import subscriber information
    # Setup
    abonne1 = AbonneFactory.create()

    subscription_qs = Revueabonne.objects
    import_restrictions.import_restriction_subscriber(abonne1, subscription_qs)

    # Run & check
    accprofile = LegacyAccountProfile.objects.get(legacy_id=abonne1.abonneid)
    org = accprofile.organisation
    orgprofile = org.legacyorganisationprofile
    assert org.name == abonne1.abonne
    assert orgprofile.account_id == str(abonne1.abonneid)
    assert orgprofile.sushi_requester_id == abonne1.requesterid
    assert accprofile.user.username == 'restriction-{}'.format(abonne1.abonneid)
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
        abonneid=abonne1.abonneid,
        revueid=revue1.revueid,
        anneeabonnement=2018)

    subscription_qs = Revueabonne.objects
    import_restrictions.import_restriction_subscriber(abonne1, subscription_qs)

    # Run & check
    assert JournalAccessSubscription.objects.count() == 1
    sub = JournalAccessSubscription.objects.first()
    assert sub.get_subscription_type() == JournalAccessSubscription.TYPE_INSTITUTIONAL
    assert sub.journals.filter(pk=journal1.pk).exists()
    assert sub.organisation.name == abonne1.abonne

@pytest.mark.django_db
def test_assign_user_to_existing_organisation():
    """ If an organisation has the LegacyOrganisationId of the restriction user to import,
    add the created user to this organisation"""
    profile = LegacyOrganisationProfileFactory()
    journal1 = JournalFactory.create()
    abonne1 = AbonneFactory.create()
    abonne1.abonneid = profile.account_id
    revue1 = RevueFactory.create(titrerevabr=journal1.code)
    sub1 = RevueabonneFactory.create(
        abonneid=abonne1.abonneid,
        revueid=revue1.revueid,
        anneeabonnement=2018)

    subscription_qs = Revueabonne.objects
    import_restrictions.import_restriction_subscriber(abonne1, subscription_qs)

    # test that no new organisation has been created
    assert Organisation.objects.count() == 1
    assert Organisation.objects.first().members.count() == 1

@pytest.mark.django_db
def test_import_can_rename_organisation():
    profile = LegacyOrganisationProfileFactory()
    profile.organisation.name = "old name"
    profile.organisation.save()
    journal1 = JournalFactory.create()
    abonne1 = AbonneFactory.create()
    abonne1.abonne = "new name"
    abonne1.abonneid = profile.account_id

    revue1 = RevueFactory.create(titrerevabr=journal1.code)
    sub1 = RevueabonneFactory.create(
        abonneid=abonne1.abonneid,
        revueid=revue1.revueid,
        anneeabonnement=2018)

    subscription_qs = Revueabonne.objects
    import_restrictions.import_restriction_subscriber(abonne1, subscription_qs)

    assert Organisation.objects.count() == 1
    organisation = Organisation.objects.first()
    assert organisation.name == "new name"

@pytest.mark.django_db
def test_import_deletions():
    # Verify that subscription deletions are properly imported, that is, that deletions propagate.
    # Setup
    legacy_organisation_profile = LegacyOrganisationProfileFactory()
    journal1 = JournalFactory.create()
    abonne1 = AbonneFactory.create()
    revue1 = RevueFactory.create(titrerevabr=journal1.code)
    sub1 = RevueabonneFactory.create(
        abonneid=abonne1.abonneid,
        revueid=revue1.revueid,
        anneeabonnement=2018)

    subscription_qs = Revueabonne.objects
    import_restrictions.import_restriction_subscriber(abonne1, subscription_qs)
    sub1.delete()
    import_restrictions.import_restriction_subscriber(abonne1, subscription_qs)

    # Run & check
    assert JournalAccessSubscription.objects.count() == 1
    assert JournalAccessSubscription.objects.first().journals.count() == 0
