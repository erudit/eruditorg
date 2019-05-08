import datetime as dt
import os
import pytest
import unittest.mock

from django.template import Context
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from base.test.factories import UserFactory
from erudit.test.factories import IssueFactory, JournalFactory
from erudit.fedora.objects import ArticleDigitalObject
from erudit.models import Issue
from erudit.test.factories import ArticleFactory
from erudit.test.domchange import SectionTitle
from apps.public.journal.views import JournalDetailView, IssueDetailView, ArticleDetailView, \
    GoogleScholarSubscribersView, GoogleScholarSubscriberJournalsView, JournalStatisticsView
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


class TestIssueDetailSummary:
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
                {'objects': [article_1, article_2], 'type': 'objects', 'level': 0, 'notegens': []},
                {
                    'titles': {'paral': [], 'main': "section 1"},
                    'level': 1,
                    'groups': [{'objects': [article_3], 'type': 'objects', 'level': 1, 'notegens': []}],
                    'type': 'subsection'
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
                'groups': [{
                    'type': 'subsection',
                    'level': 2,
                    'titles': {'paral': [], 'main': 'section 2'},
                    'groups': [{
                        'type': 'subsection',
                        'level': 3,
                        'titles': {'paral': [], 'main': 'section 3'},
                        'groups': [
                            {'objects': [article], 'type': 'objects', 'level': 3},
                        ]
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
                    'groups': [
                        {'type': 'objects', 'level': 1, 'objects': [articles[0]], 'notegens': []},
                        {
                            'type': 'subsection', 'level': 2, 'titles': {'paral': [], 'main': 'section 1.1'},  # noqa
                            'groups': [{'type': 'objects', 'level': 2, 'objects': [articles[1]], 'notegens': []}]
                        },
                        {
                            'type': 'objects', 'level': 1, 'objects': [articles[2]], 'notegens': []
                        }
                    ]
                }
            ]
        }

    def test_can_generate_section_tree_with_notegens(self):
        view = IssueDetailView()
        articles = [
            ArticleFactory(
                notegens=[{'content': 'Note surtitre', 'scope': 'surtitre', 'type': 'edito'}]
            ),
            ArticleFactory(
                section_titles=[SectionTitle(1, False, "Section 1")],
                notegens=[{'content': 'Note surtitre2', 'scope': 'surtitre2', 'type': 'edito'}]
            ),
        ]
        sections_tree = view.generate_sections_tree(articles)
        assert sections_tree == {
            'titles': {'paral': None, 'main': None},
            'level': 0,
            'groups': [
                {'objects': [articles[0]], 'type': 'objects', 'level': 0, 'notegens': [
                    {'content': ['Note surtitre'], 'scope': 'surtitre', 'type': 'edito'},
                ]},
                {
                    'titles': {'paral': [], 'main': 'Section 1'},
                    'level': 1,
                    'groups': [{'objects': [articles[1]], 'type': 'objects', 'level': 1, 'notegens': [
                        {'content': ['Note surtitre2'], 'scope': 'surtitre2', 'type': 'edito'}
                    ]}],
                    'type': 'subsection'
                },
            ],
            'type': 'subsection',
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
        assert 'Inaugural Lecture of the FR Scott Professor&nbsp;/ Conf&#233;rence inaugurale du Professeur FR Scott' in html

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


class TestArticleDetailView:

    @unittest.mock.patch('erudit.fedora.cache.cache')
    @unittest.mock.patch('erudit.fedora.cache.get_datastream_file_cache')
    @unittest.mock.patch('erudit.fedora.cache.get_cached_datastream_content')
    @pytest.mark.parametrize('is_published, url_name, fixture, expected_count', [
        # When an issue is not published, we should not get any cache.get() calls when displaying
        # an article's PDF or XML.
        (False, 'public:journal:article_raw_pdf', 'article.pdf', 0),
        (False, 'public:journal:article_raw_xml', 'article.xml', 0),
        # When an issue is published, we should get one cache.get() calls when displaying an
        # article's PDF or XML.
        (True, 'public:journal:article_raw_pdf', 'article.pdf', 1),
        (True, 'public:journal:article_raw_xml', 'article.xml', 1),
    ])
    def test_datastream_caching(self, mock_cache, mock_get_datastream_file_cache, mock_get_cached_datastream_content, is_published, url_name, fixture, expected_count):
        mock_cache.get.return_value = None
        mock_get_datastream_file_cache.return_value = mock_cache
        with open(FIXTURE_ROOT + '/' + fixture, mode='rb') as content:
            mock_get_cached_datastream_content.return_value = content

        article = ArticleFactory(
            issue__is_published=is_published,
            issue__journal__open_access=True,
        )
        url = reverse(url_name, kwargs={
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
