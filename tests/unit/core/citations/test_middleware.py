# -*- coding: utf-8 -*-

from django.contrib.auth.models import AnonymousUser
from django.contrib.sessions.middleware import SessionMiddleware
from django.test import RequestFactory

from erudit.test import BaseEruditTestCase
from erudit.test.factories import ArticleFactory
from erudit.test.factories import IssueFactory

from core.citations.citations import SavedCitationList
from core.citations.middleware import SavedCitationListMiddleware


class TestSavedCitationListMiddleware(BaseEruditTestCase):
    def setUp(self):
        super(TestSavedCitationListMiddleware, self).setUp()
        self.factory = RequestFactory()

    def test_associates_the_citation_list_to_the_request_object(self):
        # Setup
        issue = IssueFactory.create(journal=self.journal)
        article = ArticleFactory.create(issue=issue)
        request = self.factory.get('/')
        request.user = AnonymousUser()
        middleware = SessionMiddleware()
        middleware.process_request(request)
        citation_list = SavedCitationList(request)
        citation_list.add(article)
        citation_list.save()
        middleware = SavedCitationListMiddleware()
        # Run
        middleware.process_request(request)
        # Check
        self.assertEqual(list(request.saved_citations), [article.id, ])

    def test_saves_the_citation_list_in_session_when_processing_responses(self):
        # Setup
        issue = IssueFactory.create(journal=self.journal)
        article_1 = ArticleFactory.create(issue=issue)
        article_2 = ArticleFactory.create(issue=issue)
        request = self.factory.get('/')
        request.user = AnonymousUser()
        middleware = SessionMiddleware()
        middleware.process_request(request)
        citation_list = SavedCitationList(request)
        citation_list.add(article_1)
        citation_list.save()
        middleware = SavedCitationListMiddleware()
        middleware.process_request(request)
        # Run
        request.saved_citations.remove(article_1)
        request.saved_citations.add(article_2)
        middleware.process_response(request, None)
        # Check
        self.assertEqual(request.session['saved-citations'], [article_2.id, ])
