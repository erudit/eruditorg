import factory

from erudit.factories import OrganisationFactory


class PolicyFactory(factory.django.DjangoModelFactory):

    class Meta:
        model = 'individual_subscription.Policy'

    organization = factory.SubFactory(OrganisationFactory)
    max_accounts = 10


class IndividualAccountFactory(factory.django.DjangoModelFactory):

    class Meta:
        model = 'individual_subscription.IndividualAccount'

    firstname = factory.Sequence(lambda n: 'prenom{}'.format(n))
    lastname = factory.Sequence(lambda n: 'nom{}'.format(n))
    policy = factory.SubFactory(PolicyFactory)
