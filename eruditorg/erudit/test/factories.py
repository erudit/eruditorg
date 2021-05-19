import datetime as dt

from dateutil.relativedelta import relativedelta
import factory
import pysolr
from faker import Factory

from ..fedora import repository
from ..models import JournalType, Article
from .solr import SolrDocument
from erudit.conf.settings import SCIENTIFIC_JOURNAL_EMBARGO_IN_MONTHS as months_sc
from erudit.conf.settings import CULTURAL_JOURNAL_EMBARGO_IN_MONTHS as months_cult

faker = Factory.create()


class OrganisationFactory(factory.django.DjangoModelFactory):

    name = factory.Sequence(lambda n: "organization{}".format(n))
    account_id = factory.Sequence(lambda n: n)
    sushi_requester_id = factory.Sequence(lambda n: "organization{}".format(n))

    class Meta:
        model = "erudit.Organisation"


class CollectionFactory(factory.django.DjangoModelFactory):
    code = factory.Sequence(lambda n: "col-{}".format(n))
    name = factory.Sequence(lambda n: "Col{}".format(n))
    localidentifier = factory.LazyAttribute(lambda o: o.code)

    class Meta:
        model = "erudit.Collection"
        django_get_or_create = ("code",)


class DisciplineFactory(factory.django.DjangoModelFactory):
    code = factory.Sequence(lambda n: "discipline-{}".format(n))
    name = factory.LazyAttribute(lambda o: o.code)
    type = factory.LazyAttribute(lambda o: JournalTypeFactory(code=JournalType.CODE_SCIENTIFIC))

    class Meta:
        model = "erudit.Discipline"
        django_get_or_create = ("code",)


class JournalFactory(factory.django.DjangoModelFactory):
    @classmethod
    def create_with_issue(cls, *args, **kwargs):
        instance = cls(*args, **kwargs)
        IssueFactory(journal=instance)
        return instance

    collection = factory.SubFactory(
        CollectionFactory, code="erudit", name="Érudit", is_main_collection=True
    )
    type = factory.LazyAttribute(lambda o: JournalTypeFactory(code=o.type_code))
    code = factory.Sequence(lambda n: "journal-{}".format(n))
    name = factory.Sequence(lambda n: "Revue{}".format(n))
    localidentifier = factory.Sequence(lambda n: "journal{}".format(n))
    redirect_to_external_url = False
    last_publication_year = dt.datetime.now(tz=dt.timezone.utc).year
    fedora_updated = dt.datetime.now(tz=dt.timezone.utc)

    class Meta:
        model = "erudit.journal"

    class Params:
        type_code = JournalType.CODE_SCIENTIFIC

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

    @factory.post_generation
    def post(obj, create, extracted, **kwargs):
        # we always register non-null localidentifiers with our fake API server.
        if obj.localidentifier:
            repository.api.register_pid(obj.pid)

    @factory.post_generation
    def notes(obj, create, extracted, **kwargs):
        if not create:
            return

        if extracted:
            repository.api.add_notes_to_journal(extracted, obj)


class JournalTypeFactory(factory.django.DjangoModelFactory):

    name = factory.LazyAttribute(lambda o: "JournalType-{}".format(o.code))
    code = JournalType.CODE_SCIENTIFIC

    class Meta:
        model = "erudit.JournalType"
        django_get_or_create = ("code",)


class JournalInformationFactory(factory.django.DjangoModelFactory):

    journal = factory.SubFactory(JournalFactory)

    class Meta:
        model = "erudit.journalinformation"


class ContributorFactory(factory.django.DjangoModelFactory):

    journal_information = factory.SubFactory(JournalInformationFactory)

    class Meta:
        model = "erudit.contributor"


class IssueFactory(factory.django.DjangoModelFactory):
    @classmethod
    def create_published_after(cls, other_issue, *args, **kwargs):
        """Creates an issue with a publish date one day after `other_issue`, in the same journal."""
        kwargs["journal"] = other_issue.journal
        kwargs["date_published"] = other_issue.date_published + dt.timedelta(days=1)
        return cls(*args, **kwargs)

    journal = factory.SubFactory(JournalFactory)
    localidentifier = factory.Sequence(lambda n: "issue{}".format(n))
    date_published = dt.datetime.now().date()
    year = dt.datetime.now().year
    is_published = True
    fedora_updated = dt.datetime.now(tz=dt.timezone.utc)
    fedora_created = dt.datetime.now(tz=dt.timezone.utc)

    class Meta:
        model = "erudit.issue"

    @factory.post_generation
    def post(obj, create, extracted, **kwargs):
        # we always register non-null localidentifiers with our fake API server.
        if obj.get_full_identifier():
            repository.api.register_publication(obj.get_full_identifier())

    @factory.post_generation
    def add_to_fedora_journal(obj, create, extracted, **kwargs):
        if obj.localidentifier and (extracted is None or extracted):
            repository.api.add_publication_to_parent_journal(obj)


