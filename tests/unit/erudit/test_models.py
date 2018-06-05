import datetime as dt
import dateutil.relativedelta as dr
import io
import unittest.mock

import pytest
from django.conf import settings
from eruditarticle.objects import EruditJournal
from eruditarticle.objects import EruditPublication

from erudit.models import Issue, Article
from erudit.fedora.objects import JournalDigitalObject
from erudit.fedora.objects import PublicationDigitalObject
from erudit.fedora import repository
from erudit.test.factories import (
    ArticleFactory,
    IssueFactory,
    JournalFactory,
    JournalTypeFactory,
    CollectionFactory,
)


pytestmark = pytest.mark.django_db


class TestJournal:
    def test_can_return_the_associated_eulfedora_model(self):
        journal = JournalFactory()
        assert journal.fedora_model == JournalDigitalObject

    def test_can_return_the_associated_erudit_class(self):
        journal = JournalFactory()
        assert journal.erudit_class == EruditJournal

    def test_can_return_an_appropriate_fedora_pid(self):
        journal = JournalFactory(localidentifier='dummy139')
        assert journal.pid == 'erudit:erudit.dummy139'

    def test_can_return_its_published_issues(self):
        journal = JournalFactory()
        issue_1 = IssueFactory.create(journal=journal, year=2010)
        issue_2 = IssueFactory.create(journal=journal, year=2009)

        # Create an unpublished issue
        IssueFactory.create(
            journal=journal, is_published=False,
            year=dt.datetime.now().year + 2,
        )
        assert set(journal.published_issues) == {issue_1, issue_2}

    def test_can_return_when_date_embargo_begins(self, monkeypatch):
        import erudit.conf.settings
        monkeypatch.setattr(erudit.conf.settings, 'SCIENTIFIC_JOURNAL_EMBARGO_IN_MONTHS', 42)
        journal = JournalFactory(open_access=False)
        EXPECTED = dt.date.today() - dr.relativedelta(months=42)
        assert journal.date_embargo_begins == EXPECTED

    def test_inactive_journal_never_embargoes(self):
        journal = JournalFactory(active=False)
        assert journal.date_embargo_begins is None

    def test_can_return_its_first_issue(self):
        journal = JournalFactory()
        issue_1 = IssueFactory.create(
            journal=journal, year=2010,
            date_published=dt.datetime.now() - dt.timedelta(days=1))
        IssueFactory.create(
            journal=journal, year=2010, date_published=dt.datetime.now())
        IssueFactory.create(
            journal=journal, year=dt.datetime.now().year + 2,
            date_published=dt.datetime.now() + dt.timedelta(days=30))
        assert journal.first_issue == issue_1

    def test_can_return_its_last_issue(self):
        journal = JournalFactory()
        IssueFactory.create(
            journal=journal, year=2010,
            date_published=dt.datetime.now() - dt.timedelta(days=1))
        issue_2 = IssueFactory.create(
            journal=journal, year=2010, date_published=dt.datetime.now())
        IssueFactory.create(
            journal=journal, year=dt.datetime.now().year + 2, is_published=False,
            date_published=dt.datetime.now() + dt.timedelta(days=30))
        assert journal.last_issue == issue_2

    def test_knows_if_it_is_provided_by_fedora(self):
        journal = JournalFactory(localidentifier='dummy139')
        assert journal.provided_by_fedora
        journal = JournalFactory(localidentifier=None)
        assert not journal.provided_by_fedora

    def test_can_return_its_letter_prefix(self):
        journal_1 = JournalFactory.create(name='Test')
        assert journal_1.letter_prefix == 'T'

    def test_can_return_the_published_open_access_issues(self):
        journal = JournalFactory(open_access=False)
        embargo_date = journal.date_embargo_begins
        # inside embargo date, not published
        issue_1 = IssueFactory.create(  # noqa
            journal=journal, is_published=True, date_published=embargo_date)
        # after embargo date, published
        issue_2 = IssueFactory.create(
            journal=journal, is_published=True,
            date_published=embargo_date - dr.relativedelta(days=1))
        # inside embargo date, but whitelisted
        issue_3 = IssueFactory.create(
            journal=journal, is_published=True, date_published=embargo_date,
            force_free_access=True)
        assert set(journal.published_open_access_issues) == {issue_2, issue_3}

    def test_can_return_the_published_open_access_issues_period_coverage(self):
        from erudit.conf.settings import SCIENTIFIC_JOURNAL_EMBARGO_IN_MONTHS as ml
        now_dt = dt.date.today()
        journal = JournalFactory()
        journal.last_publication_year = now_dt.year
        journal.open_access = False
        journal.save()
        DATES = [
            dt.date(now_dt.year, now_dt.month, 1),
            now_dt - dr.relativedelta(months=ml),
            now_dt - dr.relativedelta(months=(ml + 5)),
            now_dt - dr.relativedelta(months=((ml + 5) * 2)),
        ]

        for d in reversed(DATES):
            IssueFactory(journal=journal, year=d.year, date_published=d)
        EXPECTED = {
            'from': DATES[3],
            'to': DATES[2],
        }
        assert journal.published_open_access_issues_period_coverage == EXPECTED

    def test_published_issues_uses_fedora_order(self):
        # The `published_issues` queryset returns a list that uses order fetched from fedora.
        journal = JournalFactory.create()
        issue1 = IssueFactory.create(journal=journal, add_to_fedora_journal=False)
        issue2 = IssueFactory.create(journal=journal, add_to_fedora_journal=False)
        issue3 = IssueFactory.create(journal=journal, add_to_fedora_journal=False)
        # add issues to their fedora journal in a different order
        ordered_issues = [issue3, issue1, issue2]
        for issue in ordered_issues:
            repository.api.add_publication_to_parent_journal(issue)

        assert list(journal.published_issues.all()) == list(reversed(ordered_issues))

    def test_published_issues_can_mix_fedora_and_non_fedora(self):
        # A journal with incomplete fedora PIDs are "mixed" journals who left Erudit. We keep
        # old issues in Fedora but redirect new issues wherever they are.
        # It's thus possible to have some issues that aren't part of the PID list. In these cases,
        # we put these issues *before* those in the PID list, in -date_published order.
        i1 = IssueFactory.create()
        i2 = IssueFactory.create_published_after(i1)
        # non-fedora
        i3 = IssueFactory.create_published_after(i2, localidentifier=None)
        i4 = IssueFactory.create_published_after(i3, localidentifier=None)

        assert list(i1.journal.published_issues.all()) == [i4, i3, i2, i1]

    def test_published_issues_missing_pid(self):
        # When a PID is missing from the PID list *but* that the issue is a fedora one, put that
        # issue at the *end* of the list. We do that because cases of missing issues are most
        # likely old issues and we don't want them to end up being considered as the journal's
        # latest issue. See #1664
        i1 = IssueFactory.create(add_to_fedora_journal=False)
        i2 = IssueFactory.create_published_after(i1)

        assert list(i1.journal.published_issues.all()) == [i2, i1]


