import datetime as dt

import factory
from faker import Factory

from ..fedora import repository
from ..models import JournalType

faker = Factory.create()


class OrganisationFactory(factory.django.DjangoModelFactory):

    name = factory.Sequence(lambda n: 'organization{}'.format(n))

    class Meta:
        model = 'erudit.Organisation'


class PublisherFactory(factory.django.DjangoModelFactory):

    class Meta:
        model = 'erudit.Publisher'


class CollectionFactory(factory.django.DjangoModelFactory):
    code = factory.Sequence(lambda n: 'col-{}'.format(n))
    name = factory.Sequence(lambda n: 'Col{}'.format(n))
    localidentifier = factory.Sequence(lambda n: 'col-{}'.format(n))

    class Meta:
        model = 'erudit.Collection'
        django_get_or_create = ('code',)


class DisciplineFactory(factory.django.DjangoModelFactory):
    code = factory.Sequence(lambda n: 'discipline-{}'.format(n))
    name = factory.Sequence(lambda n: 'Discipline{}'.format(n))

    class Meta:
        model = 'erudit.Discipline'


class JournalFactory(factory.django.DjangoModelFactory):

    @classmethod
    def create_with_issue(cls, *args, **kwargs):
        instance = cls(*args, **kwargs)
        IssueFactory(journal=instance)
        return instance

    collection = factory.SubFactory(CollectionFactory, code='erudit')
    type = factory.LazyAttribute(lambda o: JournalTypeFactory(code=o.type_code))
    code = factory.Sequence(lambda n: 'journal-{}'.format(n))
    name = factory.Sequence(lambda n: 'Revue{}'.format(n))
    localidentifier = factory.Sequence(lambda n: 'journal{}'.format(n))
    redirect_to_external_url = False
    last_publication_year = dt.datetime.now().year

    class Meta:
        model = 'erudit.journal'

    class Params:
        type_code = JournalType.CODE_SCIENTIFIC

    @factory.post_generation
    def publishers(self, create, extracted, **kwargs):
        if not create:
            # Simple build, do nothing.
            return

        if extracted:
            # A list of publishers were passed in, use them
            for publisher in extracted:
                self.publishers.add(publisher)

    @factory.post_generation
    def members(self, create, extracted, **kwargs):
        if not create:
            return

        if extracted:
            for member in extracted:
                self.members.add(member)


class JournalTypeFactory(factory.django.DjangoModelFactory):

    name = factory.LazyAttribute(lambda o: "JournalType-{}".format(o.code))
    code = JournalType.CODE_SCIENTIFIC

    class Meta:
        model = 'erudit.JournalType'
        django_get_or_create = ('code', )


class JournalInformationFactory(factory.django.DjangoModelFactory):

    journal = factory.SubFactory(JournalFactory)

    class Meta:
        model = 'erudit.journalinformation'


class IssueFactory(factory.django.DjangoModelFactory):

    @classmethod
    def create_published_after(cls, other_issue, *args, **kwargs):
        """ Creates an issue with a publish date one day after `other_issue`, in the same journal.
        """
        kwargs['journal'] = other_issue.journal
        kwargs['date_published'] = other_issue.date_published + dt.timedelta(days=1)
        return cls(*args, **kwargs)

    journal = factory.SubFactory(JournalFactory)
    localidentifier = factory.Sequence(lambda n: 'issue{}'.format(n))
    date_published = dt.datetime.now().date()
    formatted_volume_title = factory.Sequence(lambda n: "number-{}".format(n))
    year = dt.datetime.now().year
    is_published = True

    class Meta:
        model = 'erudit.issue'


class EmbargoedIssueFactory(IssueFactory):

    date_published = dt.datetime.now().date()
    year = date_published.year
    journal = factory.SubFactory(
        JournalFactory,
        collection=factory.SubFactory(
            CollectionFactory,
            code='erudit',
        )
    )


class NonEmbargoedIssueFactory(IssueFactory):

    date_published = dt.datetime.now().date()
    year = date_published.year - 5
    journal = factory.SubFactory(
        JournalFactory,
        collection=factory.SubFactory(
            CollectionFactory,
            code='not-erudit',
        )
    )


class IssueContributorFactory(factory.django.DjangoModelFactory):

    issue = factory.SubFactory(IssueFactory)
    lastname = faker.last_name()
    firstname = faker.first_name()
    role_name = faker.prefix()

    class Meta:
        model = 'erudit.IssueContributor'


class IssueThemeFactory(factory.django.DjangoModelFactory):

    issue = factory.SubFactory(IssueFactory)

    name = factory.Sequence(lambda n: 'Theme-{}'.format(n))
    subname = factory.Sequence(lambda n: 'Theme-subname{}'.format(n))
    html_name = factory.Sequence(lambda n: 'Theme-htmlname-{}'.format(n))
    html_subname = factory.Sequence(lambda n: 'Theme-htmlsubname{}'.format(n))

    class Meta:
        model = 'erudit.IssueTheme'


class ArticleFactory(factory.django.DjangoModelFactory):

    issue = factory.SubFactory(IssueFactory)
    localidentifier = factory.Sequence(lambda n: 'article{}'.format(n))
    type = 'article'
    ordseq = 0

    class Meta:
        model = 'erudit.article'

    @factory.post_generation
    def title(obj, create, extracted, **kwargs):
        # This will be a challenge to properly implement with fedora stubs, but for now let's just
        # hack the thing and do whatever is simpler to ensure that article.title will return the
        # value we specify
        if extracted:
            obj.formatted_title = extracted
            obj.save()

    @factory.post_generation
    def post(obj, create, extracted, **kwargs):
        # we always register non-null localidentifiers with our fake API server.
        if obj.localidentifier:
            repository.api.register_article(obj.get_full_identifier())


class OpenAccessArticleFactory(ArticleFactory):
    issue = factory.SubFactory(
        IssueFactory,
        journal=factory.SubFactory(
            JournalFactory,
            open_access=True
        )
    )


class EmbargoedArticleFactory(ArticleFactory):
    issue = factory.SubFactory(EmbargoedIssueFactory)


class NonEmbargoedArticleFactory(ArticleFactory):
    issue = factory.SubFactory(NonEmbargoedIssueFactory)


class AuthorFactory(factory.django.DjangoModelFactory):
    lastname = faker.last_name()
    firstname = faker.first_name()

    class Meta:
        model = 'erudit.Author'


class LegacyOrganisationProfileFactory(factory.django.DjangoModelFactory):
    organisation = factory.SubFactory(OrganisationFactory)
    account_id = factory.sequence(lambda n: n)

    class Meta:
        model = 'erudit.LegacyOrganisationProfile'


class ThesisFactory(factory.django.DjangoModelFactory):
    collection = factory.SubFactory(CollectionFactory)
    author = factory.SubFactory(AuthorFactory)
    title = factory.Sequence(lambda n: 'Thèse {}'.format(n))
    url = faker.url()
    publication_year = faker.year()
    localidentifier = factory.Sequence(lambda n: 'thesis-{}'.format(n))

    class Meta:
        model = 'erudit.Thesis'
