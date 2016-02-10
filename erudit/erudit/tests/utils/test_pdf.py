# -*- coding: utf-8 -*-

import io
import os.path as op

from django.http import HttpResponse
from django.test import TestCase
from django.test.utils import override_settings

from erudit.utils.pdf import generate_pdf


class TestGeneratePdfTool(TestCase):
    def test_generates_a_pdf_into_a_bytes_stream_by_default(self):
        # Run & check
        pdf = generate_pdf('journal/article_pdf_coverpage.html')
        self.assertTrue(isinstance(pdf, io.BytesIO))

    def test_can_generate_a_pdf_into_a_http_response(self):
        # Setup
        response = HttpResponse(content_type='application/pdf')
        # Run & check
        generate_pdf('journal/article_pdf_coverpage.html', file_object=response)
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
