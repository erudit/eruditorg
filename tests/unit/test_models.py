# -*- coding: utf-8 -*-

import datetime as dt
import io
import unittest.mock

from django.conf import settings
from eruditarticle.objects import EruditJournal
from eruditarticle.objects import EruditPublication

from erudit.fedora.objects import JournalDigitalObject
from erudit.fedora.objects import PublicationDigitalObject
from erudit.test import BaseEruditTestCase
from erudit.test.factories import ArticleFactory
from erudit.test.factories import ArticleTitleFactory
from erudit.test.factories import AuthorFactory
from erudit.test.factories import IssueFactory
from erudit.test.factories import JournalFactory
from erudit.test.factories import JournalTypeFactory
from erudit.test.factories import CollectionFactory
from erudit.test.factories import IssueContributorFactory
from erudit.test.factories import IssueThemeFactory


class TestJournal(BaseEruditTestCase):
    def test_can_return_the_associated_eulfedora_model(self):
        # Run & check
        self.assertEqual(self.journal.fedora_model, JournalDigitalObject)

    def test_can_return_the_associated_erudit_class(self):
        # Run & check
        self.assertEqual(self.journal.erudit_class, EruditJournal)

    def test_can_return_an_appropriate_fedora_pid(self):
        # Setup
        self.journal.localidentifier = 'dummy139'
        self.journal.save()
        # Run & check
        self.assertEqual(self.journal.pid, 'erudit:erudit.dummy139')

    def test_can_return_its_published_issues(self):
        # Setup
        issue_1 = IssueFactory.create(journal=self.journal, year=2010)
        issue_2 = IssueFactory.create(journal=self.journal, year=2009)
        IssueFactory.create(journal=self.journal, year=dt.datetime.now().year + 2)
        # Run & check
        self.assertEqual(set(self.journal.published_issues), {issue_1, issue_2})

    def test_can_return_its_first_issue(self):
        # Setup
        issue_1 = IssueFactory.create(
            journal=self.journal, year=2010,
            date_published=dt.datetime.now() - dt.timedelta(days=1))
        IssueFactory.create(journal=self.journal, year=2010, date_published=dt.datetime.now())
        IssueFactory.create(
            journal=self.journal, year=dt.datetime.now().year + 2,
            date_published=dt.datetime.now() + dt.timedelta(days=30))
        # Run & check
        self.assertEqual(self.journal.first_issue, issue_1)

    def test_can_return_its_last_issue(self):
        # Setup
        IssueFactory.create(
            journal=self.journal, year=2010,
            date_published=dt.datetime.now() - dt.timedelta(days=1))
        issue_2 = IssueFactory.create(
            journal=self.journal, year=2010, date_published=dt.datetime.now())
        IssueFactory.create(
            journal=self.journal, year=dt.datetime.now().year + 2,
            date_published=dt.datetime.now() + dt.timedelta(days=30))
        # Run & check
        self.assertEqual(self.journal.last_issue, issue_2)

    def test_knows_if_it_is_provided_by_fedora(self):
        # Run & check
        self.journal.localidentifier = 'dummy139'
        self.journal.save()
        self.assertTrue(self.journal.provided_by_fedora)
        self.journal.localidentifier = None
        self.journal.save()
        self.assertFalse(self.journal.provided_by_fedora)

    def test_can_return_its_letter_prefix(self):
        # Setup
        journal_1 = JournalFactory.create(
            name='Test', collection=self.collection, publishers=[self.publisher])
        journal_2 = JournalFactory.create(
            name=None, collection=self.collection, publishers=[self.publisher])
        # Run & check
        self.assertEqual(journal_1.letter_prefix, 'T')
        self.assertIsNone(journal_2.letter_prefix)

    def test_can_return_the_published_open_access_issues(self):
        # Setup
        from erudit.conf.settings import MOVABLE_LIMITATION_SCIENTIFIC_YEAR_OFFSET as ml

        now_dt = dt.datetime.now()
        self.journal.open_access = False
        self.journal.type = JournalTypeFactory.create(code='S')
        self.journal.save()
        IssueFactory.create(
            journal=self.journal, year=now_dt.year - (ml - 1),
            date_published=dt.date(now_dt.year - 3, 3, 20))
        IssueFactory.create(
            journal=self.journal, year=now_dt.year - (ml - 2),
            date_published=dt.date(now_dt.year - 1, 3, 20))
        issue_3 = IssueFactory.create(
            journal=self.journal, year=now_dt.year - (ml + 1),
            date_published=dt.date(now_dt.year - 5, 3, 20))
        # Run & check
        self.assertEqual(list(self.journal.published_open_access_issues), [issue_3, ])

    def test_can_return_the_published_open_access_issues_year_coverage(self):
        # Setup
        from erudit.conf.settings import MOVABLE_LIMITATION_SCIENTIFIC_YEAR_OFFSET as ml
        now_dt = dt.datetime.now()
        self.journal.open_access = False
        self.journal.type = JournalTypeFactory.create(code='S')
        self.journal.save()
        IssueFactory.create(
            journal=self.journal, year=now_dt.year - (ml - 1),
            date_published=dt.date(now_dt.year - 3, 3, 20))
        IssueFactory.create(
            journal=self.journal, year=now_dt.year - (ml - 3),
            date_published=dt.date(now_dt.year - 1, 3, 20))
        issue_3 = IssueFactory.create(
            journal=self.journal, year=now_dt.year - (ml + 1),
            date_published=dt.date(now_dt.year - 5, 3, 20))
        issue_4 = IssueFactory.create(
            journal=self.journal, year=now_dt.year - (ml + 2),
            date_published=dt.date(now_dt.year - 5, 3, 20))
        # Run & check
        self.assertEqual(
            self.journal.published_open_access_issues_year_coverage,
            {'from': issue_4.year, 'to': issue_3.year})

    def test_knows_its_directors(self):
        now_dt = dt.datetime.now()
        first_issue = IssueFactory.create(
            journal=self.journal, date_published=now_dt - dt.timedelta(days=1)
        )

        first_issue_director = IssueContributorFactory(
            issue=first_issue, is_director=True
        )

        last_issue = IssueFactory.create(journal=self.journal, date_published=now_dt)
        last_issue_director = IssueContributorFactory(issue=last_issue, is_director=True)

        assert last_issue_director in self.journal.get_directors()
        assert first_issue_director not in self.journal.get_directors()

    def test_knows_its_editors(self):
        now_dt = dt.datetime.now()
        first_issue = IssueFactory.create(
            journal=self.journal, date_published=now_dt - dt.timedelta(days=1)
        )
        first_issue_editor = IssueContributorFactory(issue=first_issue, is_editor=True)

        last_issue = IssueFactory.create(journal=self.journal, date_published=now_dt)
        last_issue_editor = IssueContributorFactory(issue=last_issue, is_editor=True)

        assert last_issue_editor in self.journal.get_editors()
        assert first_issue_editor not in self.journal.get_editors()


