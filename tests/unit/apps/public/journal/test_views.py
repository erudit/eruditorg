import datetime as dt
import os
import pytest
import unittest.mock

from bs4 import BeautifulSoup
from django.http import Http404
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from base.test.factories import UserFactory
from erudit.test.factories import ArticleFactory, IssueFactory, JournalFactory, \
    JournalInformationFactory, ContributorFactory
from erudit.fedora import repository
from erudit.fedora.objects import ArticleDigitalObject
from erudit.models import Issue
from erudit.test.domchange import SectionTitle
from apps.public.journal.views import JournalDetailView, IssueDetailView, ArticleDetailView, \
    GoogleScholarSubscribersView, GoogleScholarSubscriberJournalsView, JournalStatisticsView, \
    IssueReaderView
from core.subscription.test.factories import JournalAccessSubscriptionFactory
from core.subscription.test.utils import generate_casa_token

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
                {'langue': 'fr', 'content': 'foobar'},
                {'langue': 'en', 'content': 'foobaz'}
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
        assert 'Marie-Claude Loiselle (Rédactrice en chef)' in html
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
        assert 'Foo (Bar)' in html

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
        issue = IssueFactory()
        repository.api.set_xml_for_pid(
            issue.journal.get_full_identifier(),
            open('tests/fixtures/journal/recma0448.xml', 'rb').read(),
        )
        url = reverse('public:journal:journal_detail', kwargs={
            'code': issue.journal.code,
        })
        html = Client().get(url).content.decode()
        assert 'Cette revue a cessé de publier ses numéros sur Érudit depuis 2016, vous pouvez consulter les numéros subséquents sur <a href="https://www.cairn.info/revue-recma.htm">Cairn</a>' in html


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
        # When an issue is not published, the only cache.get() call we should get is for the
        # journal. No cache.get() should be called for the issue or the articles.
        (False, 1),
        # When an issue is published, cache.get() should be called once for the journal, once for
        # the issue and once for each article. There's an extra cache.get() call on the first
        # article from the is_external() method on the issue, hance the 4 expected count.
        (True, 4),
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


