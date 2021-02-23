import pytest
from django.contrib.auth.models import AnonymousUser
from django.contrib.sessions.middleware import SessionMiddleware
from django.test import RequestFactory

from erudit.test.factories import ArticleFactory
from erudit.test.factories import IssueFactory

from core.citations.citations import SavedCitationList
from core.citations.middleware import SavedCitationListMiddleware


pytestmark = pytest.mark.django_db


def test_associates_the_citation_list_to_the_request_object():
    issue = IssueFactory.create()
    article = ArticleFactory.create(issue=issue)
    request = RequestFactory().get("/")
    request.user = AnonymousUser()
    middleware = SessionMiddleware()
    middleware.process_request(request)
    citation_list = SavedCitationList(request)
    citation_list.add(article)
    citation_list.save()
    middleware = SavedCitationListMiddleware()
    middleware.process_request(request)
    assert list(request.saved_citations) == [article.solr_id]
