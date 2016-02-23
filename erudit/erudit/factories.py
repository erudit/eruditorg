import factory
from faker import Factory

faker = Factory.create()


class OrganisationFactory(factory.django.DjangoModelFactory):

    class Meta:
        model = 'erudit.Organisation'

    name = factory.Sequence(lambda n: 'organization{}'.format(n))


class PublisherFactory(factory.django.DjangoModelFactory):

    class Meta:
        model = 'erudit.Publisher'


class CollectionFactory(factory.django.DjangoModelFactory):
    code = factory.Sequence(lambda n: 'journal-{}'.format(n))
    name = factory.Sequence(lambda n: 'Revue{}'.format(n))

    class Meta:
        model = 'erudit.Collection'


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


class ArticleFactory(factory.django.DjangoModelFactory):

    class Meta:
        model = 'erudit.article'

    issue = factory.SubFactory(IssueFactory)
    localidentifier = factory.Sequence(lambda n: 'article-{}'.format(n))


class BasketFactory(factory.django.DjangoModelFactory):

    class Meta:
        model = 'erudit.Basket'

    name = factory.Sequence(lambda n: 'Basket{}'.format(n))


class AuthorFactory(factory.django.DjangoModelFactory):
    lastname = faker.last_name()
    firstname = faker.first_name()

    class Meta:
        model = 'erudit.Author'
