# -*- coding: utf-8 -*-

import datetime as dt
import os
import unittest.mock

from django.template import Context

from erudit.test import BaseEruditTestCase
from erudit.test.factories import ArticleFactory
from erudit.test.factories import IssueFactory
from erudit.fedora.objects import ArticleDigitalObject
from erudit.models import Issue
from apps.public.journal.templatetags.public_journal_tags import render_article

FIXTURE_ROOT = os.path.join(os.path.dirname(__file__), 'fixtures')


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
class TestRenderArticleTemplateTag(BaseEruditTestCase):

    def test_can_transform_article_xml_to_html(
        self, mock_has_coverpage, mock_ds, mock_xsd300
    ):
        # Setup
        with open(FIXTURE_ROOT + '/article.xml', mode='r') as fp:
            xml = fp.read()
        mock_xsd300.content.serialize = unittest.mock.MagicMock(return_value=xml)
        issue = IssueFactory.create(
            journal=self.journal, date_published=dt.datetime.now(), localidentifier='test')
        article = ArticleFactory.create(issue=issue)
        # Run
        ret = render_article(Context({}), article)
        # Check
        self.assertTrue(ret is not None)
        self.assertTrue(ret.startswith('<div xmlns:v="variables-node" class="article-wrapper">'))

    @unittest.mock.patch.object(ArticleDigitalObject, 'pdf')
    def test_can_transform_article_xml_to_html_when_pdf_exists(
        self, mock_pdf, mock_has_coverpage, mock_ds, mock_xsd300
    ):
        # Setup
        with open(FIXTURE_ROOT + '/article.xml', mode='r') as fp:
            xml = fp.read()
        fp = open(FIXTURE_ROOT + '/article.pdf', mode='rb')
        mock_xsd300.content.serialize = unittest.mock.MagicMock(return_value=xml)
        mock_pdf.exists = True
        mock_pdf.content = fp
        issue = IssueFactory.create(
            journal=self.journal, date_published=dt.datetime.now(), localidentifier='test')
        article = ArticleFactory.create(issue=issue)
        # Run
        ret = render_article(Context({}), article)
        # Check
        fp.close()
        self.assertTrue(ret is not None)