class TestIssue:
    def test_can_return_the_associated_eulfedora_model(self):
        issue = IssueFactory()
        assert issue.fedora_model == PublicationDigitalObject

    def test_can_return_the_associated_erudit_class(self):
        issue = IssueFactory()
        assert issue.erudit_class == EruditPublication

    def test_can_return_its_full_identifier(self):
        journal = JournalFactory(localidentifier='dummy139')
        issue = IssueFactory(journal=journal, localidentifier='dummy1234')
        assert issue.get_full_identifier() == 'erudit:erudit.dummy139.dummy1234'

    def test_issue_has_no_full_identifier_if_a_part_is_missing(self):
        journal = JournalFactory(localidentifier='dummy139')
        issue = IssueFactory(journal=journal, localidentifier=None)
        assert issue.get_full_identifier() is None

    def test_can_return_an_appropriate_fedora_pid(self):
        journal = JournalFactory(localidentifier='dummy139')
        issue = IssueFactory(journal=journal, localidentifier='dummy1234')
        assert issue.pid == 'erudit:erudit.dummy139.dummy1234'

    @pytest.mark.parametrize('journal_type,conf_name', [
        ('S', 'SCIENTIFIC_JOURNAL_EMBARGO_IN_MONTHS'),
        ('C', 'CULTURAL_JOURNAL_EMBARGO_IN_MONTHS'),
    ])
    def test_knows_if_it_is_embargoed(self, journal_type, conf_name):
        import erudit.conf.settings
        ml = getattr(erudit.conf.settings, conf_name)
        journal = JournalFactory(type_code=journal_type)
        now_dt = dt.date.today()
        journal.last_publication_year = now_dt.year
        journal.open_access = False
        journal.save()
        date_issue_1 = dt.date(now_dt.year, now_dt.month, 1)
        date_issue_2 = now_dt - dr.relativedelta(months=ml)
        date_issue_3 = date_issue_2 - dr.relativedelta(days=1)
        date_issue_4 = now_dt - dr.relativedelta(months=(ml + 5))
        date_issue_5 = now_dt - dr.relativedelta(months=((ml + 5) * 2))
        issue_1 = IssueFactory.create(
            journal=journal, year=date_issue_1.year,
            date_published=date_issue_1)
        issue_2 = IssueFactory.create(
            journal=journal, year=date_issue_2.year,
            date_published=date_issue_2)
        issue_3 = IssueFactory.create(
            journal=journal, year=date_issue_3.year,
            date_published=date_issue_3)
        issue_4 = IssueFactory.create(
            journal=journal, year=date_issue_4.year,
            date_published=date_issue_4)
        issue_5 = IssueFactory.create(
            journal=journal, year=date_issue_5.year,
            date_published=date_issue_5)
        issue_6 = IssueFactory.create(
            journal=journal, year=date_issue_1.year - 10,
            date_published=date_issue_1)
        issue_7 = IssueFactory.create(
            journal=journal, year=date_issue_1.year - 10,
            date_published=date_issue_1, force_free_access=True)
        assert issue_1.embargoed
        assert issue_2.embargoed
        assert not issue_3.embargoed
        assert not issue_4.embargoed
        assert not issue_5.embargoed
        assert issue_6.embargoed
        assert not issue_7.embargoed

    def test_issues_with_a_next_year_published_date_are_embargoed(self):
        now_dt = dt.datetime.now()
        journal = JournalFactory(type_code='C')
        journal.last_publication_year = now_dt.year + 1
        journal.save()
        issue = IssueFactory.create(
            journal=journal,
            year=now_dt.year + 1, date_published=dt.date(now_dt.year + 1, 1, 1)
        )
        assert issue.embargoed is True

    def test_knows_that_issues_with_open_access_are_not_embargoed(self):
        now_dt = dt.datetime.now()
        journal = JournalFactory()
        j2 = JournalFactory.create(
            type_code='C',
            open_access=False,
            collection=CollectionFactory.create(code='not-erudit'),
        )
        journal.last_publication_year = now_dt.year
        journal.open_access = True
        journal.save()
        issue_1 = IssueFactory.create(
            journal=journal, year=now_dt.year - 1,
            date_published=dt.date(now_dt.year - 1, 3, 20))
        issue_2 = IssueFactory.create(
            journal=journal, year=now_dt.year - 2,
            date_published=dt.date(now_dt.year - 2, 3, 20))
        issue_3 = IssueFactory.create(
            journal=j2, year=now_dt.year,
            date_published=dt.date(now_dt.year, 3, 20))
        assert not issue_1.embargoed
        assert not issue_2.embargoed
        assert not issue_3.embargoed

    def test_last_issue_is_always_embargoed(self):
        from erudit.conf.settings import SCIENTIFIC_JOURNAL_EMBARGO_IN_MONTHS as ml
        outside_embargo = dt.date.today() - dr.relativedelta(months=ml + 1)
        issue1 = IssueFactory(date_published=outside_embargo)
        issue2 = IssueFactory(journal=issue1.journal, date_published=outside_embargo)
        assert issue1 != issue1.journal.last_issue
        assert not issue1.embargoed
        assert issue2 == issue2.journal.last_issue
        assert issue2.embargoed

    def test_last_issue_is_not_always_embargoed_when_next_journal(self):
        from erudit.conf.settings import SCIENTIFIC_JOURNAL_EMBARGO_IN_MONTHS as ml
        outside_embargo = dt.date.today() - dr.relativedelta(months=ml + 1)
        issue = IssueFactory(
            journal__next_journal=JournalFactory(),
            date_published=outside_embargo)
        assert not issue.embargoed

    def test_issue_with_roc_article_is_forced_to_free_access(self):
        article = ArticleFactory()
        with repository.api.open_article(article.pid) as wrapper:
            wrapper.set_roc()
        repository.api.add_article_to_parent_publication(article)
        article.issue.sync_with_erudit_object()
        assert article.issue.force_free_access

    def test_knows_if_it_has_a_coverpage(self):
        journal = JournalFactory()
        journal.open_access = True
        journal.save()
        with open(settings.MEDIA_ROOT + '/coverpage.png', 'rb') as f:
            issue_1 = IssueFactory.create(journal=journal)
            issue_2 = IssueFactory.create(journal=journal)
            issue_1._fedora_object = unittest.mock.MagicMock()
            issue_1._fedora_object.pid = "pid"
            issue_1._fedora_object.coverpage = unittest.mock.MagicMock()
            issue_1._fedora_object.coverpage.content = io.BytesIO(f.read())
            issue_2._fedora_object = unittest.mock.MagicMock()
            issue_2._fedora_object.pid = "pid2"
            issue_2._fedora_object.coverpage = unittest.mock.MagicMock()
            issue_2._fedora_object.coverpage.content = ''
        # We don't crash trying to check the fedora object. We return False
        issue_3 = IssueFactory.create(journal=journal)

        assert issue_1.has_coverpage
        assert not issue_2.has_coverpage
        assert not issue_3.has_coverpage

    def test_knows_that_an_issue_with_an_empty_coverpage_has_no_coverpage(self):
        journal = JournalFactory(open_access=True)
        with open(settings.MEDIA_ROOT + '/coverpage_empty.png', 'rb') as f:
            issue = IssueFactory.create(journal=journal)
            issue._fedora_object = unittest.mock.MagicMock()
            issue._fedora_object.pid = "issue"
            issue._fedora_object.coverpage = unittest.mock.MagicMock()
            issue._fedora_object.coverpage.content = io.BytesIO(f.read())

        assert not issue.has_coverpage

    def test_can_return_a_slug_that_can_be_used_in_urls(self):
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
        assert issue_1.volume_slug == '2015-v4-n1'
        assert issue_2.volume_slug == '2015-v4'
        assert issue_3.volume_slug == '2015-n2'
        assert issue_4.volume_slug == '2015-v2-3-n39'
        assert issue_5.volume_slug == '2015'
        assert issue_6.volume_slug == '2015-v2-bis-n39'

    @pytest.mark.parametrize('fixture_name,expected', [
        ('inter02349', "Affirmation autochtone"),
        ('images1080663', "David Cronenberg / La production au Qu&#233;bec: Cinq cin&#233;astes sur le divan"),  # noqa
    ])
    def test_can_return_its_name_with_themes(self, fixture_name, expected):
        issue = IssueFactory()
        repository.api.set_publication_xml(
            issue.get_full_identifier(),
            open('./tests/fixtures/issue/{}.xml'.format(fixture_name), 'rb').read(),
        )
        assert issue.name_with_themes == expected

    def test_get_from_fedora_ids_can_return_ephemeral_issues(self):
        journal = JournalFactory()
        ephemeral_pid = '{}.dummy123'.format(journal.get_full_identifier())
        repository.api.register_publication(ephemeral_pid)
        issue = Issue.from_fedora_ids(journal.code, 'dummy123')
        assert issue.id is None
        assert issue.get_full_identifier() == ephemeral_pid

    def test_get_from_fedora_ids_can_return_django_models(self):
        issue = IssueFactory()
        result = Issue.from_fedora_ids(issue.journal.code, issue.localidentifier)
        assert result.id is not None
        assert result.id == issue.id

    def test_get_from_fedora_ids_can_raise_DoesNotExist(self):
        journal = JournalFactory()
        with pytest.raises(Issue.DoesNotExist):
            Issue.from_fedora_ids(journal.code, 'dummy123')