class TestArticleDetailView:

    @unittest.mock.patch('erudit.fedora.cache.cache')
    @unittest.mock.patch('erudit.fedora.cache.get_datastream_file_cache')
    @unittest.mock.patch('erudit.fedora.cache.get_cached_datastream_content')
    @pytest.mark.parametrize('is_published, expected_count', [
        # When an issue is not published, we should not get any cache.get() calls when displaying
        # an article's PDF.
        (False, 0),
        # When an issue is published, we should get one cache.get() calls when displaying an
        # article's PDF.
        (True, 1),
    ])
    def test_pdf_datastream_caching(self, mock_cache, mock_get_datastream_file_cache, mock_get_cached_datastream_content, is_published, expected_count):
        mock_cache.get.return_value = None
        mock_get_datastream_file_cache.return_value = mock_cache
        mock_get_cached_datastream_content.return_value = None

        article = ArticleFactory(
            issue__is_published=is_published,
            issue__journal__open_access=True,
        )
        url = reverse('public:journal:article_raw_pdf', kwargs={
            'journal_code': article.issue.journal.code,
            'issue_slug': article.issue.volume_slug,
            'issue_localid': article.issue.localidentifier,
            'localid': article.localidentifier,
        })
        mock_cache.get.reset_mock()

        response = Client().get(url, {
            'ticket': article.issue.prepublication_ticket,
        })
        assert mock_cache.get.call_count == expected_count

    @unittest.mock.patch('erudit.fedora.modelmixins.cache')
    @pytest.mark.parametrize('is_published, expected_count', [
        # When an issue is not published, we should not get any cache.get() calls when displaying
        # an article's XML.
        (False, 0),
        # When an issue is published, we should get one cache.get() calls when displaying an
        # article's XML.
        (True, 1),
    ])
    def test_xml_datastream_caching(self, mock_cache, is_published, expected_count):
        mock_cache.get.return_value = None

        article = ArticleFactory(
            issue__is_published=is_published,
            issue__journal__open_access=True,
        )
        url = reverse('public:journal:article_raw_xml', kwargs={
            'journal_code': article.issue.journal.code,
            'issue_slug': article.issue.volume_slug,
            'issue_localid': article.issue.localidentifier,
            'localid': article.localidentifier,
        })
        mock_cache.get.reset_mock()

        response = Client().get(url, {
            'ticket': article.issue.prepublication_ticket,
        })
        assert mock_cache.get.call_count == expected_count

    def test_that_article_titles_are_truncated_in_breadcrumb(self):
        article = ArticleFactory(
            from_fixture='1056823ar',
            localidentifier='article',
            issue__localidentifier='issue',
            issue__year='2000',
            issue__journal__code='journal',
        )
        url = reverse('public:journal:article_detail', kwargs={
            'journal_code': article.issue.journal.code,
            'issue_slug': article.issue.volume_slug,
            'issue_localid': article.issue.localidentifier,
            'localid': article.localidentifier,
        })
        response = Client().get(url)
        html = response.content.decode()
        assert '<a href="/fr/revues/journal/2000-issue/article/">Jean-Guy Desjardins, Traité de l’évaluation foncière, Montréal, Wilson &amp; Lafleur ...</a>' in html  # noqa

    def test_keywords_html_tags(self):
        article = ArticleFactory(from_fixture='1055883ar')
        url = reverse('public:journal:article_detail', kwargs={
            'journal_code': article.issue.journal.code,
            'issue_slug': article.issue.volume_slug,
            'issue_localid': article.issue.localidentifier,
            'localid': article.localidentifier,
        })
        response = Client().get(url)
        html = response.content.decode()
        # Check that HTML tags are displayed in the body.
        assert '<ul>\n<li class="keyword">Charles Baudelaire, </li>\n<li class="keyword">\n<em>Fleurs du Mal</em>, </li>\n<li class="keyword">Seine, </li>\n<li class="keyword">mythe et réalité de Paris, </li>\n<li class="keyword">poétique du miroir</li>\n</ul>' in html  # noqa
        # Check that HTML tags are not displayed in the head.
        assert '<meta name="citation_keywords" lang="fr" content="Charles Baudelaire, Fleurs du Mal, Seine, mythe et réalité de Paris, poétique du miroir" />' in html

    def test_article_pdf_links(self):
        article = ArticleFactory(
            with_pdf=True,
            from_fixture='602354ar',
            localidentifier='602354ar',
            issue__year='2000',
            issue__localidentifier='issue',
            issue__is_published=False,
            issue__journal__code='journal',
            issue__journal__open_access=True,
        )
        url = reverse('public:journal:article_detail', kwargs={
            'journal_code': article.issue.journal.code,
            'issue_slug': article.issue.volume_slug,
            'issue_localid': article.issue.localidentifier,
            'localid': article.localidentifier,
        })
        response = Client().get(url, {
            'ticket': article.issue.prepublication_ticket if not article.issue.is_published else '',
        })
        html = response.content.decode()

        # Check that the PDF download button URL has the prepublication ticket if the issue is not published.
        assert '<a class="tool-btn tool-download" data-href="/fr/revues/journal/2000-issue/602354ar.pdf?ticket=0aae4c8f3cc35693d0cbbe631f2e8b52"><span class="toolbox-pdf">PDF</span><span class="tools-label">Télécharger</span></a>' in html
        # Check that the PDF menu link URL has the prepublication ticket if the issue is not published.
        assert '<a href="#pdf-viewer" id="pdf-viewer-menu-link">Texte intégral (PDF)</a><a href="/fr/revues/journal/2000-issue/602354ar.pdf?ticket=0aae4c8f3cc35693d0cbbe631f2e8b52" id="pdf-download-menu-link" target="_blank">Texte intégral (PDF)</a>' in html
        # Check that the embeded PDF URL has the prepublication ticket if the issue is not published.
        assert '<object id="pdf-viewer" data="/fr/revues/journal/2000-issue/602354ar.pdf?embed&amp;ticket=0aae4c8f3cc35693d0cbbe631f2e8b52" type="application/pdf" width="100%" height="700px"></object>' in html
        # Check that the PDF download link URL has the prepublication ticket if the issue is not published.
        assert '<a href="/fr/revues/journal/2000-issue/602354ar.pdf?ticket=0aae4c8f3cc35693d0cbbe631f2e8b52" class="btn btn-secondary" target="_blank">Télécharger</a>' in html

        article.issue.is_published = True
        article.issue.save()
        response = Client().get(url)
        html = response.content.decode()

        # Check that the PDF download button URL does not have the prepublication ticket if the issue is published.
        assert '<a class="tool-btn tool-download" data-href="/fr/revues/journal/2000-issue/602354ar.pdf"><span class="toolbox-pdf">PDF</span><span class="tools-label">Télécharger</span></a>' in html
        # Check that the PDF menu link URL does not have the prepublication ticket if the issue is published.
        assert '<a href="#pdf-viewer" id="pdf-viewer-menu-link">Texte intégral (PDF)</a><a href="/fr/revues/journal/2000-issue/602354ar.pdf" id="pdf-download-menu-link" target="_blank">Texte intégral (PDF)</a>' in html
        # Check that the embeded PDF URL does not have the prepublication ticket if the issue is published.
        assert '<object id="pdf-viewer" data="/fr/revues/journal/2000-issue/602354ar.pdf?embed" type="application/pdf" width="100%" height="700px"></object>' in html
        # Check that the PDF download link URL does not have the prepublication ticket if the issue is published.
        assert '<a href="/fr/revues/journal/2000-issue/602354ar.pdf" class="btn btn-secondary" target="_blank">Télécharger</a>' in html

    @pytest.mark.parametrize('kwargs, nonce_count, authorized', (
        # Valid token
        ({}, 1, True),
        # Badly formed token
        ({'token_separator': '!'}, 1, False),
        # Invalid nonce
        ({'invalid_nonce': True}, 1, False),
        # Invalid message
        ({'invalid_message': True}, 1, False),
        # Invalid signature
        ({'invalid_signature': True}, 1, False),
        # Nonce seen more than 3 times
        ({}, 4, False),
        # Badly formatted payload
        ({'payload_separator': '!'}, 1, False),
        # Expired token
        ({'time_delta': 3600000001}, 1, False),
        # Wrong IP
        ({'ip_subnet': '8.8.8.0/24'}, 1, False),
        # Invalid subscription
        ({'subscription_id': 2}, 1, False),
    ))
    @pytest.mark.parametrize('url_name', (
        ('public:journal:article_detail'),
        ('public:journal:article_raw_pdf'),
    ))
    @unittest.mock.patch('core.subscription.middleware.SubscriptionMiddleware._nonce_count')
    @override_settings(GOOGLE_CASA_KEY='74796E8FF6363EFF91A9308D1D05335E')
    def test_article_detail_with_google_casa_token(self, mock_nonce_count, url_name, kwargs, nonce_count, authorized):
        mock_nonce_count.return_value = nonce_count
        article = ArticleFactory()
        subscription = JournalAccessSubscriptionFactory(
            pk=1,
            post__valid=True,
            post__journals=[article.issue.journal],
        )
        url = reverse(url_name, kwargs={
            'journal_code': article.issue.journal.code,
            'issue_slug': article.issue.volume_slug,
            'issue_localid': article.issue.localidentifier,
            'localid': article.localidentifier,
        })
        response = Client().get(url, {
            'casa_token': generate_casa_token(**kwargs),
        }, follow=True)
        html = response.content.decode()
        if authorized:
            assert 'Seuls les 600 premiers mots du texte seront affichés.' not in html
        else:
            assert 'Seuls les 600 premiers mots du texte seront affichés.' in html

    @pytest.mark.parametrize('url_name, fixture, display_biblio, display_pdf_first_page', (
        # Complete treatment articles should always display a bibliography
        ('public:journal:article_biblio', '009256ar', 1, 0),
        ('public:journal:article_summary', '009256ar', 1, 0),
        ('public:journal:article_detail', '009256ar', 1, 0),
        # Retro minimal treatment articles should only display a bibliography in article_biblio view
        ('public:journal:article_biblio', '1058447ar', 1, 0),
        ('public:journal:article_summary', '1058447ar', 0, 1),
        ('public:journal:article_detail', '1058447ar', 0, 1),
    ))
    def test_biblio_references_display(self, url_name, fixture, display_biblio, display_pdf_first_page):
        article = ArticleFactory(
            from_fixture=fixture,
            with_pdf=True,
        )
        url = reverse(url_name, kwargs={
            'journal_code': article.issue.journal.code,
            'issue_slug': article.issue.volume_slug,
            'issue_localid': article.issue.localidentifier,
            'localid': article.localidentifier,
        })
        html = Client().get(url).content.decode()
        assert html.count('<section id="grbiblio" class="article-section grbiblio" role="complementary">') == display_biblio
        # Minimal treatment articles should not display PDF first page when displaying references.
        assert html.count('<object id="pdf-viewer"') == display_pdf_first_page

    def test_article_detail_marquage_in_toc_nav(self):
        issue = IssueFactory(
            journal__code='journal',
            localidentifier='issue',
            year='2000',
        )
        prev_article = ArticleFactory(
            from_fixture='1054008ar',
            localidentifier='prev_article',
            issue=issue,
        )
        article = ArticleFactory(
            issue=issue,
        )
        next_article = ArticleFactory(
            from_fixture='1054008ar',
            localidentifier='next_article',
            issue=issue,
        )
        url = reverse('public:journal:article_detail', kwargs={
            'journal_code': article.issue.journal.code,
            'issue_slug': article.issue.volume_slug,
            'issue_localid': article.issue.localidentifier,
            'localid': article.localidentifier,
        })
        response = Client().get(url)
        html = response.content.decode()
        # Check that TOC navigation titles include converted marquage.
        assert '<a href="/fr/revues/journal/2000-issue/prev_article/" class="toc-nav__prev" title="Article précédent"><span class="toc-nav__arrow">&lt;--</span><h4 class="toc-nav__title">\n        L’action et le verbe dans <em>Feuillets d’Hypnos</em>\n</h4></a>' in html  # noqa
        assert '<a href="/fr/revues/journal/2000-issue/next_article/" class="toc-nav__next" title="Article suivant"><span class="toc-nav__arrow">--&gt;</span><h4 class="toc-nav__title">\n        L’action et le verbe dans <em>Feuillets d’Hypnos</em>\n</h4></a>' in html  # noqa

    def test_surtitre_not_split_in_multiple_spans(self):
        article = ArticleFactory(
            from_fixture='1056389ar',
        )
        url = reverse('public:journal:article_detail', kwargs={
            'journal_code': article.issue.journal.code,
            'issue_slug': article.issue.volume_slug,
            'issue_localid': article.issue.localidentifier,
            'localid': article.localidentifier,
        })
        response = Client().get(url)
        html = response.content.decode()
        assert '<span class="surtitre">Cahier commémoratif : 25<sup>e</sup> anniversaire</span>' in html

    def test_title_and_paral_title_are_displayed(self):
        article = ArticleFactory(
            from_fixture='1058368ar',
        )
        url = reverse('public:journal:article_detail', kwargs={
            'journal_code': article.issue.journal.code,
            'issue_slug': article.issue.volume_slug,
            'issue_localid': article.issue.localidentifier,
            'localid': article.localidentifier,
        })
        response = Client().get(url)
        html = response.content.decode()
        assert '<span class="titre">Les Parcs Nationaux de Roumanie : considérations sur les habitats Natura 2000 et sur les réserves IUCN</span>' in html
        assert '<span class="titreparal">The National Parks of Romania: considerations on Natura 2000 habitats and IUCN reserves</span>' in html

    def test_article_detail_view_with_untitled_article(self):
        article = ArticleFactory(
            from_fixture='1042058ar',
            localidentifier='article',
            issue__year='2000',
            issue__localidentifier='issue',
            issue__journal__code='journal',
            issue__journal__name='Revue',
        )
        url = reverse('public:journal:article_detail', kwargs={
            'journal_code': article.issue.journal.code,
            'issue_slug': article.issue.volume_slug,
            'issue_localid': article.issue.localidentifier,
            'localid': article.localidentifier,
        })
        html = Client().get(url).content.decode()
        # Check that "[Article sans titre]" is displayed in the header title.
        assert '<title>[Article sans titre] – Revue – Érudit</title>' in html
        # Check that "[Article sans titre]" is displayed in the body title.
        assert '<h1 class="doc-head__title"><span class="titre">[Article sans titre]</span></h1>' in html
        # Check that "[Article sans titre]" is displayed in the breadcrumbs.
        assert '<li>\n  <a href="/fr/revues/journal/2000-issue/article/">[Article sans titre]</a>\n</li>' in html

    def test_article_authors_with_suffixes(self):
        article = ArticleFactory(
            from_fixture='1058611ar',
        )
        url = reverse('public:journal:article_detail', kwargs={
            'journal_code': article.issue.journal.code,
            'issue_slug': article.issue.volume_slug,
            'issue_localid': article.issue.localidentifier,
            'localid': article.localidentifier,
        })
        html = Client().get(url).content.decode()
        # Check that authors' suffixes are not displayed on the the author list under the article title.
        assert '<li class="auteur doc-head__author">\n<span class="nompers">André\n      Ngamini-Ngui</span> et </li>' in html
        # Check that authors' suffixes are displayed on the 'more information' section.
        assert '<li class="auteur-affiliation"><p><strong>André\n      Ngamini-Ngui, †</strong></p></li>' in html

    def test_figure_groups_source_display(self):
        article = ArticleFactory(
            from_fixture='1058470ar',
            localidentifier='article',
            issue__year='2000',
            issue__localidentifier='issue',
            issue__journal__code='journal',
            issue__journal__open_access=True,
        )
        url = reverse('public:journal:article_detail', kwargs={
            'journal_code': article.issue.journal.code,
            'issue_slug': article.issue.volume_slug,
            'issue_localid': article.issue.localidentifier,
            'localid': article.localidentifier,
        })
        html = Client().get(url).content.decode()
        # Check that the source is displayed under both figures 1 & 2 which are in the same figure group.
        assert '<figure class="figure" id="fi1"><figcaption></figcaption><div class="figure-wrapper">\n<div class="figure-object"><a href="/fr/revues/journal/2000-issue/article/media/" class="lightbox objetmedia" title=""><img src="/fr/revues/journal/2000-issue/article/media/" alt="" class="img-responsive"></a></div>\n<div class="figure-legende-notes-source"><cite class="source">Avec l’aimable autorisation de l’artiste et kamel mennour, Paris/London. © <em>ADAGP Mohamed Bourouissa</em></cite></div>\n</div>\n<p class="voirliste"><a href="#ligf1">-&gt; Voir la liste des figures</a></p></figure>' in html
        assert '<figure class="figure" id="fi2"><figcaption></figcaption><div class="figure-wrapper">\n<div class="figure-object"><a href="/fr/revues/journal/2000-issue/article/media/" class="lightbox objetmedia" title=""><img src="/fr/revues/journal/2000-issue/article/media/" alt="" class="img-responsive"></a></div>\n<div class="figure-legende-notes-source"><cite class="source">Avec l’aimable autorisation de l’artiste et kamel mennour, Paris/London. © <em>ADAGP Mohamed Bourouissa</em></cite></div>\n</div>\n<p class="voirliste"><a href="#ligf1">-&gt; Voir la liste des figures</a></p></figure>' in html

    def test_table_groups_display(self):
        article = ArticleFactory(
            from_fixture='1061713ar',
            localidentifier='article',
            issue__year='2000',
            issue__localidentifier='issue',
            issue__journal__code='journal',
            issue__journal__open_access=True,
        )
        url = reverse('public:journal:article_detail', kwargs={
            'journal_code': article.issue.journal.code,
            'issue_slug': article.issue.volume_slug,
            'issue_localid': article.issue.localidentifier,
            'localid': article.localidentifier,
        })
        html = Client().get(url).content.decode()
        dom = BeautifulSoup(html, 'html.parser')
        grtableau = dom.find_all('div', {'class': 'grtableau'})[0]
        figures = grtableau.find_all('figure')
        # Check that the table group is displayed.
        assert grtableau.attrs.get('id') == 'gt1'
        # Check that the tables are displayed inside the table group.
        assert figures[0].attrs.get('id') == 'ta2'
        assert figures[1].attrs.get('id') == 'ta3'
        assert figures[2].attrs.get('id') == 'ta4'
        # Check that the table images are displayed inside the tables.
        assert len(figures[0].find_all('img', {'class': 'img-responsive'})) == 1
        assert len(figures[1].find_all('img', {'class': 'img-responsive'})) == 1
        assert len(figures[2].find_all('img', {'class': 'img-responsive'})) == 1
        # Check that the table legends are displayed inside the tables.
        assert len(figures[0].find_all('p', {'class': 'alinea'})) == 1
        assert len(figures[1].find_all('p', {'class': 'alinea'})) == 2
        assert len(figures[2].find_all('p', {'class': 'alinea'})) == 4

    def test_table_groups_display_with_table_no(self):
        article = ArticleFactory(
            from_fixture='1060065ar',
            localidentifier='article',
            issue__year='2000',
            issue__localidentifier='issue',
            issue__journal__code='journal',
            issue__journal__open_access=True,
        )
        url = reverse('public:journal:article_detail', kwargs={
            'journal_code': article.issue.journal.code,
            'issue_slug': article.issue.volume_slug,
            'issue_localid': article.issue.localidentifier,
            'localid': article.localidentifier,
        })
        html = Client().get(url).content.decode()
        dom = BeautifulSoup(html, 'html.parser')
        grtableau = dom.find_all('div', {'class': 'grtableau'})[0]
        figures = grtableau.find_all('figure')
        # Check that the table group is displayed.
        assert grtableau.attrs.get('id') == 'gt1'
        # Check that the tables are displayed inside the table group.
        assert figures[0].attrs.get('id') == 'ta2'
        assert figures[1].attrs.get('id') == 'ta3'
        # Check that the table numbers are displayed.
        assert figures[0].find_all('p', {'class': 'no'})[0].text == '2A'
        assert figures[1].find_all('p', {'class': 'no'})[0].text == '2B'

    def test_figure_back_arrow_is_displayed_when_theres_no_number_or_title(self):
        article = ArticleFactory(
            from_fixture='1031003ar',
            issue__journal__open_access=True,
        )
        url = reverse('public:journal:article_detail', kwargs={
            'journal_code': article.issue.journal.code,
            'issue_slug': article.issue.volume_slug,
            'issue_localid': article.issue.localidentifier,
            'localid': article.localidentifier,
        })
        html = Client().get(url).content.decode()
        # Check that the arrow to go back to the figure is present event if there's no figure number or caption.
        assert '<figure class="tableau" id="lita7"><figcaption><p class="allertexte"><a href="#ta7">|^</a></p></figcaption>' in html

    def test_figure_groups_numbers_display_in_figure_list(self):
        article = ArticleFactory(
            from_fixture='1058470ar',
            localidentifier='article',
            issue__year='2000',
            issue__localidentifier='issue',
            issue__journal__code='journal',
            issue__journal__open_access=True,
        )
        url = reverse('public:journal:article_detail', kwargs={
            'journal_code': article.issue.journal.code,
            'issue_slug': article.issue.volume_slug,
            'issue_localid': article.issue.localidentifier,
            'localid': article.localidentifier,
        })
        html = Client().get(url).content.decode()
        # Check that the figure numbers are displayed in the figure list for figure groups.
        assert '<div class="grfigure" id="ligf1">\n<div class="grfigure-caption">\n<p class="allertexte"><a href="#gf1">|^</a></p>\n<p class="no">Figures 1 - 2</p>' in html

    def test_figcaption_display_for_figure_groups_and_figures(self):
        article = ArticleFactory(
            from_fixture='1060169ar',
            issue__journal__open_access=True,
        )
        url = reverse('public:journal:article_detail', kwargs={
            'journal_code': article.issue.journal.code,
            'issue_slug': article.issue.volume_slug,
            'issue_localid': article.issue.localidentifier,
            'localid': article.localidentifier,
        })
        html = Client().get(url).content.decode()
        # Check that figure group caption and the figure captions are displayed.
        assert '<div class="grfigure-caption">\n<p class="allertexte"><a href="#gf1">|^</a></p>\n<p class="no">Figure 1</p>\n<div class="legende"><p class="legende"><strong class="titre">RMF frequencies in German data</strong></p></div>\n</div>' in html
        assert '<figcaption><p class="legende"><strong class="titre">German non-mediated</strong></p></figcaption>' in html
        assert '<figcaption><p class="legende"><strong class="titre">German interpreted</strong></p></figcaption>' in html

    def test_article_multilingual_titles(self):
        article = ArticleFactory(
            from_fixture='1059303ar',
        )
        url = reverse('public:journal:article_detail', kwargs={
            'journal_code': article.issue.journal.code,
            'issue_slug': article.issue.volume_slug,
            'issue_localid': article.issue.localidentifier,
            'localid': article.localidentifier,
        })
        html = Client().get(url).content.decode()
        # Check that paral titles are displayed in the article header.
        assert '<span class="titreparal">Détection d’ADN d’<em>Ophiostoma ulmi</em> introgressé naturellement        dans les régions entourant les loci contrôlant la pathogénie et le type sexuel chez        <em>O. novo-ulmi</em></span>' in html  # noqa
        # Check that paral titles are not displayed in summary section.
        assert '<h4><span class="title">Détection d’ADN d’<em>Ophiostoma ulmi</em> introgressé naturellement dans les régions entourant les loci contrôlant la pathogénie et le type sexuel chez <em>O. novo-ulmi</em></span></h4>' not in html  # noqa

    def test_authors_more_information_for_author_with_suffix_and_no_affiliation(self):
        article = ArticleFactory(
            from_fixture='1059571ar',
        )
        url = reverse('public:journal:article_detail', kwargs={
            'journal_code': article.issue.journal.code,
            'issue_slug': article.issue.volume_slug,
            'issue_localid': article.issue.localidentifier,
            'localid': article.localidentifier,
        })
        html = Client().get(url).content.decode()
        # Check that more information akkordion is displayed for author with suffix and no affiliation.
        assert '<ul class="akkordion-content unstyled"><li class="auteur-affiliation"><p><strong>Guy\n      Sylvestre, o.c.</strong></p></li></ul>' in html

    def test_journal_multilingual_titles_in_citations(self):
        issue = IssueFactory()
        repository.api.set_publication_xml(
            issue.get_full_identifier(),
            open('tests/fixtures/issue/ri04376.xml', 'rb').read(),
        )
        article = ArticleFactory(
            localidentifier='article',
            issue=issue,
        )
        url = reverse('public:journal:article_detail', kwargs={
            'journal_code': article.issue.journal.code,
            'issue_slug': article.issue.volume_slug,
            'issue_localid': article.issue.localidentifier,
            'localid': article.localidentifier,
        })
        html = Client().get(url).content.decode()
        # Check that the journal name is displayed in French and English (Relations industrielles / Industrial Relations).
        assert '<dd id="id_cite_mla_article" class="cite-mla">\n        Pratt, Lynda. «&nbsp;Robert Southey, Writing and Romanticism.&nbsp;» <em>Relations industrielles / Industrial Relations</em>, volume 73, numéro 4, automne 2018. https://doi.org/10.7202/009255ar\n      </dd>' in html
        assert '<dd id="id_cite_apa_article" class="cite-apa">\n        Pratt, L. (2019). Robert Southey, Writing and Romanticism. <em>Relations industrielles / Industrial Relations</em>. https://doi.org/10.7202/009255ar\n      </dd>' in html
        assert '<dd id="id_cite_chicago_article" class="cite-chicago">\n        Pratt, Lynda «&nbsp;Robert Southey, Writing and Romanticism&nbsp;». <em>Relations industrielles / Industrial Relations</em> (2019). https://doi.org/10.7202/009255ar\n      </dd>' in html

    @pytest.mark.parametrize('fixture, url_name, expected_result', (
        # Multilingual journals should have all titles in citations.
        ('ri04376', 'public:journal:article_citation_enw', '%J Relations industrielles / Industrial Relations'),
        ('ri04376', 'public:journal:article_citation_ris', 'JO  - Relations industrielles / Industrial Relations'),
        ('ri04376', 'public:journal:article_citation_bib', 'journal="Relations industrielles / Industrial Relations",'),
        # Sub-titles should not be in citations.
        ('im03868', 'public:journal:article_citation_enw', '%J Intermédialités / Intermediality'),
        ('im03868', 'public:journal:article_citation_ris', 'JO  - Intermédialités / Intermediality'),
        ('im03868', 'public:journal:article_citation_bib', 'journal="Intermédialités / Intermediality'),
    ))
    def test_journal_multilingual_titles_in_article_citation_views(self, fixture, url_name, expected_result):
        issue = IssueFactory()
        repository.api.set_publication_xml(
            issue.get_full_identifier(),
            open('tests/fixtures/issue/{}.xml'.format(fixture), 'rb').read(),
        )
        article = ArticleFactory(
            issue=issue,
        )
        url = reverse(url_name, kwargs={
            'journal_code': article.issue.journal.code,
            'issue_slug': article.issue.volume_slug,
            'issue_localid': article.issue.localidentifier,
            'localid': article.localidentifier,
        })
        citation = Client().get(url).content.decode()
        # Check that the journal name is displayed in French and English (Relations industrielles / Industrial Relations).
        assert expected_result in citation

    def test_doi_with_extra_space(self):
        article = ArticleFactory(
            from_fixture='1009368ar',
        )
        url = reverse('public:journal:article_detail', kwargs={
            'journal_code': article.issue.journal.code,
            'issue_slug': article.issue.volume_slug,
            'issue_localid': article.issue.localidentifier,
            'localid': article.localidentifier,
        })
        html = Client().get(url).content.decode()
        # Check that extra space around DOIs is stripped.
        assert '<meta name="citation_doi" content="https://doi.org/10.7202/1009368ar" />' in html
        assert '<a href="https://doi.org/10.7202/1009368ar" class="clipboard-data">' in html

    def test_unicode_combining_characters(self):
        article = ArticleFactory(
            from_fixture='1059577ar',
        )
        url = reverse('public:journal:article_detail', kwargs={
            'journal_code': article.issue.journal.code,
            'issue_slug': article.issue.volume_slug,
            'issue_localid': article.issue.localidentifier,
            'localid': article.localidentifier,
        })
        html = Client().get(url).content.decode()
        # Pre-combined character is present (ă = ă)
        assert '<em>Studii de lingvistică</em>' in html
        # Combining character is not present (ă = a + ˘)
        assert '<em>Studii de lingvistică</em>' not in html

    def test_acknowledgements_and_footnotes_sections_order(self):
        article = ArticleFactory(
            from_fixture='1060048ar',
            issue__journal__open_access=True,
        )
        url = reverse('public:journal:article_detail', kwargs={
            'journal_code': article.issue.journal.code,
            'issue_slug': article.issue.volume_slug,
            'issue_localid': article.issue.localidentifier,
            'localid': article.localidentifier,
        })
        html = Client().get(url).content.decode()
        dom = BeautifulSoup(html, 'html.parser')
        partiesann = dom.find_all('section', {'class': 'partiesann'})[0]
        sections = partiesann.find_all('section')
        # Check that acknowledgements are displayed before footnotes.
        assert sections[0].attrs['id'] == 'merci'
        assert sections[1].attrs['id'] == 'grnote'

    def test_abstracts_and_keywords(self):
        article = ArticleFactory()
        with repository.api.open_article(article.pid) as wrapper:
            wrapper.set_abstracts([{'lang': 'fr', 'content': 'Résumé français'}])
            wrapper.set_abstracts([{'lang': 'en', 'content': 'English abstract'}])
            wrapper.add_keywords('es', ['Palabra clave en español'])
            wrapper.add_keywords('fr', ['Mot-clé français'])
        url = reverse('public:journal:article_detail', kwargs={
            'journal_code': article.issue.journal.code,
            'issue_slug': article.issue.volume_slug,
            'issue_localid': article.issue.localidentifier,
            'localid': article.localidentifier,
        })
        html = Client().get(url).content.decode()
        dom = BeautifulSoup(html, 'html.parser')
        grresume = dom.find_all('section', {'class': 'grresume'})[0]
        resumes = grresume.find_all('section', {'class': 'resume'})
        keywords = grresume.find_all('div', {'class': 'keywords'})
        # Make sure the main abstract (English) appears first, even though it's in second position in the XML.
        assert resumes[0].decode() == '<section class="resume" id="resume-en"><h3>Abstract</h3>\n<p class="alinea"><em>English abstract</em></p></section>'
        # Make sure the French keywords appear in the French abstract section.
        assert resumes[1].decode() == '<section class="resume" id="resume-fr"><h3>Résumé</h3>\n<p class="alinea"><em>Résumé français</em></p>\n<div class="keywords">\n<p><strong>Mots-clés :</strong></p>\n<ul><li class="keyword">Mot-clé français</li></ul>\n</div></section>'
        # Make sure the French keywords appear first since there is no English keywords and no Spanish abstract.
        assert keywords[0].decode() == '<div class="keywords">\n<p><strong>Mots-clés :</strong></p>\n<ul><li class="keyword">Mot-clé français</li></ul>\n</div>'
        # Make sure the Spanish keywords are displayed even though there is no Spanish abstract.
        assert keywords[1].decode() == '<div class="keywords">\n<p><strong>Palabras clave:</strong></p>\n<ul><li class="keyword">Palabra clave en español</li></ul>\n</div>'

    @pytest.mark.parametrize('article_type, expected_string', (
        ('compterendu', 'Un compte rendu de la revue'),
        ('article', 'Un article de la revue'),
    ))
    def test_review_article_explanatory_note(self, article_type, expected_string):
        article = ArticleFactory(type=article_type)
        url = reverse('public:journal:article_detail', kwargs={
            'journal_code': article.issue.journal.code,
            'issue_slug': article.issue.volume_slug,
            'issue_localid': article.issue.localidentifier,
            'localid': article.localidentifier,
        })
        html = Client().get(url).content.decode()
        dom = BeautifulSoup(html, 'html.parser')
        div = dom.find_all('div', {'class': 'doc-head__metadata'})[1]
        note = 'Ce document est le compte-rendu d\'une autre oeuvre tel qu\'un livre ou un film. L\'oeuvre originale discutée ici n\'est pas disponible sur cette plateforme.'
        assert expected_string in div.decode()
        if article_type == 'compterendu':
            assert note in div.decode()
        else:
            assert note not in div.decode()

    def test_verbatim_poeme_lines(self):
        article = ArticleFactory(
            from_fixture='1062061ar',
            issue__journal__open_access=True,
        )
        url = reverse('public:journal:article_detail', kwargs={
            'journal_code': article.issue.journal.code,
            'issue_slug': article.issue.volume_slug,
            'issue_localid': article.issue.localidentifier,
            'localid': article.localidentifier,
        })
        html = Client().get(url).content.decode()
        dom = BeautifulSoup(html, 'html.parser')
        poeme = dom.find('blockquote', {'class': 'verbatim poeme'})
        # Check that poems lines are displayed in <p>.
        assert poeme.decode() == '<blockquote class="verbatim poeme">\n<p class="ligne">Jour de larme, </p>\n<p class="ligne">jour où les coupables se réveilleront</p>\n<p class="ligne">pour entendre leur jugement,</p>\n<p class="ligne">alors, ô Dieu, pardonne-leur et leur donne le repos.</p>\n<p class="ligne">Jésus, accorde-leur le repos.</p>\n</blockquote>'



