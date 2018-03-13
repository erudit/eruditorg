import io
import os.path as op
import pytest

from django.http import HttpResponse
from django.test.utils import override_settings
from erudit.test.factories import ArticleFactory
from erudit.test.factories import IssueFactory

from base.pdf import generate_pdf, local_url_fetcher


pytestmark = pytest.mark.django_db

def test_generates_a_pdf_into_a_bytes_stream_by_default():
    issue = IssueFactory.create()
    article = ArticleFactory.create(issue=issue)
    pdf = generate_pdf('public/journal/article_pdf_coverpage.html', context={
        'article': article, 'issue': issue, 'journal': issue.journal})
    assert isinstance(pdf, io.BytesIO)

def test_can_raise_an_exception_when_path_is_not_a_subpath_of_static_root():
    with pytest.raises(ValueError):
        local_url_fetcher("local:/../../erudit.png")

def test_can_open_a_local_file():
    with pytest.raises(FileNotFoundError):
        local_url_fetcher("local:/erudit.png")

def test_can_generate_a_pdf_into_a_http_response():
    issue = IssueFactory.create()
    article = ArticleFactory.create(issue=issue)
    response = HttpResponse(content_type='application/pdf')
    generate_pdf(
        'public/journal/article_pdf_coverpage.html',
        file_object=response, context={
            'article': article, 'issue': issue, 'journal': issue.journal})
    assert isinstance(response.content, bytes)
    assert response.tell()

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
def test_can_use_a_context():
    response_1 = HttpResponse(content_type='application/pdf')
    response_2 = HttpResponse(content_type='application/pdf')
    generate_pdf('pdf.html', file_object=response_1)
    generate_pdf('pdf.html', file_object=response_2, context={'title': 'test'})
    assert response_2.tell() > response_1.tell()
