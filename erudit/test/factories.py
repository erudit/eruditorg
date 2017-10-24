# -*- coding: utf-8 -*-
import datetime as dt

import factory
from faker import Factory

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

    collection = factory.SubFactory(CollectionFactory)
    code = factory.Sequence(lambda n: 'journal-{}'.format(n))
    name = factory.Sequence(lambda n: 'Revue{}'.format(n))
    localidentifier = factory.Sequence(lambda n: 'journal{}'.format(n))
    redirect_to_external_url = False
    last_publication_year = dt.datetime.now().year

    class Meta:
        model = 'erudit.journal'

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
    def use_fedora(self, create, extracted, **kwargs):
        if not create:
            return
        if extracted is False:
            self.erudit_object = None


class JournalTypeFactory(factory.django.DjangoModelFactory):

    name = factory.Sequence(lambda n: "JournalType-{}".format(n))

    class Meta:
        model = 'erudit.JournalType'


class JournalInformationFactory(factory.django.DjangoModelFactory):

    journal = factory.SubFactory(JournalFactory)

    class Meta:
        model = 'erudit.journalinformation'


class IssueFactory(factory.django.DjangoModelFactory):

    journal = factory.SubFactory(JournalFactory)
    localidentifier = factory.Sequence(lambda n: 'issue{}'.format(n))
    date_published = dt.datetime.now().date()
    year = dt.datetime.now().year
    is_published = True

    class Meta:
        model = 'erudit.issue'


class EmbargoedIssueFactory(IssueFactory):

    date_published = dt.datetime.now().date()
    year = date_published.year


class NonEmbargoedIssueFactory(IssueFactory):

    date_published = dt.datetime.now().date()
    year = date_published.year - 5


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


class OpenAccessArticleFactory(ArticleFactory):
    issue = factory.SubFactory(
        IssueFactory,
        journal=factory.SubFactory(
            JournalFactory,
            open_access=True
        )
    )


class EmbargoedArticleFactory(ArticleFactory):

    issue = factory.SubFactory(
        EmbargoedIssueFactory,
        journal=factory.SubFactory(
            JournalFactory,
            collection=factory.SubFactory(
                CollectionFactory,
                code='erudit',
            )
        )
    )


class NonEmbargoedArticleFactory(ArticleFactory):

    issue = factory.SubFactory(NonEmbargoedIssueFactory)


class ArticleTitleFactory(factory.django.DjangoModelFactory):

    article = factory.SubFactory(ArticleFactory)
    title = factory.Sequence(lambda n: 'Article {}'.format(n))
    paral = False

    class Meta:
        model = 'erudit.ArticleTitle'


class ArticleSectionTitleFactory(factory.django.DjangoModelFactory):

    article = factory.SubFactory(ArticleFactory)
    title = factory.sequence(lambda n: "Section {}".format(n))
    paral = False

    class Meta:
        model = 'erudit.ArticleSectionTitle'


class AuthorFactory(factory.django.DjangoModelFactory):
    lastname = faker.last_name()
    firstname = faker.first_name()

    class Meta:
        model = 'erudit.Author'


class ThesisFactory(factory.django.DjangoModelFactory):
    collection = factory.SubFactory(CollectionFactory)
    author = factory.SubFactory(AuthorFactory)
    title = factory.Sequence(lambda n: 'Thèse {}'.format(n))
    url = faker.url()
    publication_year = faker.year()
    localidentifier = factory.Sequence(lambda n: 'thesis-{}'.format(n))

    class Meta:
        model = 'erudit.Thesis'
