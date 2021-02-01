import datetime as dt
import os

import pytest
import unittest.mock

from django.http import Http404
from django.test import Client, TestCase, override_settings, RequestFactory
from django.urls import reverse

from apps.public.journal.article_access_log import ArticleAccessType
from apps.public.journal.viewmixins import SolrDataMixin
from base.test.factories import UserFactory
from erudit.test.factories import ArticleFactory, IssueFactory, JournalFactory, \
    JournalInformationFactory, ContributorFactory
from erudit.fedora import repository
from eruditarticle.objects.article import EruditArticle
from erudit.fedora.objects import ArticleDigitalObject
from erudit.models import Article, Issue, Journal
from erudit.test.domchange import SectionTitle
from erudit.test.solr import FakeSolrData
from apps.public.journal.views import (
    JournalDetailView,
    IssueDetailView,
    ArticleDetailView,
    ArticleSummaryView,
    ArticleBiblioView,
    ArticleTocView,
    ArticleXmlView,
    ArticleRawPdfView,
    ArticleRawPdfFirstPageView,
    GoogleScholarSubscribersView,
    GoogleScholarSubscriberJournalsView,
    JournalStatisticsView,
    IssueReaderView,
    IssueReaderPageView,
    IssueRawCoverpageView,
    IssueRawCoverpageHDView,
    ArticleMediaView,
)
from core.subscription.test.factories import JournalAccessSubscriptionFactory

FIXTURE_ROOT = os.path.join(os.path.dirname(__file__), 'fixtures')
pytestmark = pytest.mark.django_db


class TestJournalDetailView:

    @pytest.mark.parametrize('localidentifier, language, expected_notes', [
        ('journal1', 'fr', ['foobar']),
        ('journal1', 'en', ['foobaz']),
        # Should not crash if the journal is not in fedora.
        (None, 'fr', []),
    ])
    def test_get_context_data_with_notes(self, localidentifier, language, expected_notes):
        view = JournalDetailView()
        view.object = unittest.mock.MagicMock()
        view.request = unittest.mock.MagicMock()
        view.kwargs = unittest.mock.MagicMock()
        view.journal = JournalFactory(
            localidentifier=localidentifier,
            notes=[
                {'langue': 'fr', 'content': 'foobar', 'pid': f'erudit:erudit.{localidentifier}'},
                {'langue': 'en', 'content': 'foobaz', 'pid': f'erudit:erudit.{localidentifier}'}
            ],
        )
        with override_settings(LANGUAGE_CODE=language):
            context = view.get_context_data()
            assert context['notes'] == expected_notes

    def test_contributors(self):
        issue = IssueFactory()
        url = reverse('public:journal:journal_detail', kwargs={'code': issue.journal.code})

        # No contributors in journal_info, issue's contributors should be displayed.
        repository.api.set_publication_xml(
            issue.get_full_identifier(),
            open('tests/fixtures/issue/images1102374.xml', 'rb').read(),
        )
        html = Client().get(url).content.decode()
        assert 'Claude Racine' in html
        assert '<dd>Marie-Claude Loiselle (Rédactrice en chef)</dd>' in html
        assert 'Rédaction&nbsp;:\n          \n            Marie-Claude Loiselle (Rédactrice en chef)' in html
        assert 'Foo (Bar)' not in html

        # There's a director in journal_info, issue's contributors should not be displayed.
        journal_info = JournalInformationFactory(journal=issue.journal)
        journal_info.editorial_leaders.add(
            ContributorFactory(
                type='D',
                name='Foo',
                role='Bar',
                journal_information=journal_info,
            )
        )
        html = Client().get(url).content.decode()
        assert 'Claude Racine (Éditeur)' not in html
        assert 'Isabelle Richer (Rédactrice adjointe)' not in html
        assert '<dd>Foo (Bar)</dd>' in html
        assert 'Direction&nbsp;:\n          \n            Foo (Bar)' in html

    def test_available_since_when_issues_are_not_produced_in_the_same_order_as_their_published_date(self):
        journal = JournalFactory()
        issue_1 = IssueFactory(journal=journal, date_published=dt.date(2019, 1, 1))
        issue_2 = IssueFactory(journal=journal, date_published=dt.date(2015, 1, 1))
        issue_3 = IssueFactory(journal=journal, date_published=dt.date(2017, 1, 1))
        url = reverse('public:journal:journal_detail', kwargs={
            'code': journal.code,
        })
        html = Client().get(url).content.decode()
        assert '<dt>Disponible dans Érudit depuis</dt>\n          <dd>2015</dd>' in html

    @pytest.mark.parametrize('subtitle', [
        ('bar'),
        (''),
        (None),
    ])
    def test_journal_with_no_issue_title_and_subtitle_display(self, subtitle):
        journal = JournalFactory(
            name='foo',
            subtitle=subtitle,
        )
        url = reverse('public:journal:journal_detail', kwargs={
            'code': journal.code,
        })
        html = Client().get(url).content.decode()
        assert '<span class="journal-title">foo</span>' in html
        if subtitle:
            assert '<span class="journal-subtitle">bar</span>' in html
        else:
            assert '<span class="journal-subtitle">None</span>' not in html

    def test_journal_note_with_html_link(self):
        issue = IssueFactory(journal__localidentifier='recma0448')
        repository.api.set_xml_for_pid(
            issue.journal.get_full_identifier(),
            open('tests/fixtures/journal/recma0448.xml', 'rb').read(),
        )
        url = reverse('public:journal:journal_detail', kwargs={
            'code': issue.journal.code,
        })
        html = Client().get(url).content.decode()
        assert 'Cette revue a cessé de publier ses numéros sur Érudit depuis 2016, vous pouvez consulter les numéros subséquents sur <a href="https://www.cairn.info/revue-recma.htm">Cairn</a>' in html

    @pytest.mark.parametrize('with_issue, expected_cache_key', [
        (False, 'journal_code'),
        (True, 'issue_localidentifier'),
    ])
    def test_journal_base_cache_key(self, with_issue, expected_cache_key):
        journal = JournalFactory(code='journal_code')
        if with_issue:
            issue = IssueFactory(journal=journal, localidentifier='issue_localidentifier')
        view = JournalDetailView()
        view.object = journal
        view.journal = journal
        view.request = unittest.mock.MagicMock()
        view.kwargs = unittest.mock.MagicMock()
        context = view.get_context_data()
        assert context['primary_cache_key'] == expected_cache_key


