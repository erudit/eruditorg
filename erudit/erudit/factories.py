import factory


class OrganisationFactory(factory.django.DjangoModelFactory):

    class Meta:
        model = 'erudit.Organisation'

    name = factory.Sequence(lambda n: 'organization{}'.format(n))


class PublisherFactory(factory.django.DjangoModelFactory):

    class Meta:
        model = 'erudit.Publisher'


class JournalFactory(factory.django.DjangoModelFactory):

    class Meta:
        model = 'erudit.journal'

    code = factory.Sequence(lambda n: 'journal-{}'.format(n))
    name = factory.Sequence(lambda n: 'Revue{}'.format(n))

    @factory.post_generation
    def publishers(self, create, extracted, **kwargs):
        if not create:
            # Simple build, do nothing.
            return

        if extracted:
            # A list of groups were passed in, use them
            for group in extracted:
                self.publishers.add(group)


class JournalInformationFactory(factory.django.DjangoModelFactory):
    journal = factory.SubFactory(JournalFactory)

    class Meta:
        model = 'erudit.journalinformation'


class IssueFactory(factory.django.DjangoModelFactory):

    class Meta:
        model = 'erudit.issue'

    journal = factory.SubFactory(JournalFactory)
    localidentifier = factory.Sequence(lambda n: 'issue-{}'.format(n))


class BasketFactory(factory.django.DjangoModelFactory):

    class Meta:
        model = 'subscription.Basket'

    name = factory.Sequence(lambda n: 'Basket{}'.format(n))