class EmbargoedIssueFactory(IssueFactory):

    date_published = dt.datetime.now().date()
    year = date_published.year
    journal = factory.SubFactory(JournalFactory)


class NonEmbargoedIssueFactory(IssueFactory):
    date_published = dt.datetime.now().date() - relativedelta(
        years=1 + max(months_cult, months_sc) / 12
    )
    year = date_published.year
    journal = factory.SubFactory(JournalFactory)


class OpenAccessIssueFactory(IssueFactory):
    journal = factory.SubFactory(
        JournalFactory,
        open_access=True,
    )


class ArticleRef(Article):
    """ An article that creates its own solr/fedora references upon instantiation. """

    def __init__(
        self,
        issue,
        localidentifier,
        from_fixture=None,
        title=None,
        type=None,
        section_titles=None,
        publication_allowed=True,
        authors=None,
        add_to_fedora_issue=True,
        with_pdf=False,
        with_pdf_erudit=False,
        pdf_url=None,
        html_url=None,
        solr_attrs=None,
        abstracts=None,
        notegens=None,
    ):
        self.issue = issue
        self.localidentifier = localidentifier
        if self.pid is not None:
            repository.api.register_article(self.pid)
            if from_fixture:
                xml = open("./tests/fixtures/article/{}.xml".format(from_fixture)).read()
                repository.api.set_article_xml(self.pid, xml)
            if any(x is not None for x in (title, section_titles, notegens, abstracts, type)):
                with repository.api.open_article(self.pid) as wrapper:
                    if title is not None:
                        wrapper.set_title(title)
                    if section_titles is not None:
                        wrapper.set_section_titles(section_titles)
                    if notegens is not None:
                        wrapper.set_notegens(notegens)
                    if abstracts is not None:
                        wrapper.set_abstracts(abstracts)
                    if type is not None:
                        wrapper.set_type(type)
            if add_to_fedora_issue:
                repository.api.add_article_to_parent_publication(
                    self,
                    publication_allowed=publication_allowed,
                    pdf_url=pdf_url,
                    html_url=html_url,
                )
            if with_pdf:
                repository.api.add_pdf_to_article(self.pid)
            if with_pdf_erudit:
                repository.api.add_pdf_erudit_to_article(self.pid)
        super().__init__(issue, localidentifier)
        if self.pid is not None and self.issue.is_published:
            solr_client = pysolr.Solr()
            solr_client.add_document(
                SolrDocument.from_article(self, authors=authors, solr_attrs=solr_attrs)
            )


class ArticleFactory(factory.Factory):
    issue = factory.SubFactory(IssueFactory)
    localidentifier = factory.Sequence(lambda n: "article{}".format(n))

    class Meta:
        model = ArticleRef

    @factory.post_generation
    def with_pdf(obj, create, extracted, **kwargs):
        if obj.localidentifier and extracted:
            repository.api.register_article(obj.pid, with_pdf=True)

    @factory.post_generation
    def with_pdf_erudit(obj, create, extracted, **kwargs):
        if obj.localidentifier and extracted:
            repository.api.register_article(obj.pid, with_pdf_erudit=True)


class OpenAccessArticleFactory(ArticleFactory):
    issue = factory.SubFactory(
        IssueFactory, journal=factory.SubFactory(JournalFactory, open_access=True)
    )


class EmbargoedArticleFactory(ArticleFactory):
    issue = factory.SubFactory(EmbargoedIssueFactory)


class NonEmbargoedArticleFactory(ArticleFactory):
    issue = factory.SubFactory(NonEmbargoedIssueFactory)


class ThesisRepositoryFactory(factory.django.DjangoModelFactory):
    code = factory.Sequence(lambda n: "repository{}".format(n))
    name = factory.Sequence(lambda n: "repository{}".format(n))
    solr_name = factory.LazyAttribute(lambda obj: obj.name)

    class Meta:
        model = "erudit.ThesisRepository"
        django_get_or_create = ("code",)


class ThesisFactory(factory.Factory):
    id = factory.Sequence(lambda n: "thesis-{}".format(n))
    title = factory.Sequence(lambda n: "Thèse {}".format(n))
    type = "Thèses"
    authors = ["{}, {}".format(faker.last_name(), faker.first_name())]
    year = faker.year()
    date_added = factory.LazyFunction(lambda: dt.datetime.now().isoformat())
    repository = factory.SubFactory(ThesisRepositoryFactory, code="default")
    collection = factory.LazyAttribute(lambda obj: obj.repository.solr_name)
    url = faker.url()

    class Meta:
        model = SolrDocument


class SolrDocumentFactory(factory.Factory):
    id = factory.Sequence(lambda n: "solr_id_{}".format(n))
    title = factory.Sequence(lambda n: "title_{}".format(n))
    type = "Article"
    authors = []
    journal_code = factory.Sequence(lambda n: "journal_code_{}".format(n))
    issue_localidentifier = factory.Sequence(lambda n: "issue_id_{}".format(n))

    class Meta:
        model = SolrDocument