class TestJournalAuthorsListView:

    def test_do_not_crash_for_journal_with_no_issue(self):
        journal = JournalFactory()
        url = reverse('public:journal:journal_authors_list', kwargs={'code': journal.code})
        response = Client().get(url)
        assert response.status_code == 200


class TestIssueDetailSummary:
    def test_generate_sections_tree_with_scope_surtitre(self):
        view = IssueDetailView()
        article_1 = ArticleFactory(from_fixture='1059644ar')
        article_2 = ArticleFactory(from_fixture='1059645ar')
        article_3 = ArticleFactory(from_fixture='1059646ar')
        sections_tree = view.generate_sections_tree([article_1, article_2, article_3])
        assert sections_tree == {
            'level': 0,
            'type': 'subsection',
            'titles': {'main': None, 'paral': None},
            'groups': [{
                'level': 1,
                'type': 'subsection',
                'titles': {'main': 'La recherche qualitative aujourd’hui. 30 ans de diffusion et de réflexion', 'paral': []},
                'notegens': [{
                    'content': ['Sous la direction de Frédéric Deschenaux, Chantal Royer et Colette Baribeau'],
                    'scope': 'surtitre',
                    'type': 'edito',
                }],
                'groups': [{
                    'level': 2,
                    'type': 'subsection',
                    'titles': {'main': 'Introduction', 'paral': []},
                    'notegens': [],
                    'groups': [{
                        'level': 2,
                        'type': 'objects',
                        'objects': [article_1],
                    }],
                }, {
                    'level': 1,
                    'type': 'objects',
                    'objects': [article_2, article_3],
                }],
            }],
        }

    def test_can_generate_section_tree_with_contiguous_articles(self):
        view = IssueDetailView()
        article_1 = ArticleFactory()
        article_2 = ArticleFactory()
        article_3 = ArticleFactory(section_titles=[SectionTitle(1, False, "section 1")])
        sections_tree = view.generate_sections_tree([article_1, article_2, article_3])
        assert sections_tree == {
            'titles': {'paral': None, 'main': None},
            'level': 0,
            'groups': [
                {'objects': [article_1, article_2], 'type': 'objects', 'level': 0},
                {
                    'titles': {'paral': [], 'main': "section 1"},
                    'level': 1,
                    'groups': [{'objects': [article_3], 'type': 'objects', 'level': 1}],
                    'type': 'subsection',
                    'notegens': [],
                },
            ],
            'type': 'subsection',
        }

    def test_can_generate_section_tree_with_three_levels(self):
        view = IssueDetailView()
        article = ArticleFactory(section_titles=[
            SectionTitle(1, False, "section 1"),
            SectionTitle(2, False, "section 2"),
            SectionTitle(3, False, "section 3"),
        ])

        sections_tree = view.generate_sections_tree([article])
        assert sections_tree == {
            'type': 'subsection',
            'level': 0,
            'titles': {'paral': None, 'main': None},
            'groups': [{
                'type': 'subsection',
                'level': 1,
                'titles': {'paral': [], 'main': 'section 1'},
                'notegens': [],
                'groups': [{
                    'type': 'subsection',
                    'level': 2,
                    'titles': {'paral': [], 'main': 'section 2'},
                    'notegens': [],
                    'groups': [{
                        'type': 'subsection',
                        'level': 3,
                        'titles': {'paral': [], 'main': 'section 3'},
                        'groups': [
                            {'objects': [article], 'type': 'objects', 'level': 3},
                        ],
                        'notegens': [],
                    }]
                }]
            }]
        }

    def test_can_generate_section_tree_with_non_contiguous_articles(self):
        view = IssueDetailView()
        articles = [
            ArticleFactory(section_titles=[SectionTitle(1, False, "section 1")]),
            ArticleFactory(section_titles=[
                SectionTitle(1, False, "section 1"),
                SectionTitle(2, False, "section 1.1"),
            ]),
            ArticleFactory(section_titles=[SectionTitle(1, False, "section 1")]),
        ]

        sections_tree = view.generate_sections_tree(articles)
        assert sections_tree == {
            'type': 'subsection',
            'level': 0,
            'titles': {'paral': None, 'main': None},
            'groups': [
                {
                    'type': 'subsection',
                    'level': 1,
                    'titles': {
                        'paral': [], 'main': 'section 1'
                    },
                    'notegens': [],
                    'groups': [
                        {'type': 'objects', 'level': 1, 'objects': [articles[0]]},
                        {
                            'type': 'subsection', 'level': 2, 'titles': {'paral': [], 'main': 'section 1.1'},  # noqa
                            'groups': [{'type': 'objects', 'level': 2, 'objects': [articles[1]]}],
                            'notegens': [],
                        },
                        {
                            'type': 'objects', 'level': 1, 'objects': [articles[2]],
                        }
                    ]
                }
            ]
        }

    def test_can_generate_section_tree_with_notegens(self):
        view = IssueDetailView()
        articles = [
            ArticleFactory(
                section_titles=[
                    SectionTitle(1, False, "Section 1"),
                ],
                notegens=[
                    {'content': 'Note surtitre', 'scope': 'surtitre', 'type': 'edito'},
                ],
            ),
            ArticleFactory(
                section_titles=[
                    SectionTitle(1, False, "Section 1"),
                    SectionTitle(2, False, "Section 2"),
                ],
                notegens=[
                    {'content': 'Note surtitre2', 'scope': 'surtitre2', 'type': 'edito'},
                ],
            ),
        ]
        sections_tree = view.generate_sections_tree(articles)
        assert sections_tree == {
            'level': 0,
            'type': 'subsection',
            'titles': {'main': None, 'paral': None},
            'groups': [{
                'level': 1,
                'type': 'subsection',
                'titles': {'main': 'Section 1', 'paral': []},
                'notegens': [{
                    'content': ['Note surtitre'],
                    'scope': 'surtitre',
                    'type': 'edito',
                }],
                'groups': [{
                    'level': 1,
                    'objects': [articles[0]],
                    'type': 'objects',
                }, {
                    'level': 2,
                    'type': 'subsection',
                    'titles': {'main': 'Section 2', 'paral': []},
                    'notegens': [{
                        'content': ['Note surtitre2'],
                        'scope': 'surtitre2',
                        'type': 'edito',
                    }],
                    'groups': [{
                        'level': 2,
                        'objects': [articles[1]],
                        'type': 'objects',
                    }],
                }],
            }],
        }

    @unittest.mock.patch('erudit.fedora.modelmixins.cache')
    @pytest.mark.parametrize('is_published, expected_count', [
        (False, 3),
        (True, 3),
    ])
    def test_issue_caching(self, mock_cache, is_published, expected_count):
        mock_cache.get.return_value = None

        article = ArticleFactory(issue__is_published=is_published)
        url = reverse('public:journal:issue_detail', kwargs={
            'journal_code': article.issue.journal.code,
            'issue_slug': article.issue.volume_slug,
            'localidentifier': article.issue.localidentifier,
        })
        mock_cache.get.reset_mock()

        response = Client().get(url, {
            'ticket': article.issue.prepublication_ticket,
        })
        assert mock_cache.get.call_count == expected_count

    def test_main_title_and_paral_title(self):
        article = ArticleFactory(
            from_fixture='1058197ar',
        )
        url = reverse('public:journal:issue_detail', kwargs={
            'journal_code': article.issue.journal.code,
            'issue_slug': article.issue.volume_slug,
            'localidentifier': article.issue.localidentifier,
        })
        response = Client().get(url)
        html = response.content.decode()
        # Check that there's only one space between the main title and the '/'.
        assert 'Inaugural Lecture of the FR Scott Professor&nbsp;/ Conférence inaugurale du Professeur FR Scott' in html

    def test_issue_detail_view_with_untitled_article(self):
        article = ArticleFactory(
            from_fixture='1042058ar',
            localidentifier='article',
            issue__year='2000',
            issue__localidentifier='issue',
            issue__journal__code='journal',
            issue__journal__name='Revue',
        )
        url = reverse('public:journal:issue_detail', kwargs={
            'journal_code': article.issue.journal.code,
            'issue_slug': article.issue.volume_slug,
            'localidentifier': article.issue.localidentifier,
        })
        response = Client().get(url)
        html = response.content.decode()
        assert '<h6 class="bib-record__title">\n    \n    <a href="/fr/revues/journal/2000-issue/article/"\n    \n    title="Lire l\'article">\n    [Article sans titre]\n    </a>\n  </h6>' in html

    def test_article_authors_are_not_displayed_with_suffixes(self):
        article = ArticleFactory(
            from_fixture='1058611ar',
        )
        url = reverse('public:journal:issue_detail', kwargs={
            'journal_code': article.issue.journal.code,
            'issue_slug': article.issue.volume_slug,
            'localidentifier': article.issue.localidentifier,
        })
        html = Client().get(url).content.decode()
        # Check that authors' suffixes are not displayed on the issue detail view.
        assert '<p class="bib-record__authors col-sm-9">\n      Mélissa Beaudoin, Stéphane Potvin, Laura Dellazizzo, Maëlle Surprenant, Alain Lesage, Alain Vanasse, André Ngamini-Ngui et Alexandre Dumais\n    </p>' in html

    def test_article_authors_html_display(self):
        article = ArticleFactory(
            from_fixture='1070658ar',
        )
        url = reverse('public:journal:issue_detail', kwargs={
            'journal_code': article.issue.journal.code,
            'issue_slug': article.issue.volume_slug,
            'localidentifier': article.issue.localidentifier,
        })
        html = Client().get(url).content.decode()
        # Check that authors are displayed with html.
        assert '<p class="bib-record__authors col-sm-9">\n      Le Comité exécutif de la ' \
               '<em>Revue québécoise de psychologie</em> (Suzanne Léveillée, Julie Maheux, ' \
               'Gaëtan Tremblay, Carolanne Vignola-Lévesque)\n    </p>' in html

    @pytest.mark.parametrize('journal_type', [
        ('S'),
        ('C'),
    ])
    @pytest.mark.parametrize('is_published', [
        (True),
        (False),
    ])
    def test_issue_reader_url_in_context_for_cultural_journal_issues(self, journal_type, is_published):
        issue = IssueFactory(
            is_published=is_published,
            year='2000',
            localidentifier='issue',
            journal__code='journal',
            journal__type_code=journal_type,
        )
        issue.is_prepublication_ticket_valid = unittest.mock.MagicMock()
        view = IssueDetailView()
        view.object = issue
        view.request = unittest.mock.MagicMock()
        context = view.get_context_data()
        if journal_type == 'C':
            assert context['reader_url'] == '/fr/revues/journal/2000-issue/feuilletage/'
            if not is_published:
                assert context['ticket'] == issue.prepublication_ticket
        else:
            assert 'reader_url' not in context

    def test_issue_detail_back_issues(self):
        journal = JournalFactory()
        issue_1 = IssueFactory(journal=journal, year='2019', volume='1', number='1')
        issue_2 = IssueFactory(journal=journal, year='2019', volume='1', number='2')
        issue_3 = IssueFactory(journal=journal, year='2019', volume='2', number='1')
        issue_4 = IssueFactory(journal=journal, year='2019', volume='2', number='2')
        issue_5 = IssueFactory(journal=journal, year='2019', volume='3', number='1')
        issue_6 = IssueFactory(journal=journal, year='2019', volume='3', number='2')
        view = IssueDetailView()
        view.request = unittest.mock.MagicMock()
        view.object = issue_6
        context = view.get_context_data()
        # Back issues should be ordered by year, volume & number, and should not include current one
        assert list(context['back_issues']) == [issue_5, issue_4, issue_3, issue_2]


