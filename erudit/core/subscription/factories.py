import factory

from erudit.factories import OrganisationFactory


class PolicyFactory(factory.django.DjangoModelFactory):

    class Meta:
        model = 'subscription.Policy'

    content_object = factory.SubFactory(OrganisationFactory)
    max_accounts = 10


class IndividualAccountFactory(factory.django.DjangoModelFactory):

    class Meta:
        model = 'subscription.IndividualAccount'

    firstname = factory.Sequence(lambda n: 'prenom{}'.format(n))
    lastname = factory.Sequence(lambda n: 'nom{}'.format(n))
    email = factory.Sequence(lambda n: 'mail{}@erudit.test'.format(n))
    policy = factory.SubFactory(PolicyFactory)


class InstitutionalAccountFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = 'subscription.InstitutionalAccount'

    institution = factory.SubFactory(OrganisationFactory)
    policy = factory.SubFactory(PolicyFactory)


class InstitutionIPAddressRangeFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = 'subscription.InstitutionIPAddressRange'

    institutional_account = factory.SubFactory(InstitutionalAccountFactory)
