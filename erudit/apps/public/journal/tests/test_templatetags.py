# -*- coding: utf-8 -*-

import datetime as dt
import os
import unittest.mock

from django.template import Context

from erudit.factories import ArticleFactory
from erudit.factories import AuthorFactory
from erudit.factories import IssueFactory
from erudit.factories import JournalFactory
from erudit.fedora.objects import ArticleDigitalObject
from erudit.tests import BaseEruditTestCase

from ..templatetags.public_journal_tags import author_articles
from ..templatetags.public_journal_tags import render_article
from ..templatetags.public_journal_tags import sort_by_ordseq

FIXTURE_ROOT = os.path.join(os.path.dirname(__file__), 'fixtures')


class TestRenderArticleTemplateTag(BaseEruditTestCase):
    @unittest.mock.patch.object(ArticleDigitalObject, 'erudit_xsd300')
    @unittest.mock.patch.object(ArticleDigitalObject, '_get_datastreams')
    def test_can_transform_article_xml_to_html(self, mock_ds, mock_xsd300):
        # Setup
        with open(FIXTURE_ROOT + '/article.xml', mode='r') as fp:
            xml = fp.read()
        mock_ds.return_value = ['ERUDITXSD300', ]  # noqa
        mock_xsd300.content = unittest.mock.MagicMock()
        mock_xsd300.content.serialize = unittest.mock.MagicMock(return_value=xml)
        issue = IssueFactory.create(
            journal=self.journal, date_published=dt.datetime.now(), localidentifier='test')
        article = ArticleFactory.create(issue=issue)
        # Run
        ret = render_article(Context({}), article)
        # Check
        self.assertTrue(ret is not None)
        self.assertTrue(ret.startswith('<div xmlns:v="variables-node" class="article-wrapper">'))


class TestAuthorArticlesFilter(BaseEruditTestCase):
    def test_can_return_the_articles_associated_with_an_author_for_a_given_journal(self):
        # Setup
        other_journal = JournalFactory.create(publishers=[self.publisher])
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
        self.assertEqual(list(author_articles(author, self.journal)), [article, ])


class TestSortByOrdseqFilter(BaseEruditTestCase):
    def test_can_return_articles_sorted_by_their_ordering_number(self):
        # Setup
        issue = IssueFactory.create(journal=self.journal)
        a1 = ArticleFactory.create(issue=issue)
        a2 = ArticleFactory.create(issue=issue)
        a3 = ArticleFactory.create(issue=issue)
        setattr(a1, 'erudit_object', unittest.mock.MagicMock())
        setattr(a2, 'erudit_object', unittest.mock.MagicMock())
        setattr(a3, 'erudit_object', unittest.mock.MagicMock())
        a1.erudit_object.ordseq = 10
        a2.erudit_object.ordseq = 1
        a3.erudit_object.ordseq = 30
        # Run & check
        self.assertEqual(sort_by_ordseq([a1, a2, a3]), [a2, a1, a3])