class TestIssueReaderView:

    @pytest.mark.parametrize('journal_type', [
        ('S'),
        ('C'),
    ])
    @pytest.mark.parametrize('is_published', [
        (True),
        (False),
    ])
    def test_get_context_data(self, journal_type, is_published):
        issue = IssueFactory(
            is_published=is_published,
            year='2000',
            localidentifier='issue',
            journal__code='journal',
            journal__type_code=journal_type,
        )
        issue.is_prepublication_ticket_valid = unittest.mock.MagicMock()
        view = IssueReaderView()
        view.object = issue
        view.get_object = unittest.mock.MagicMock(return_value=issue)
        view.request = unittest.mock.MagicMock()
        view.kwargs = unittest.mock.MagicMock()
        if journal_type == 'C':
            context = view.get_context_data()
            assert context['num_leafs'] == '80'
            assert context['page_width'] == '1350'
            assert context['page_height'] == '1800'
            assert context['issue_url'] == '/fr/revues/journal/2000-issue/'
            if not is_published:
                assert context['ticket'] == issue.prepublication_ticket
        else:
            with pytest.raises(Http404):
                context = view.get_context_data()


class TestIssueReaderPageView:

    @pytest.mark.parametrize('page, open_access, is_published, ticket, expected_status_code, expected_redirection', [
        # All pages should be accessible for open access published issues.
        ('1', True, True, False, 200, ''),
        ('6', True, True, False, 200, ''),
        # Only the 5 first pages should be accessible for embargoed published issues.
        ('1', False, True, False, 200, ''),
        ('6', False, True, False, 302, '/static/img/bookreader/restriction.jpg'),
        # All pages should be accessible for unpublished issues when a prepublication ticket is provided.
        ('1', True, False, True, 200, ''),
        ('6', True, False, True, 200, ''),
        ('1', False, False, True, 200, ''),
        ('6', False, False, True, 200, ''),
        # No pages should be accessible for unpublished issues when no prepublication ticket is provided.
        ('1', True, False, False, 302, '/fr/revues/journal/'),
        ('6', True, False, False, 302, '/fr/revues/journal/'),
        ('1', False, False, False, 302, '/fr/revues/journal/'),
        ('6', False, False, False, 302, '/fr/revues/journal/'),
    ])
    def test_issue_reader_page_view(self, page, open_access, is_published, ticket, expected_status_code, expected_redirection):
        issue = IssueFactory(
            is_published=is_published,
            journal__open_access=open_access,
            journal__code='journal',
        )
        url = reverse('public:journal:issue_reader_page', kwargs={
            'journal_code': issue.journal.code,
            'issue_slug': issue.volume_slug,
            'localidentifier': issue.localidentifier,
            'page': page,
        })
        response = Client().get(url, {
            'ticket': issue.prepublication_ticket if ticket else '',
        })
        assert response.status_code == expected_status_code
        if expected_redirection:
            assert response.url == expected_redirection

    @pytest.mark.parametrize('is_published', (True, False))
    @unittest.mock.patch('erudit.fedora.views.generic.get_cached_datastream_content')
    def test_cache_unpublished_issue_pages(self, mock_get_cached_datastream_content, is_published):
        issue = IssueFactory(localidentifier='issue', is_published=is_published)
        view = IssueReaderPageView()
        view.kwargs = {'localidentifier': issue.localidentifier, 'page': 1}
        view.get_datastream_content(unittest.mock.MagicMock())
        assert mock_get_cached_datastream_content.call_count == 1