class TestIssue(BaseEruditTestCase):
    def setUp(self):
        super(TestIssue, self).setUp()
        self.issue = IssueFactory.create(journal=self.journal)

    def test_can_return_the_associated_eulfedora_model(self):
        # Run & check
        self.assertEqual(self.issue.fedora_model, PublicationDigitalObject)

    def test_can_return_the_associated_erudit_class(self):
        # Run & check
        self.assertEqual(self.issue.erudit_class, EruditPublication)

    def test_can_return_its_full_identifier(self):
        # Setup
        self.journal.localidentifier = 'dummy139'
        self.journal.save()
        self.issue.localidentifier = 'dummy1234'
        self.issue.save()
        # Run & check
        self.assertEqual(self.issue.get_full_identifier(), 'erudit:erudit.dummy139.dummy1234')

    def test_issue_has_no_full_identifier_if_a_part_is_missing(self):
        self.journal.localidentifier = "dummy139"
        self.journal.save()
        self.issue.localidentifier = None
        self.issue.save()

        assert self.issue.get_full_identifier() is None

    def test_can_return_an_appropriate_fedora_pid(self):
        # Setup
        self.journal.localidentifier = 'dummy139'
        self.journal.save()
        self.issue.localidentifier = 'dummy1234'
        self.issue.save()
        # Run & check
        self.assertEqual(self.issue.pid, 'erudit:erudit.dummy139.dummy1234')

    def test_knows_if_it_has_a_movable_limitation_in_case_of_scientific_journals(self):
        # Setup
        from erudit.conf.settings import MOVABLE_LIMITATION_SCIENTIFIC_YEAR_OFFSET as ml

        now_dt = dt.datetime.now()
        self.journal.open_access = False
        self.journal.type = JournalTypeFactory.create(code='S')
        self.journal.save()
        issue_1 = IssueFactory.create(
            journal=self.journal, year=now_dt.year - (ml - 1),
            date_published=dt.date(now_dt.year - (ml - 1), 3, 20))
        issue_2 = IssueFactory.create(
            journal=self.journal, year=now_dt.year - (ml - 2),
            date_published=dt.date(now_dt.year - (ml - 2), 3, 20))
        issue_3 = IssueFactory.create(
            journal=self.journal, year=now_dt.year - (ml + 2),
            date_published=dt.date(now_dt.year - (ml + 2), 3, 20))
        # Run & check
        self.assertTrue(issue_1.has_movable_limitation)
        self.assertTrue(issue_2.has_movable_limitation)
        self.assertFalse(issue_3.has_movable_limitation)

    def test_knows_if_it_has_a_movable_limitation_in_case_of_non_scientific_journals(self):
        # Setup
        from erudit.conf.settings import MOVABLE_LIMITATION_CULTURAL_YEAR_OFFSET as ml

        now_dt = dt.datetime.now()
        self.journal.open_access = False
        self.journal.type = JournalTypeFactory.create(code='C')
        self.journal.save()
        issue_1 = IssueFactory.create(
            journal=self.journal, year=now_dt.year - (ml + 1),
            date_published=dt.date(now_dt.year - (ml + 1), 3, 20))
        issue_2 = IssueFactory.create(
            journal=self.journal, year=now_dt.year - (ml - 1),
            date_published=dt.date(now_dt.year - (ml - 1), 3, 20))
        issue_3 = IssueFactory.create(
            journal=self.journal, year=now_dt.year - (ml + 2),
            date_published=dt.date(now_dt.year - (ml + 2), 3, 20))
        # Run & check
        self.assertFalse(issue_1.has_movable_limitation)
        self.assertTrue(issue_2.has_movable_limitation)
        self.assertFalse(issue_3.has_movable_limitation)

    def test_issues_with_a_next_year_published_date_have_movable_limitation(self):
        now_dt = dt.datetime.now()
        issue = IssueFactory.create(
            journal=self.journal,
            year=now_dt.year + 1, date_published=dt.date(now_dt.year + 1, 1, 1)
        )
        assert issue.has_movable_limitation is True

    def test_knows_that_issues_with_open_access_has_no_movable_limitation(self):
        # Setup
        now_dt = dt.datetime.now()
        j2 = JournalFactory.create(open_access=False)
        self.journal.open_access = True
        self.journal.type = JournalTypeFactory.create(code='C')
        self.journal.save()
        issue_1 = IssueFactory.create(
            journal=self.journal, year=now_dt.year - 3,
            date_published=dt.date(now_dt.year - 3, 3, 20))
        issue_2 = IssueFactory.create(
            journal=self.journal, year=now_dt.year - 1,
            date_published=dt.date(now_dt.year - 1, 3, 20))
        issue_3 = IssueFactory.create(
            journal=j2, year=now_dt.year - 5,
            date_published=dt.date(now_dt.year - 5, 3, 20))
        # Run & check
        self.assertFalse(issue_1.has_movable_limitation)
        self.assertFalse(issue_2.has_movable_limitation)
        self.assertFalse(issue_3.has_movable_limitation)

    def test_knows_if_it_has_a_coverpage(self):
        # Setup
        self.journal.open_access = True
        self.journal.save()
        with open(settings.MEDIA_ROOT + '/coverpage.png', 'rb') as f:
            issue_1 = IssueFactory.create(journal=self.journal)
            issue_2 = IssueFactory.create(journal=self.journal)
            issue_1.fedora_object = unittest.mock.MagicMock()
            issue_1.fedora_object.coverpage = unittest.mock.MagicMock()
            issue_1.fedora_object.coverpage.content = io.BytesIO(f.read())
            issue_2.fedora_object = unittest.mock.MagicMock()
            issue_2.fedora_object.coverpage = unittest.mock.MagicMock()
            issue_2.fedora_object.coverpage.content = ''

        # Run & check
        self.assertTrue(issue_1.has_coverpage)
        self.assertFalse(issue_2.has_coverpage)

    def test_knows_that_an_issue_with_an_empty_coverpage_has_no_coverpage(self):
        # Setup
        self.journal.open_access = True
        self.journal.save()
        with open(settings.MEDIA_ROOT + '/coverpage_empty.png', 'rb') as f:
            issue = IssueFactory.create(journal=self.journal)
            issue.fedora_object = unittest.mock.MagicMock()
            issue.fedora_object.coverpage = unittest.mock.MagicMock()
            issue.fedora_object.coverpage.content = io.BytesIO(f.read())

        # Run & check
        self.assertFalse(issue.has_coverpage)

    def test_can_return_a_slug_that_can_be_used_in_urls(self):
        # Setup
        issue_1 = IssueFactory.create(
            year=2015, volume='4', number='1', localidentifier='i1')
        issue_2 = IssueFactory.create(
            year=2015, volume='4', number=None, localidentifier='i2')
        issue_3 = IssueFactory.create(
            year=2015, volume=None, number='2', localidentifier='i3')
        issue_4 = IssueFactory.create(
            year=2015, volume='2-3', number='39', localidentifier='i4')
        issue_5 = IssueFactory.create(
            year=2015, volume=None, number=None, localidentifier='i5')
        issue_6 = IssueFactory.create(
            year=2015, volume='2 bis', number='39', localidentifier='i6')
        # Run & check
        self.assertEqual(issue_1.volume_slug, '2015-v4-n1')
        self.assertEqual(issue_2.volume_slug, '2015-v4')
        self.assertEqual(issue_3.volume_slug, '2015-n2')
        self.assertEqual(issue_4.volume_slug, '2015-v2-3-n39')
        self.assertEqual(issue_5.volume_slug, '2015')
        self.assertEqual(issue_6.volume_slug, '2015-v2-bis-n39')

    def test_knows_its_directors(self):
        contributor = IssueContributorFactory(issue=self.issue, is_director=True)
        assert contributor in self.issue.get_directors()

    def test_knows_its_editors(self):
        contributor = IssueContributorFactory(issue=self.issue, is_editor=True)
        assert contributor in self.issue.get_editors()

    def test_can_return_its_name_with_themes(self):
        theme1 = IssueThemeFactory(issue=self.issue)
        assert self.issue.name_with_themes == "{html_name}: {html_subname}".format(
            html_name=theme1.html_name, html_subname=theme1.html_subname
        )

        theme2 = IssueThemeFactory(issue=self.issue)
        assert self.issue.name_with_themes == "{html_name}: {html_subname} / {html_name2}: {html_subname2}".format(  # noqa
            html_name=theme1.html_name, html_subname=theme1.html_subname,
            html_name2=theme2.html_name, html_subname2=theme2.html_subname,
        )