class TestArticle:
    def test_properties(self):
        article = ArticleFactory(type='compterendu')
        assert article.get_type_display() == 'Compte rendu'

    def test_only_has_fedora_object_if_collection_has_localidentifier(self):
        c1 = CollectionFactory.create(localidentifier=None)
        j1 = JournalFactory.create(collection=c1)
        issue_1 = IssueFactory.create(journal=j1)
        with pytest.raises(Article.DoesNotExist):
            ArticleFactory.create(issue=issue_1)

    def test_knows_that_it_is_in_open_access_if_its_issue_is_in_open_access(self):
        j1 = JournalFactory.create(open_access=True)
        j2 = JournalFactory.create(open_access=False)
        issue_1 = IssueFactory.create(journal=j1)
        article_1 = ArticleFactory.create(issue=issue_1)
        issue_2 = IssueFactory.create(journal=j2)
        article_2 = ArticleFactory.create(issue=issue_2)
        assert article_1.open_access
        assert not article_2.open_access

    def test_knows_if_it_is_in_open_access_if_its_journal_is_in_open_access(self):
        j1 = JournalFactory.create(open_access=True)
        j2 = JournalFactory.create(open_access=False)
        issue_1 = IssueFactory.create(journal=j1)
        article_1 = ArticleFactory.create(issue=issue_1)
        issue_2 = IssueFactory.create(journal=j2)
        article_2 = ArticleFactory.create(issue=issue_2)
        assert article_1.open_access
        assert not article_2.open_access

    def test_knows_if_it_is_embargoed(self):
        from erudit.conf.settings import SCIENTIFIC_JOURNAL_EMBARGO_IN_MONTHS as ml
        article1 = ArticleFactory(
            issue__journal__open_access=False,
            issue__date_published=dt.date.today() - dr.relativedelta(months=ml + 1))
        article2 = ArticleFactory(
            issue__journal=article1.issue.journal, issue__date_published=dt.date.today())
        # the 3rd article is to take the "last issue spot" in embargo rules.
        article3 = ArticleFactory(issue__journal=article1.issue.journal)
        assert not article1.embargoed
        assert article2.embargoed
        assert article3.embargoed

    def test_get_from_fedora_ids_can_return_ephemeral_issues(self):
        issue = IssueFactory()
        ephemeral_pid = '{}.dummy123'.format(issue.get_full_identifier())
        repository.api.register_article(ephemeral_pid)
        article = Article.from_fedora_ids(issue.journal.code, issue.localidentifier, 'dummy123')
        assert article.get_full_identifier() == ephemeral_pid

    def test_get_from_fedora_ids_can_raise_DoesNotExist(self):
        issue = IssueFactory()
        with pytest.raises(Article.DoesNotExist):
            Article.from_fedora_ids(issue.journal.code, issue.localidentifier, 'dummy123')

    @pytest.mark.parametrize('collection_code,is_external', [('erudit', False), ('unb', True)])
    def test_is_external(self, collection_code, is_external):
        # an article is "external" if its collection code is "unb"
        article = ArticleFactory(issue__journal__collection__code=collection_code)
        assert article.is_external == is_external

    def test_absolute_url_when_external(self):
        # When an article is "external", its absolute_url is the value of its first "URLDocument"
        # in Solr
        article = ArticleFactory(
            issue__journal__collection__code='unb',
            solr_attrs={'URLDocument': ['http://example.com']}
        )
        assert article.get_absolute_url() == 'http://example.com'


def test_journaltype_can_return_embargo_duration_in_days():
    journal_type = JournalTypeFactory.create(code='S')
    from erudit.conf.settings import SCIENTIFIC_JOURNAL_EMBARGO_IN_MONTHS as ml
    duration = dt.date.today() - (dt.date.today() - dr.relativedelta(months=ml))
    assert journal_type.embargo_duration(unit="days") == duration.days
