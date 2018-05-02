import datetime as dt

import factory
import pysolr
from faker import Factory

from ..fedora import repository
from ..models import JournalType
from .solr import SolrDocument

faker = Factory.create()


class OrganisationFactory(factory.django.DjangoModelFactory):

    name = factory.Sequence(lambda n: 'organization{}'.format(n))

    class Meta:
        model = 'erudit.Organisation'


class PublisherFactory(factory.django.DjangoModelFactory):

    name = factory.Sequence(lambda n: 'publisher{}'.format(n))

    class Meta:
        model = 'erudit.Publisher'


class CollectionFactory(factory.django.DjangoModelFactory):
    code = factory.Sequence(lambda n: 'col-{}'.format(n))
    name = factory.Sequence(lambda n: 'Col{}'.format(n))
    localidentifier = factory.LazyAttribute(lambda o: o.code)

    class Meta:
        model = 'erudit.Collection'
        django_get_or_create = ('code',)


class DisciplineFactory(factory.django.DjangoModelFactory):
    code = factory.Sequence(lambda n: 'discipline-{}'.format(n))
    name = factory.LazyAttribute(lambda o: o.code)

    class Meta:
        model = 'erudit.Discipline'
        django_get_or_create = ('code', )


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

    @factory.post_generation
    def disciplines(self, create, extracted, **kwargs):
        if not create:
            return

        if extracted:
            for discipline in extracted:
                d = DisciplineFactory(code=discipline)
                self.disciplines.add(d)


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
    year = dt.datetime.now().year
    is_published = True

    class Meta:
        model = 'erudit.issue'

    @factory.post_generation
    def post(obj, create, extracted, **kwargs):
        # we always register non-null localidentifiers with our fake API server.
        if obj.get_full_identifier():
            repository.api.register_publication(obj.get_full_identifier())


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
    def from_fixture(obj, create, extracted, **kwargs):
        # we always register non-null localidentifiers with our fake API server.
        if obj.localidentifier:
            if extracted:
                xml = open('./tests/fixtures/article/{}.xml'.format(extracted)).read()
                repository.api.set_article_xml(obj.pid, xml)
            else:
                repository.api.register_article(obj.pid)

    @factory.post_generation
    def add_to_fedora_issue(obj, create, extracted, **kwargs):
        if obj.localidentifier and (extracted is None or extracted):
            repository.api.add_article_to_parent_publication(obj)

    @factory.post_generation
    def authors(obj, create, extracted, **kwargs):
        if obj.pid and obj.issue.is_published:
            solr_client = pysolr.Solr()
            solr_client.add_article(obj, authors=extracted)


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


class LegacyOrganisationProfileFactory(factory.django.DjangoModelFactory):
    organisation = factory.SubFactory(OrganisationFactory)
    account_id = factory.sequence(lambda n: n)

    class Meta:
        model = 'erudit.LegacyOrganisationProfile'


class ThesisRepositoryFactory(factory.django.DjangoModelFactory):
    code = factory.Sequence(lambda n: 'repository{}'.format(n))
    name = factory.Sequence(lambda n: 'repository{}'.format(n))
    solr_name = factory.LazyAttribute(lambda obj: obj.name)

    class Meta:
        model = 'erudit.ThesisRepository'
        django_get_or_create = ('code',)


class ThesisFactory(factory.Factory):
    id = factory.Sequence(lambda n: 'thesis-{}'.format(n))
    title = factory.Sequence(lambda n: 'Thèse {}'.format(n))
    type = 'Thèses'
    authors = ["{}, {}".format(faker.last_name(), faker.first_name())]
    year = faker.year()
    date_added = factory.LazyFunction(lambda: dt.datetime.now().isoformat())
    repository = factory.SubFactory(ThesisRepositoryFactory, code='default')
    collection = factory.LazyAttribute(lambda obj: obj.repository.solr_name)
    url = faker.url()

    class Meta:
        model = SolrDocument


class SolrDocumentFactory(factory.Factory):
    id = factory.Sequence(lambda n: 'solr_id_{}'.format(n))
    title = factory.Sequence(lambda n: 'title_{}'.format(n))
    type = 'Article'
    authors = []

    class Meta:
        model = SolrDocument
