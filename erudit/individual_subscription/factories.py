import factory

from erudit.factories import OrganisationFactory


class OrganizationPolicyFactory(factory.django.DjangoModelFactory):

    class Meta:
        model = 'individual_subscription.OrganizationPolicy'

    organization = factory.SubFactory(OrganisationFactory)
    max_accounts = 10


class IndividualAccountFactory(factory.django.DjangoModelFactory):

    class Meta:
        model = 'individual_subscription.IndividualAccount'

    firstname = factory.Sequence(lambda n: 'prenom{}'.format(n))
    lastname = factory.Sequence(lambda n: 'nom{}'.format(n))
    organization_policy = factory.SubFactory(OrganizationPolicyFactory)
