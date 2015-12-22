import factory


class OrganisationFactory(factory.django.DjangoModelFactory):

    class Meta:
        model = 'erudit.Organisation'

    name = factory.Sequence(lambda n: 'organization{}'.format(n))


class JournalFactory(factory.django.DjangoModelFactory):

    class Meta:
        model = 'erudit.journal'

    name = factory.Sequence(lambda n: 'Revue{}'.format(n))


class BasketFactory(factory.django.DjangoModelFactory):

    class Meta:
        model = 'subscription.Basket'

    name = factory.Sequence(lambda n: 'Basket{}'.format(n))
