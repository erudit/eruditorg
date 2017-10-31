import pytest

from erudit.test.factories import ArticleFactory, ArticleSectionTitleFactory
from apps.public.journal.views import IssueDetailView


@pytest.mark.django_db
class TestIssueDetailSummary(object):

    def test_can_generate_section_tree_with_contiguous_articles(self):
        view = IssueDetailView()
        article_1, article_2, article_3 = ArticleFactory.create_batch(3, use_fedora=False)
        ArticleSectionTitleFactory(
            article=article_3,
            title="section 1",
            level=1,
        )
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
        article = ArticleFactory(use_fedora=False)

        ArticleSectionTitleFactory(
            article=article,
            title="section 1",
            level=1,
        )

        ArticleSectionTitleFactory(
            article=article,
            title="section 2",
            level=2,
        )

        ArticleSectionTitleFactory(
            article=article,
            title="section 3",
            level=3
        )

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
        articles = ArticleFactory.create_batch(3, use_fedora=False)

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
