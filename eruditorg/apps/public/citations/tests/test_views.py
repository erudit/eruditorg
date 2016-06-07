# -*- coding: utf-8 -*-

import json

from django.contrib.auth.models import AnonymousUser
from django.contrib.sessions.middleware import SessionMiddleware
from django.test import RequestFactory
from django.utils.encoding import force_text

from core.citations.middleware import SavedCitationListMiddleware
from erudit.test import BaseEruditTestCase
from erudit.test.factories import ArticleFactory
from erudit.test.factories import IssueFactory

from ..views import SavedCitationAddView
from ..views import SavedCitationRemoveView


class TestSavedCitationAddView(BaseEruditTestCase):
    def setUp(self):
        super(TestSavedCitationAddView, self).setUp()
        self.factory = RequestFactory()

    def test_can_add_an_article_to_a_citation_list(self):
        # Setup
        issue = IssueFactory.create(journal=self.journal)
        article = ArticleFactory.create(issue=issue)
        request = self.factory.post('/')
        request.user = AnonymousUser()
        SessionMiddleware().process_request(request)
        SavedCitationListMiddleware().process_request(request)
        view = SavedCitationAddView.as_view()
        # Run
        response = view(request, article.id)
        # Check
        self.assertEqual(response.status_code, 200)
        self.assertEqual(list(request.saved_citations), [article.id, ])


class TestSavedCitationRemoveView(BaseEruditTestCase):
    def setUp(self):
        super(TestSavedCitationRemoveView, self).setUp()
        self.factory = RequestFactory()

    def test_can_remove_an_article_from_a_citation_list(self):
        # Setup
        issue = IssueFactory.create(journal=self.journal)
        article = ArticleFactory.create(issue=issue)
        request = self.factory.post('/')
        request.user = AnonymousUser()
        SessionMiddleware().process_request(request)
        SavedCitationListMiddleware().process_request(request)
        request.saved_citations.add(article)
        view = SavedCitationRemoveView.as_view()
        # Run
        response = view(request, article.id)
        # Check
        self.assertEqual(response.status_code, 200)
        self.assertFalse(len(request.saved_citations))

    def test_can_properly_handle_the_case_where_an_item_is_no_longer_in_the_citation_list(self):
        # Setup
        issue = IssueFactory.create(journal=self.journal)
        article = ArticleFactory.create(issue=issue)
        request = self.factory.post('/')
        request.user = AnonymousUser()
        SessionMiddleware().process_request(request)
        SavedCitationListMiddleware().process_request(request)
        view = SavedCitationRemoveView.as_view()
        # Run
        response = view(request, article.id)
        # Check
        self.assertEqual(response.status_code, 200)
        self.assertTrue('error' in json.loads(force_text(response.content)))
