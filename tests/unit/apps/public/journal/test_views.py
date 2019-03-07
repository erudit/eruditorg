import datetime as dt
import os
import pytest
import unittest.mock

from django.template import Context
from django.test import TestCase, override_settings

from erudit.test.factories import IssueFactory, JournalFactory
from erudit.fedora.objects import ArticleDigitalObject
from erudit.models import Issue
from erudit.test.factories import ArticleFactory
from erudit.test.domchange import SectionTitle
from apps.public.journal.views import JournalDetailView, IssueDetailView, ArticleDetailView, \
    GoogleScholarSubscribersView, GoogleScholarSubscriberJournalsView
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
        assert '<h2>Titre <a href="#no1" id="re1no1" class="norenvoi" title="Note 1, avec espace entre deux marquages">[1]</a>\n</h2>' in ret

        assert '<a href="#s1n2"><strong>Titre gras</strong></a>' in ret
        assert '<h2><strong>Titre gras <a href="#no2" id="re1no2" class="norenvoi" title="Lien à encoder">[2]</a></strong></h2>' in ret

        assert '<a href="#s1n3"><em>Titre italique</em></a>' in ret
        assert '<h2><em>Titre italique <a href="#no3" id="re1no3" class="norenvoi" title="Lien déjà encodé">[3]</a></em></h2>' in ret

        assert '<a href="#s1n4"><span class="petitecap">Titre petitecap</span></a>' in ret
        assert '<h2><span class="petitecap">Titre petitecap <a href="#no4" id="re1no4" class="norenvoi" title="">[4]</a></span></h2>' in ret

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

    def test_links_url_ecoding(
            self, mock_has_coverpage, mock_ds, mock_xsd300, mock_eo):
        ret = self.mock_article_detail_view(mock_has_coverpage, mock_ds, mock_xsd300, mock_eo, '1053699ar.xml')

        # Check that links' URL are correctly ecoded.
        assert '<a href="http://example.com%23test" id="ls2" target="_blank">Lien à encoder</a>' in ret
        # Check that already encoded links' URL are not ecoded again.
        assert '<a href="http://example.com%23test" id="ls3" target="_blank">Lien déjà encodé</a>' in ret

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


class TestGoogleScholarSubscribersView:

    @pytest.mark.parametrize('valid, expired, expected_subscribers', [
        (True, False, {
            1: {
                'institution': 'foo',
                'ip_ranges': [
                    ['0.0.0.0', '255.255.255.255'],
                ],
            },
        }),
        (False, True, {}),
    ])
    def test_google_scholar_subscribers(self, valid, expired, expected_subscribers):
        JournalAccessSubscriptionFactory(
            pk=1,
            post__valid=valid,
            post__expired=expired,
            post__ip_start='0.0.0.0',
            post__ip_end='255.255.255.255',
            organisation__name='foo',
        )
        view = GoogleScholarSubscribersView()
        context = view.get_context_data()
        assert context.get('subscribers') == expected_subscribers


class TestGoogleScholarSubscriberJournalsView:

    @pytest.mark.parametrize('valid, expired, subscription_id, expected_journal_ids', [
        (False, True, '1', []),
        (True, False, '1', ['journal_1']),
        (True, False, '', ['journal_1', 'journal_2']),
    ])
    def test_google_scholar_subscriber_journals(self, valid, expired, subscription_id, expected_journal_ids):
        journal_1 = JournalFactory(localidentifier='journal_1')
        journal_2 = JournalFactory(localidentifier='journal_2')
        JournalAccessSubscriptionFactory(
            pk=1,
            post__valid=valid,
            post__expired=expired,
            post__journals=[journal_1],
        )
        view = GoogleScholarSubscriberJournalsView()
        context = view.get_context_data(subscription_id=subscription_id)
        assert [journal.localidentifier for journal in context.get('journals')] == expected_journal_ids
