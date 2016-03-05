import factory

from core.userspace.factories import UserFactory
from erudit.factories import OrganisationFactory


class PolicyFactory(factory.django.DjangoModelFactory):

    class Meta:
        model = 'subscription.Policy'

    content_object = factory.SubFactory(OrganisationFactory)
    max_accounts = 10


class IndividualAccountProfileFactory(factory.django.DjangoModelFactory):

    class Meta:
        model = 'subscription.IndividualAccountProfile'

    policy = factory.SubFactory(PolicyFactory)
    user = factory.SubFactory(UserFactory)


class InstitutionalAccountFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = 'subscription.InstitutionalAccount'

    institution = factory.SubFactory(OrganisationFactory)
    policy = factory.SubFactory(PolicyFactory)


class InstitutionIPAddressRangeFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = 'subscription.InstitutionIPAddressRange'

    institutional_account = factory.SubFactory(InstitutionalAccountFactory)