@unittest.mock.patch.object(
    Issue,
    'erudit_object',
)
@unittest.mock.patch.object(
    ArticleDigitalObject,
    'erudit_xsd300',
    content=unittest.mock.MagicMock()
)
@unittest.mock.patch.object(
    ArticleDigitalObject,
    '_get_datastreams',
    return_value=['ERUDITXSD300', ]
)
@unittest.mock.patch.object(
    Issue,
    'has_coverpage',
    return_value=True
)
class TestRenderArticleTemplateTag(TestCase):

    def mock_article_detail_view(
            self, mock_has_coverpage, mock_ds, mock_xsd300, mock_eo, fixture='article.xml'):
        """ Helper method to mock an article detail view from a given fixture."""
        with open(FIXTURE_ROOT + '/' + fixture, mode='r') as fp:
            xml = fp.read()
        mock_xsd300.content.serialize = unittest.mock.MagicMock(return_value=xml)
        article = ArticleFactory()
        view = ArticleDetailView()
        view.request = unittest.mock.MagicMock()
        view.object = article
        view.get_object = unittest.mock.MagicMock(return_value=article)

        # Run the XSL transformation.
        return view.render_xml_contents()

    def test_can_transform_article_xml_to_html(
            self, mock_has_coverpage, mock_ds, mock_xsd300, mock_eo):
        ret = self.mock_article_detail_view(mock_has_coverpage, mock_ds, mock_xsd300, mock_eo)

        # Check
        self.assertTrue(ret is not None)
        self.assertTrue(ret.startswith('<div xmlns:v="variables-node" class="article-wrapper">'))

    @unittest.mock.patch.object(ArticleDigitalObject, 'pdf')
    def test_can_transform_article_xml_to_html_when_pdf_exists(
            self, mock_pdf, mock_has_coverpage, mock_ds, mock_xsd300, mock_eo):
        # Setup
        fp = open(FIXTURE_ROOT + '/article.pdf', mode='rb')
        mock_pdf.exists = True
        mock_pdf.content = fp

        # Run
        ret = self.mock_article_detail_view(mock_has_coverpage, mock_ds, mock_xsd300, mock_eo)

        # Check
        fp.close()
        self.assertTrue(ret is not None)

    def test_html_tags_in_transformed_article_biblio_titles(
            self, mock_has_coverpage, mock_ds, mock_xsd300, mock_eo):
        ret = self.mock_article_detail_view(mock_has_coverpage, mock_ds, mock_xsd300, mock_eo)

        # Check that HTML tags in biblio titles are not stripped.
        assert '<h3 class="titre">H3 avec balise <strong>strong</strong>\n</h3>' in ret
        assert '<h4 class="titre">H4 avec balise <em>em</em>\n</h4>' in ret
        assert '<h5 class="titre">H5 avec balise <small>small</small>\n</h5>' in ret

    def test_footnotes_in_section_titles_not_in_toc(
            self, mock_has_coverpage, mock_ds, mock_xsd300, mock_eo):
        ret = self.mock_article_detail_view(mock_has_coverpage, mock_ds, mock_xsd300, mock_eo, '1053699ar.xml')

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

    def test_space_between_two_tags(
            self, mock_has_coverpage, mock_ds, mock_xsd300, mock_eo):
        ret = self.mock_article_detail_view(mock_has_coverpage, mock_ds, mock_xsd300, mock_eo, '1053699ar.xml')

        # Check that the space is preserved between two tags.
        assert '<span class="petitecap">Note 1,</span> <em>avec espace entre deux marquages</em>' in ret

    def test_blockquote_between_two_spans(
            self, mock_has_coverpage, mock_ds, mock_xsd300, mock_eo):
        ret = self.mock_article_detail_view(mock_has_coverpage, mock_ds, mock_xsd300, mock_eo, '1053699ar.xml')

        # Check that the blockquote is displayed before the second paragraph.
        assert '<blockquote class="bloccitation ">\n<p class="alinea">Citation</p>\n<cite class="source">Source</cite>\n</blockquote>\n<p class="alinea">Paragraphe</p>' in ret

    def test_annexes_footnotes(
            self, mock_has_coverpage, mock_ds, mock_xsd300, mock_eo):
        ret = self.mock_article_detail_view(mock_has_coverpage, mock_ds, mock_xsd300, mock_eo, '1035294ar.xml')

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

    def test_space_between_keywords_and_colon(
            self, mock_has_coverpage, mock_ds, mock_xsd300, mock_eo):
        ret = self.mock_article_detail_view(mock_has_coverpage, mock_ds, mock_xsd300, mock_eo, '1055726ar.xml')

        # Check that a space is present before the colon in French, but not in the other languages.
        assert 'Mots-clés :' in ret
        assert 'Keywords:' in ret
        assert 'Palabras clave:' in ret

    def test_article_titles_css_class(self, mock_has_coverpage, mock_ds, mock_xsd300, mock_eo):
        ret = self.mock_article_detail_view(mock_has_coverpage, mock_ds, mock_xsd300, mock_eo, '1055651ar.xml')
        # A normal title should not have any class.
        assert '<h2>La synthèse hoguettienne</h2>' in ret
        # A special character title should have the 'special' class.
        assert '<h2 class="special">*</h2>' in ret
        ret = self.mock_article_detail_view(mock_has_coverpage, mock_ds, mock_xsd300, mock_eo, '1055648ar.xml')
        # An empty title should have the 'special' and 'empty' classes and should be empty.
        assert '<h2 class="special empty"></h2>' in ret

    def test_volumaison_punctuation(self, mock_has_coverpage, mock_ds, mock_xsd300, mock_eo):
        ret = self.mock_article_detail_view(mock_has_coverpage, mock_ds, mock_xsd300, mock_eo, '1053504ar.xml')
        # There should be an hyphen between multiple months and no coma between month and year.
        assert '<p class="refpapier"><span class="volumaison"><span class="nonumero">Numéro 179</span>, Janvier–Avril 2018</span>, p. 1–2</p>' in ret

    def test_separator_between_sections_in_different_languages(self, mock_has_coverpage, mock_ds, mock_xsd300, mock_eo):
        ret = self.mock_article_detail_view(mock_has_coverpage, mock_ds, mock_xsd300, mock_eo, '1046558ar.xml')
        # There should not be a separator before the first section.
        assert '<hr>\n<section id="s1n1"><div class="para" id="pa1">' not in ret
        # There should be a separator before sections in different languages.
        assert '<hr>\n<section id="s1n2"><div class="para" id="pa11">' in ret
        assert '<hr>\n<section id="s1n3"><div class="para" id="pa21">' in ret

    def test_multilingual_titreparal_and_sstitreparal_order(self, mock_has_coverpage, mock_ds, mock_xsd300, mock_eo):
        ret = self.mock_article_detail_view(mock_has_coverpage, mock_ds, mock_xsd300, mock_eo, '1058157ar.xml')
        # Check that titreparal and sstitreparal are in the right order.
        assert '<h1 class="doc-head__title">\n<span class="titre">Introduction au dossier spécial</span><span class="sstitre">À la découverte du lien organisationnel : avez-vous lu A. O. Hirschman ?</span><span class="titreparal">Introduction to the special section</span><span class="sstitreparal">Exploring the Organizational Link: Have You Read A. O.\n        Hirschman?</span><span class="titreparal">Introducción Dossier Especial</span><span class="sstitreparal">Descubriendo las relaciones organizativas: ¿leyó a A.O.\n        Hirschman?</span>\n</h1>' in ret