class TestIssueContributor(BaseEruditTestCase):

    def test_can_format_its_name(self):
        contributor = IssueContributorFactory(
            firstname="Tryphon",
            lastname=None,
            role_name=None
        )

        assert contributor.format_name() == "Tryphon"

        contributor = IssueContributorFactory(
            firstname="Tryphon",
            lastname="Tournesol",
            role_name=None
        )

        assert contributor.format_name() == "Tryphon Tournesol"

        contributor = IssueContributorFactory(
            firstname="Tryphon",
            lastname="Tournesol",
            role_name="Professeur"
        )

        assert contributor.format_name() == "Tryphon Tournesol (Professeur)"


class TestArticle(BaseEruditTestCase):

    def setUp(self):
        super(TestArticle, self).setUp()
        self.issue = IssueFactory.create(journal=self.journal)
        self.article = ArticleFactory.create(issue=self.issue)

    def test_only_has_fedora_object_if_collection_has_localidentifier(self):
        c1 = CollectionFactory.create(localidentifier=None)
        j1 = JournalFactory.create(collection=c1)
        issue_1 = IssueFactory.create(journal=j1)
        article_1 = ArticleFactory.create(issue=issue_1)
        assert article_1.fedora_object is None

    def test_only_has_full_identifier_if_complete(self):
        c1 = CollectionFactory.create(localidentifier=None)

        j1 = JournalFactory.create(collection=c1, localidentifier=None)
        i1 = IssueFactory.create(journal=j1)
        article_1 = ArticleFactory.create(issue=i1)

        assert article_1.get_full_identifier() is None

        i1.localidentifier = 'issue1'
        i1.save()
        assert article_1.get_full_identifier() is None

        j1.localidentifier = 'journal1'
        j1.save()
        assert article_1.get_full_identifier() is None

        c1.localidentifier = 'c1'
        c1.save()
        assert article_1.get_full_identifier() is not None

    def test_knows_that_it_is_in_open_access_if_its_issue_is_in_open_access(self):
        # Setup
        j1 = JournalFactory.create(open_access=True)
        j2 = JournalFactory.create(open_access=False)
        issue_1 = IssueFactory.create(journal=j1)
        article_1 = ArticleFactory.create(issue=issue_1)
        issue_2 = IssueFactory.create(journal=j2)
        article_2 = ArticleFactory.create(issue=issue_2)
        # Run 1 check
        self.assertTrue(article_1.open_access)
        self.assertFalse(article_2.open_access)

    def test_knows_if_it_is_in_open_access_if_its_journal_is_in_open_access(self):
        # Setup
        self.journal.open_access = True
        self.journal.save()
        j2 = JournalFactory.create(open_access=False)
        issue_1 = IssueFactory.create(journal=self.journal)
        article_1 = ArticleFactory.create(issue=issue_1)
        issue_2 = IssueFactory.create(journal=j2)
        article_2 = ArticleFactory.create(issue=issue_2)
        # Run 1 check
        self.assertTrue(article_1.open_access)
        self.assertFalse(article_2.open_access)

    def test_knows_if_it_has_a_movable_limitation(self):
        # Setup
        now_dt = dt.datetime.now()
        from erudit.conf.settings import MOVABLE_LIMITATION_SCIENTIFIC_YEAR_OFFSET as ml
        self.journal.open_access = False
        self.journal.type = JournalTypeFactory.create(code='S')
        self.journal.save()
        issue_1 = IssueFactory.create(
            journal=self.journal, year=now_dt.year - (ml - 1),
            date_published=dt.date(now_dt.year - (ml - 1), 3, 20))
        issue_2 = IssueFactory.create(
            journal=self.journal, year=now_dt.year - (ml - 2),
            date_published=dt.date(now_dt.year - (ml - 2), 3, 20))
        issue_3 = IssueFactory.create(
            journal=self.journal, year=now_dt.year - (ml + 1),
            date_published=dt.date(now_dt.year - (ml + 1), 3, 20))
        article_1 = ArticleFactory.create(issue=issue_1)
        article_2 = ArticleFactory.create(issue=issue_2)
        article_3 = ArticleFactory.create(issue=issue_3)
        # Run & check
        self.assertTrue(article_1.has_movable_limitation)
        self.assertTrue(article_2.has_movable_limitation)
        self.assertFalse(article_3.has_movable_limitation)

    def test_can_return_its_title(self):
        article = ArticleFactory()
        article_title = ArticleTitleFactory(article=article)
        assert article.title == article_title.title


