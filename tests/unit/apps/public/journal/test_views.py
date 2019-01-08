import datetime as dt
import os
import pytest
import unittest.mock

from django.template import Context
from django.test import TestCase

from erudit.test.factories import IssueFactory, JournalFactory
from erudit.fedora.objects import ArticleDigitalObject
from erudit.models import Issue
from erudit.test.factories import ArticleFactory
from erudit.test.domchange import SectionTitle
from apps.public.journal.views import IssueDetailView, ArticleDetailView

FIXTURE_ROOT = os.path.join(os.path.dirname(__file__), 'fixtures')
pytestmark = pytest.mark.django_db


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
                {'objects': [article_1, article_2], 'type': 'objects', 'level': 0},
                {
                    'titles': {'paral': [], 'main': "section 1"},
                    'level': 1,
                    'groups': [{'objects': [article_3], 'type': 'objects', 'level': 1}],
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
                        {'type': 'objects', 'level': 1, 'objects': [articles[0]]},
                        {
                            'type': 'subsection', 'level': 2, 'titles': {'paral': [], 'main': 'section 1.1'},  # noqa
                            'groups': [{'type': 'objects', 'level': 2, 'objects': [articles[1]]}]
                        },
                        {
                            'type': 'objects', 'level': 1, 'objects': [articles[2]]
                        }
                    ]
                }
            ]
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

    def test_can_transform_article_xml_to_html(
            self, mock_has_coverpage, mock_ds, mock_xsd300, mock_eo):
        with open(FIXTURE_ROOT + '/article.xml', mode='r') as fp:
            xml = fp.read()
        mock_xsd300.content.serialize = unittest.mock.MagicMock(return_value=xml)
        issue = IssueFactory.create(
            date_published=dt.datetime.now(), localidentifier='test')
        article = ArticleFactory.create(issue=issue)
        view = ArticleDetailView()
        view.request = unittest.mock.MagicMock(return_value={})
        view.get_context_data = unittest.mock.MagicMock(return_value={})
        view.get_object = unittest.mock.MagicMock(return_value=article)

        # Run
        ret = view.render_xml_contents()

        # Check
        self.assertTrue(ret is not None)
        self.assertTrue(ret.startswith('<div xmlns:v="variables-node" class="article-wrapper">'))

    @unittest.mock.patch.object(ArticleDigitalObject, 'pdf')
    def test_can_transform_article_xml_to_html_when_pdf_exists(
            self, mock_pdf, mock_has_coverpage, mock_ds, mock_xsd300, mock_eo):
        # Setup
        with open(FIXTURE_ROOT + '/article.xml', mode='r') as fp:
            xml = fp.read()
        fp = open(FIXTURE_ROOT + '/article.pdf', mode='rb')
        mock_xsd300.content.serialize = unittest.mock.MagicMock(return_value=xml)
        mock_pdf.exists = True
        mock_pdf.content = fp
        issue = IssueFactory.create(
            journal=JournalFactory(), date_published=dt.datetime.now(), localidentifier='test')
        article = ArticleFactory.create(issue=issue)
        view = ArticleDetailView()
        view.request = unittest.mock.MagicMock(return_value={})
        view.get_context_data = unittest.mock.MagicMock(return_value={})
        view.get_object = unittest.mock.MagicMock(return_value=article)

        # Run
        ret = view.render_xml_contents()

        # Check
        fp.close()
        self.assertTrue(ret is not None)

    def test_html_tags_in_transformed_article_biblio_titles(
            self, mock_has_coverpage, mock_ds, mock_xsd300, mock_eo):
        with open(FIXTURE_ROOT + '/article.xml', mode='r') as fp:
            xml = fp.read()
        mock_xsd300.content.serialize = unittest.mock.MagicMock(return_value=xml)
        view = ArticleDetailView()
        view.request = unittest.mock.MagicMock(return_value={})
        view.get_context_data = unittest.mock.MagicMock(return_value={})
        view.get_object = unittest.mock.MagicMock(return_value=ArticleFactory())

        # Run the XSL transformation.
        ret = view.render_xml_contents()

        # Check that HTML tags in biblio titles are not stripped.
        assert ret is not None
        assert '<h3 class="titre">H3 avec balise <strong>strong</strong>\n</h3>' in ret
        assert '<h4 class="titre">H4 avec balise <em>em</em>\n</h4>' in ret
        assert '<h5 class="titre">H5 avec balise <small>small</small>\n</h5>' in ret