class TestIssueRawCoverpageView:
    @pytest.mark.parametrize('is_published', (True, False))
    @unittest.mock.patch('erudit.fedora.views.generic.get_cached_datastream_content')
    def test_cache_unpublished_issue_coverpages(self, mock_get_cached_datastream_content, is_published):
        issue = IssueFactory(localidentifier='issue', is_published=is_published)
        view = IssueRawCoverpageView()
        view.kwargs = {'localidentifier': issue.localidentifier}
        view.get_datastream_content(unittest.mock.MagicMock())
        assert mock_get_cached_datastream_content.call_count == 1


class TestIssueRawCoverpageHDView:
    @pytest.mark.parametrize('is_published', (True, False))
    @unittest.mock.patch('erudit.fedora.views.generic.get_cached_datastream_content')
    def test_cache_unpublished_issue_coverpages_hd(self, mock_get_cached_datastream_content, is_published):
        issue = IssueFactory(localidentifier='issue', is_published=is_published)
        view = IssueRawCoverpageHDView()
        view.kwargs = {'localidentifier': issue.localidentifier}
        view.get_datastream_content(unittest.mock.MagicMock())
        assert mock_get_cached_datastream_content.call_count == 1


class TestIssueXmlView:

    @pytest.mark.parametrize('ticket', [
        True, False,
    ])
    @pytest.mark.parametrize('is_published', [
        True, False,
    ])
    def test_issue_raw_xml_view(self, is_published, ticket):
        issue = IssueFactory(
            is_published=is_published,
            journal__code='journal',
        )
        url = reverse('public:journal:issue_raw_xml', kwargs={
            'journal_code': issue.journal.code,
            'issue_slug': issue.volume_slug,
            'localidentifier': issue.localidentifier,
        })
        response = Client().get(url, {
            'ticket': issue.prepublication_ticket if ticket else '',
        }, follow=True)
        # The Issue XML view should be accessible if the issue is published or if a prepublication
        # ticket is provided.
        if is_published or ticket:
            with open('./tests/fixtures/issue/minimal.xml', mode='r') as xml:
                assert response.content.decode() in xml.read()
        # The Issue XML view should redirect to the journal detail view if the issue is not
        # published and a prepublication ticket is not provided.
        else:
            assert response.redirect_chain == [('/fr/revues/journal/', 302)]


