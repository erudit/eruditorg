# -*- coding: utf-8 -*-
import unittest
import io
import os.path as op
import pytest

from django.http import HttpResponse
from django.test.utils import override_settings
from erudit.test.factories import ArticleFactory
from erudit.test.factories import IssueFactory
from erudit.test.testcases import BaseEruditTestCase
from erudit.fedora.modelmixins import FedoraMixin

from base.pdf import generate_pdf


def get_mocked_erudit_object(self):
    m = unittest.mock.MagicMock()
    m.get_formatted_title.return_value = "mocked title"
    return m

@pytest.fixture(autouse=True)
def monkeypatch_get_erudit_article(monkeypatch):
    monkeypatch.setattr(FedoraMixin, "get_erudit_object", get_mocked_erudit_object)

@override_settings(DEBUG=True)
class TestGeneratePdfTool(BaseEruditTestCase):
    def test_generates_a_pdf_into_a_bytes_stream_by_default(self):
        # Setup
        issue = IssueFactory.create(journal=self.journal)
        article = ArticleFactory.create(issue=issue)
        # Run & check
        pdf = generate_pdf('public/journal/article_pdf_coverpage.html', context={
            'article': article, 'issue': issue, 'journal': issue.journal})
        self.assertTrue(isinstance(pdf, io.BytesIO))

    def test_can_generate_a_pdf_into_a_http_response(self):
        # Setup
        issue = IssueFactory.create(journal=self.journal)
        article = ArticleFactory.create(issue=issue)
        response = HttpResponse(content_type='application/pdf')
        # Run & check
        generate_pdf(
            'public/journal/article_pdf_coverpage.html',
            file_object=response, context={
                'article': article, 'issue': issue, 'journal': issue.journal})
        self.assertTrue(isinstance(response.content, bytes))
        self.assertTrue(response.tell())

    @override_settings(TEMPLATES=[
        {
            'BACKEND': 'django.template.backends.django.DjangoTemplates',
            'DIRS': ['%s/templates' % op.abspath(op.dirname(__file__))],
            'OPTIONS': {
                'context_processors': [
                    'django.core.context_processors.request',
                    'django.template.context_processors.debug',
                    'django.template.context_processors.request',
                    'django.template.context_processors.static',
                ],
            },
        },
    ])
    def test_can_use_a_context(self):
        # Setup
        response_1 = HttpResponse(content_type='application/pdf')
        response_2 = HttpResponse(content_type='application/pdf')
        # Run & check
        generate_pdf('pdf.html', file_object=response_1)
        generate_pdf('pdf.html', file_object=response_2, context={'title': 'test'})
        self.assertTrue(response_2.tell() > response_1.tell())