class TestAuthor(BaseEruditTestCase):
    def test_can_return_articles_written_for_a_given_journal(self):
        # Setup
        other_journal = JournalFactory.create(
            publishers=[self.publisher])
        other_issue = IssueFactory.create(
            journal=other_journal, date_published=dt.datetime.now())
        other_article = ArticleFactory.create(issue=other_issue)

        issue = IssueFactory.create(
            journal=self.journal, date_published=dt.datetime.now())
        article = ArticleFactory.create(issue=issue)

        author = AuthorFactory.create()

        article.authors.add(author)
        other_article.authors.add(author)

        # Run
        self.assertEqual(list(author.articles_in_journal(self.journal)), [article, ])

    def test_can_return_its_letter_prefix(self):
        # Setup
        author_1 = AuthorFactory.create(lastname='Abc', firstname='Def')
        author_2 = AuthorFactory.create(lastname=None, firstname='Def')
        author_3 = AuthorFactory.create(lastname=None, firstname='Def', othername='Ghi')
        # Run & check
        self.assertEqual(author_1.letter_prefix, 'A')
        self.assertEqual(author_2.letter_prefix, 'D')
        self.assertEqual(author_3.letter_prefix, 'G')

    def test_can_return_its_name(self):
        author_1 = AuthorFactory()

        assert str(author_1) == "{lastname}, {firstname}".format(
            lastname=author_1.lastname, firstname=author_1.firstname
        )

        author_1.suffix = 'PhD'

        assert str(author_1) == "{suffix} {firstname} {lastname}".format(
            suffix=author_1.suffix, firstname=author_1.firstname, lastname=author_1.lastname
        )