class TestRenderArticleTemplateTag:

    @pytest.fixture(autouse=True)
    def article_detail_solr_data(self, monkeypatch):
        monkeypatch.setattr(SolrDataMixin, 'solr_data', FakeSolrData())

    def render_article_detail_html(self, fixture='article.xml'):
        """ Helper method to mock an article detail view from a given fixture."""
        with open(FIXTURE_ROOT + '/' + fixture, mode='r') as fp:
            xml = fp.read()

        article = ArticleFactory()

        article.erudit_object = EruditArticle(xml)

        view = ArticleDetailView()
        view.request = unittest.mock.MagicMock()
        view.object = article

        article.issue.get_previous_and_next_articles = lambda localid: (None, None)
        view.get_object = unittest.mock.MagicMock(return_value=article)
        context = view.get_context_data()

        # Run the XSL transformation.
        return view.render_xml_content(context)

    def test_can_transform_article_xml_to_html(self):
        ret = self.render_article_detail_html()

        # Check
        assert ret is not None
        assert ret.startswith('<div class="article-wrapper">')

    @unittest.mock.patch.object(ArticleDigitalObject, 'pdf')
    def test_can_transform_article_xml_to_html_when_pdf_exists(self, mock_pdf):
        # Setup
        fp = open(FIXTURE_ROOT + '/article.pdf', mode='rb')
        mock_pdf.exists = True
        mock_pdf.content = fp

        # Run
        ret = self.render_article_detail_html()

        # Check
        fp.close()
        assert ret is not None

    def test_html_tags_in_transformed_article_biblio_titles(self):
        ret = self.render_article_detail_html()
        # Check that HTML tags in biblio titles are not stripped.

        assert '<h3 class="titre">H3 avec balise <strong>strong</strong>\n</h3>' in ret
        assert '<h4 class="titre">H4 avec balise <em>em</em>\n</h4>' in ret
        assert '<h5 class="titre">H5 avec balise <small>small</small>\n</h5>' in ret

    def test_footnotes_in_section_titles_not_in_toc(self):
        ret = self.render_article_detail_html('1053699ar.xml')

        # Check that footnotes in section titles are stripped when displayed in
        # table of content and not stripped when displayed as section titles.
        assert '<a href="#s1n1">Titre</a>' in ret
        assert '<h2>Titre<a href="#no1" id="re1no1" class="norenvoi" title="Note 1, avec espace entre deux marquages">[1]</a>\n</h2>' in ret

        assert '<a href="#s1n2"><strong>Titre gras</strong></a>' in ret
        assert '<h2><strong>Titre gras<a href="#no2" id="re1no2" class="norenvoi" title="Lien à encoder">[2]</a></strong></h2>' in ret

        assert '<a href="#s1n3"><em>Titre italique</em></a>' in ret
        assert '<h2><em>Titre italique<a href="#no3" id="re1no3" class="norenvoi" title="Lien déjà encodé">[3]</a></em></h2>' in ret

        assert '<a href="#s1n4"><span class="petitecap">Titre petitecap</span></a>' in ret
        assert '<h2><span class="petitecap">Titre petitecap<a href="#no4" id="re1no4" class="norenvoi" title="">[4]</a></span></h2>' in ret

    def test_space_between_two_tags(self):
        ret = self.render_article_detail_html('1053699ar.xml')

        # Check that the space is preserved between two tags.
        assert '<span class="petitecap">Note 1,</span> <em>avec espace entre deux marquages</em>' in ret

    def test_blockquote_between_two_spans(self):
        ret = self.render_article_detail_html('1053699ar.xml')

        # Check that the blockquote is displayed before the second paragraph.
        assert '<blockquote class="bloccitation ">\n<p class="alinea">Citation</p>\n<cite class="source">Source</cite>\n</blockquote>\n<p class="alinea">Paragraphe</p>' in ret

    def test_annexes_footnotes(self):
        ret = self.render_article_detail_html('1035294ar.xml')

        # Check that annexes have an ID set.
        assert '<div id="an1" class="article-section-content" role="complementary">' in ret
        assert '<div id="an2" class="article-section-content" role="complementary">' in ret
        assert '<div id="an3" class="article-section-content" role="complementary">' in ret
        # Check that footnotes are linked to the annexes IDs.
        assert '<a href="#an1" id="" class="norenvoi" title="">[2]</a>' in ret
        assert '<a href="#an2" id="" class="norenvoi" title="">[ii]</a>' in ret
        assert '<a href="#an3" id="" class="norenvoi" title="">[**]</a>' in ret
        # Check that footnotes are not wrapped in <sup>.
        assert '<sup><a href="#an1" id="" class="norenvoi" title="">[2]</a></sup>' not in ret
        assert '<sup><a href="#an2" id="" class="norenvoi" title="">[ii]</a></sup>' not in ret
        assert '<sup><a href="#an3" id="" class="norenvoi" title="">[**]</a></sup>' not in ret

    def test_space_between_keywords_and_colon(self):
        ret = self.render_article_detail_html('1055726ar.xml')

        # Check that a space is present before the colon in French, but not in the other languages.
        assert 'Mots-clés :' in ret
        assert 'Keywords:' in ret
        assert 'Palabras clave:' in ret

    def test_article_titles_css_class(self):
        ret = self.render_article_detail_html('1055651ar.xml')
        # A normal title should not have any class.
        assert '<h2>La synthèse hoguettienne</h2>' in ret
        # A special character title should have the 'special' class.
        assert '<h2 class="special">*</h2>' in ret
        ret = self.render_article_detail_html('1055648ar.xml')
        # An empty title should have the 'special' and 'empty' classes and should be empty.
        assert '<h2 class="special empty"></h2>' in ret

    def test_volumaison_punctuation(self):
        ret = self.render_article_detail_html('1053504ar.xml')
        # There should be an hyphen between multiple months and no coma between month and year.
        assert '<p class="refpapier"><span class="volumaison"><span class="nonumero">Numéro 179</span>, Janvier–Avril 2018</span>, p. 1–2</p>' in ret

    def test_volumaison_with_multiple_numbers(self):
        ret = self.render_article_detail_html('1067490ar.xml')
        # There should be an hyphen between multiple numbers and a coma between numbers and period.
        assert '<p class="refpapier"><span class="volumaison"><span class="volume">Volume\xa028</span>, <span class="nonumero">Numéro\xa02–3</span>, Printemps 2018</span>, p.\xa07–9' in ret

    def test_separator_between_sections_in_different_languages(self):
        ret = self.render_article_detail_html('1046558ar.xml')
        # There should not be a separator before the first section.
        assert '<hr>\n<section id="s1n1"><div class="para" id="pa1">' not in ret
        # There should be a separator before sections in different languages.
        assert '<hr>\n<section id="s1n2"><div class="para" id="pa11">' in ret
        assert '<hr>\n<section id="s1n3"><div class="para" id="pa21">' in ret

    def test_multilingual_titreparal_and_sstitreparal_order(self):
        ret = self.render_article_detail_html('1058157ar.xml')
        # Check that titreparal and sstitreparal are in the right order.
        assert '<h1 class="doc-head__title">\n<span class="titre">Introduction au dossier spécial</span><span class="sstitre">À la découverte du lien organisationnel : avez-vous lu A. O. Hirschman ?</span><span class="titreparal">Introduction to the special section</span><span class="sstitreparal">Exploring the Organizational Link: Have You Read A. O.\n        Hirschman?</span><span class="titreparal">Introducción Dossier Especial</span><span class="sstitreparal">Descubriendo las relaciones organizativas: ¿leyó a A.O.\n        Hirschman?</span>\n</h1>' in ret