class TestGoogleScholarSubscribersView:

    @pytest.mark.parametrize('valid, expired, google_scholar_opt_out, expected_subscribers', [
        (True, False, False, {
            1: {
                'institution': 'foo',
                'ip_ranges': [
                    ['0.0.0.0', '255.255.255.255'],
                ],
            },
        }),
        (False, True, False, {}),
        (True, False, True, {}),
    ])
    def test_google_scholar_subscribers(self, valid, expired, google_scholar_opt_out, expected_subscribers):
        JournalAccessSubscriptionFactory(
            pk=1,
            post__valid=valid,
            post__expired=expired,
            post__ip_start='0.0.0.0',
            post__ip_end='255.255.255.255',
            organisation__name='foo',
            organisation__google_scholar_opt_out=google_scholar_opt_out,
        )
        view = GoogleScholarSubscribersView()
        context = view.get_context_data()
        assert context.get('subscribers') == expected_subscribers


class TestGoogleScholarSubscriberJournalsView:

    @pytest.mark.parametrize('valid, expired, google_scholar_opt_out, subscription_id, expected_journal_ids', [
        (False, True, False, '1', []),
        (True, False, False, '1', ['journal_1']),
        (True, False, False, '', ['journal_1', 'journal_2']),
        (True, False, True, '1', []),
    ])
    def test_google_scholar_subscriber_journals(self, valid, expired, google_scholar_opt_out, subscription_id, expected_journal_ids):
        journal_1 = JournalFactory(localidentifier='journal_1')
        journal_2 = JournalFactory(localidentifier='journal_2')
        JournalAccessSubscriptionFactory(
            pk=1,
            post__valid=valid,
            post__expired=expired,
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
