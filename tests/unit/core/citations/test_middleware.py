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
        self.assertEqual(list(request.saved_citations), [str(article.id), ])