class TestGoogleScholarSubscribersView:

    @pytest.mark.parametrize('google_scholar_opt_out, expected_subscribers', [
        (False, {
            1: {
                'institution': 'foo',
                'ip_ranges': [
                    ['0.0.0.0', '255.255.255.255'],
                ],
            },
        }),
        (True, {}),
    ])
    def test_google_scholar_subscribers(self, google_scholar_opt_out, expected_subscribers):
        JournalAccessSubscriptionFactory(
            pk=1,
            post__ip_start='0.0.0.0',
            post__ip_end='255.255.255.255',
            post__valid=True,
            organisation__name='foo',
            organisation__google_scholar_opt_out=google_scholar_opt_out,
        )
        view = GoogleScholarSubscribersView()
        context = view.get_context_data()
        assert context.get('subscribers') == expected_subscribers


class TestGoogleScholarSubscriberJournalsView:

    @pytest.mark.parametrize('google_scholar_opt_out, subscription_id, expected_journal_ids', [
        (False, '1', ['journal_1']),
        (False, '', ['journal_1', 'journal_2']),
        (True, '1', []),
    ])
    def test_google_scholar_subscriber_journals(self, google_scholar_opt_out, subscription_id, expected_journal_ids):
        journal_1 = JournalFactory(localidentifier='journal_1')
        journal_2 = JournalFactory(localidentifier='journal_2')
        JournalAccessSubscriptionFactory(
            pk=1,
            post__journals=[journal_1],
            organisation__google_scholar_opt_out=google_scholar_opt_out,
        )
        view = GoogleScholarSubscriberJournalsView()
        context = view.get_context_data(subscription_id=subscription_id)
        assert [journal.localidentifier for journal in context.get('journals')] == expected_journal_ids


