import pytest
from django.contrib.auth.models import AnonymousUser
from django.contrib.sessions.middleware import SessionMiddleware
from django.test import RequestFactory

from base.test.factories import UserFactory
from erudit.test.factories import ArticleFactory
from erudit.test.factories import IssueFactory

from core.citations.citations import SavedCitationList


pytestmark = pytest.mark.django_db


def test_can_add_new_articles():
    issue = IssueFactory.create()
    article_1 = ArticleFactory.create(issue=issue)
    article_2 = ArticleFactory.create(issue=issue)
    request = RequestFactory().get("/")
    middleware = SessionMiddleware()
    middleware.process_request(request)
    citation_list = SavedCitationList(request)
    citation_list.add(article_1)
    citation_list.add(article_2)
    assert article_1.solr_id in citation_list
    assert article_2.solr_id in citation_list


def test_can_remove_articles():
    issue = IssueFactory.create()
    article_1 = ArticleFactory.create(issue=issue)
    article_2 = ArticleFactory.create(issue=issue)
    request = RequestFactory().get("/")
    middleware = SessionMiddleware()
    middleware.process_request(request)
    citation_list = SavedCitationList(request)
    citation_list.add(article_1)
    citation_list.add(article_2)
    citation_list.remove(article_1)
    citation_list.remove(article_2)
    assert len(citation_list) == 0


def test_can_save_the_set_of_articles_to_the_session():
    issue = IssueFactory.create()
    article = ArticleFactory.create(issue=issue)
    request = RequestFactory().get("/")
    request.user = AnonymousUser()
    middleware = SessionMiddleware()
    middleware.process_request(request)
    citation_list = SavedCitationList(request)
    citation_list.add(article)
    citation_list.save()
    assert request.session["saved-citations"] == [article.solr_id]


def test_can_associate_the_article_to_the_registered_users():
    issue = IssueFactory.create()
    article = ArticleFactory.create(issue=issue)
    request = RequestFactory().get("/")
    request.user = UserFactory.create()
    middleware = SessionMiddleware()
    middleware.process_request(request)
    citation_list = SavedCitationList(request)
    citation_list.add(article)
    citation_list.save()
    assert request.user.saved_citations.count() == 1
    db_citation = request.user.saved_citations.first()
    assert db_citation.user == request.user
    assert db_citation.solr_id == article.solr_id
