import pytest

from erudit.test.factories import ArticleFactory, ArticleSectionTitleFactory
from apps.public.journal.views import IssueDetailView


@pytest.mark.django_db
class TestIssueDetailSummary(object):

    def test_can_generate_section_tree_with_contiguous_articles(self):
        view = IssueDetailView()
        article_1, article_2, article_3 = ArticleFactory.create_batch(3)
        ArticleSectionTitleFactory(
            article=article_3,
            title="section 1",
            level=1,
        )
        sections_tree = view.generate_sections_tree([article_1, article_2, article_3])
        assert sections_tree == {
            'titles': {'paral': None, 'main': None},
            'level': 1,
            'groups': [
                {'objects': [article_1, article_2], 'type': 'objects', 'level': 1},
                {
                    'titles': {'paral': [], 'main': "section 1"},
                    'level': 2,
                    'groups': [{'objects': [article_3], 'type': 'objects', 'level': 2}],
                    'type': 'subsection'
                },
            ],
            'type': 'subsection',
        }

    def test_can_generate_section_tree_with_non_contiguous_articles(self):
        view = IssueDetailView()
        articles = ArticleFactory.create_batch(3)

        for article in articles:
            ArticleSectionTitleFactory(
                article=article,
                title="section 1",
                level=1,
            )

        ArticleSectionTitleFactory(
            article=articles[1],
            title="section 1.1",
            level=2,
        )

        sections_tree = view.generate_sections_tree(articles)
        assert sections_tree == {
            'type': 'subsection',
            'level': 1,
            'titles': {'paral': None, 'main': None},
            'groups': [
                {
                    'type': 'subsection',
                    'level': 2,
                    'titles': {
                        'paral': [], 'main': 'section 1'
                    },
                    'groups': [
                        {'type': 'objects', 'level': 2, 'objects': [articles[0]]},
                        {
                            'type': 'subsection', 'level': 3, 'titles': {'paral': [], 'main': 'section 1.1'},  # noqa
                            'groups': [{'type': 'objects', 'level': 3, 'objects': [articles[1]]}]
                        },
                        {
                            'type': 'objects', 'level': 2, 'objects': [articles[2]]
                        }
                    ]
                }
            ]
        }