class TestJournalStatisticsView:

    @pytest.mark.parametrize('is_staff, is_superuser, has_permission', [
        (True, True, True),
        (True, False, True),
        (False, True, True),
        (False, False, False),
    ])
    def test_journal_statistics_view_access(self, is_staff, is_superuser, has_permission):
        view = JournalStatisticsView()
        view.request = unittest.mock.MagicMock()
        view.request.user = UserFactory(
            is_staff=is_staff,
            is_superuser=is_superuser,
        )
        assert view.has_permission() == has_permission


class TestArticleDetailView:
    @pytest.mark.parametrize(
        "publication_allowed, content_access_granted, processing, expected_access_type",
        (
            (False, True, Article.PROCESSING_FULL, ArticleAccessType.content_not_available),
            (False, True, Article.PROCESSING_MINIMAL, ArticleAccessType.content_not_available),
            (False, False, Article.PROCESSING_FULL, ArticleAccessType.content_not_available),
            (False, False, Article.PROCESSING_MINIMAL, ArticleAccessType.content_not_available),
            (True, True, Article.PROCESSING_FULL, ArticleAccessType.html_full_view),
            (True, True, Article.PROCESSING_MINIMAL, ArticleAccessType.html_full_view_pdf_embedded),
            (True, False, Article.PROCESSING_FULL, ArticleAccessType.html_preview),
            (True, False, Article.PROCESSING_MINIMAL, ArticleAccessType.html_preview_pdf_embedded),
        ),
    )
    def test_get_access_type(
        self,
        publication_allowed,
        content_access_granted,
        processing,
        expected_access_type,
        monkeypatch,
    ):
        monkeypatch.setattr(ArticleDetailView, "get_object", unittest.mock.MagicMock(
           return_value=ArticleFactory(),
        ))
        monkeypatch.setattr(ArticleDetailView, "content_access_granted", content_access_granted)
        monkeypatch.setattr(Article, "publication_allowed", publication_allowed)
        monkeypatch.setattr(Article, "processing", processing)
        assert ArticleDetailView().get_access_type() == expected_access_type


class TestArticleSummaryView:
    @pytest.mark.parametrize("publication_allowed, processing, expected_access_type", (
        (False, Article.PROCESSING_FULL, ArticleAccessType.content_not_available),
        (False, Article.PROCESSING_MINIMAL, ArticleAccessType.content_not_available),
        (True, Article.PROCESSING_FULL, ArticleAccessType.html_preview),
        (True, Article.PROCESSING_MINIMAL, ArticleAccessType.html_preview_pdf_embedded),
    ))
    def test_get_access_type(
        self, publication_allowed, processing, expected_access_type, monkeypatch,
    ):
        monkeypatch.setattr(ArticleSummaryView, "get_object", unittest.mock.MagicMock(
           return_value=ArticleFactory(),
        ))
        monkeypatch.setattr(Article, "publication_allowed", publication_allowed)
        monkeypatch.setattr(Article, "processing", processing)
        assert ArticleSummaryView().get_access_type() == expected_access_type


class TestArticleBiblioView:
    @pytest.mark.parametrize("publication_allowed, expected_access_type", (
        (False, ArticleAccessType.content_not_available),
        (True, ArticleAccessType.html_biblio),
    ))
    def test_get_access_type(self, publication_allowed, expected_access_type, monkeypatch):
        monkeypatch.setattr(ArticleBiblioView, "get_object", unittest.mock.MagicMock(
           return_value=ArticleFactory(),
        ))
        monkeypatch.setattr(Article, "publication_allowed", publication_allowed)
        assert ArticleBiblioView().get_access_type() == expected_access_type


class TestArticleTocView:
    @pytest.mark.parametrize("publication_allowed, expected_access_type", (
        (False, ArticleAccessType.content_not_available),
        (True, ArticleAccessType.html_toc),
    ))
    def test_get_access_type(self, publication_allowed, expected_access_type, monkeypatch):
        monkeypatch.setattr(ArticleTocView, "get_object", unittest.mock.MagicMock(
           return_value=ArticleFactory(),
        ))
        monkeypatch.setattr(Article, "publication_allowed", publication_allowed)
        assert ArticleTocView().get_access_type() == expected_access_type


class TestArticleXmlView:
    @pytest.mark.parametrize("publication_allowed, expected_access_type", (
        (False, ArticleAccessType.content_not_available),
        (True, ArticleAccessType.xml_full_view),
    ))
    def test_get_access_type(self, publication_allowed, expected_access_type, monkeypatch):
        monkeypatch.setattr(ArticleXmlView, "get_object", unittest.mock.MagicMock(
           return_value=ArticleFactory(),
        ))
        monkeypatch.setattr(Article, "publication_allowed", publication_allowed)
        assert ArticleXmlView().get_access_type() == expected_access_type


class TestArticleRawPdfView:
    @pytest.mark.parametrize("publication_allowed, data, expected_access_type", (
        (False, {}, ArticleAccessType.content_not_available),
        (False, {"embed": ""}, ArticleAccessType.content_not_available),
        (True, {}, ArticleAccessType.pdf_full_view),
        (True, {"embed": ""}, ArticleAccessType.pdf_full_view_embedded),
    ))
    def test_get_access_type(self, publication_allowed, data, expected_access_type, monkeypatch):
        monkeypatch.setattr(ArticleRawPdfView, "get_object", unittest.mock.MagicMock(
           return_value=ArticleFactory(),
        ))
        monkeypatch.setattr(Article, "publication_allowed", publication_allowed)
        view = ArticleRawPdfView()
        view.request = RequestFactory()
        view.request.GET = data
        assert view.get_access_type() == expected_access_type


class TestArticleRawPdfFirstPageView:
    @pytest.mark.parametrize("publication_allowed, data, expected_access_type", (
        (False, {}, ArticleAccessType.content_not_available),
        (False, {"embed": ""}, ArticleAccessType.content_not_available),
        (True, {}, ArticleAccessType.pdf_preview),
        (True, {"embed": ""}, ArticleAccessType.pdf_preview_embedded),
    ))
    def test_get_access_type(self, publication_allowed, data, expected_access_type, monkeypatch):
        monkeypatch.setattr(ArticleRawPdfFirstPageView, "get_object", unittest.mock.MagicMock(
           return_value=ArticleFactory(),
        ))
        monkeypatch.setattr(Article, "publication_allowed", publication_allowed)
        view = ArticleRawPdfFirstPageView()
        view.request = RequestFactory()
        view.request.GET = data
        assert view.get_access_type() == expected_access_type


class TestArticleMediaView:
    @pytest.mark.parametrize('is_published', (True, False))
    @unittest.mock.patch('erudit.fedora.views.generic.get_cached_datastream_content')
    def test_cache_unpublished_issue_article_medias(self, mock_get_cached_datastream_content, is_published):
        article = ArticleFactory(
            localidentifier='article',
            issue__is_published=is_published,
            issue__localidentifier='issue',
            issue__journal__code='journal',
        )
        view = ArticleMediaView()
        view.kwargs = {
            'media_localid': '1234n.jpg',
            'localidentifier': article.localidentifier,
            'issue_localid': article.issue.localidentifier,
            'journal_code': article.issue.journal.code,
        }
        view.get_object = unittest.mock.MagicMock(return_value=article)
        view.get_datastream_content(unittest.mock.MagicMock())
        assert mock_get_cached_datastream_content.call_count == True
