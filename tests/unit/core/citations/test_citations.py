# -*- coding: utf-8 -*-

from django.contrib.auth.models import AnonymousUser
from django.contrib.sessions.middleware import SessionMiddleware
from django.test import RequestFactory

from erudit.test import BaseEruditTestCase
from erudit.test.factories import ArticleFactory
from erudit.test.factories import IssueFactory

from core.citations.citations import SavedCitationList
from core.citations.models import SavedCitationList as DBSavedCitationList


class TestSavedCitationList(BaseEruditTestCase):
    def setUp(self):
        super(TestSavedCitationList, self).setUp()
        self.factory = RequestFactory()

    def test_can_add_new_articles(self):
        # Setup
        issue = IssueFactory.create(journal=self.journal)
        article_1 = ArticleFactory.create(issue=issue)
        article_2 = ArticleFactory.create(issue=issue)
        request = self.factory.get('/')
        middleware = SessionMiddleware()
        middleware.process_request(request)
        citation_list = SavedCitationList(request)
        # Run
        citation_list.add(article_1)
        citation_list.add(article_2.id)
        # Check
        self.assertTrue(article_1 in citation_list)
        self.assertTrue(article_2.id in citation_list)

    def test_can_remove_articles(self):
        # Setup
        issue = IssueFactory.create(journal=self.journal)
        article_1 = ArticleFactory.create(issue=issue)
        article_2 = ArticleFactory.create(issue=issue)
        request = self.factory.get('/')
        middleware = SessionMiddleware()
        middleware.process_request(request)
        citation_list = SavedCitationList(request)
        citation_list.add(article_1)
        citation_list.add(article_2.id)
        # Run
        citation_list.remove(article_1)
        citation_list.remove(article_2.id)
        # Check
        self.assertFalse(len(citation_list))

    def test_can_save_the_set_of_articles_to_the_session(self):
        # Setup
        issue = IssueFactory.create(journal=self.journal)
        article = ArticleFactory.create(issue=issue)
        request = self.factory.get('/')
        request.user = AnonymousUser()
        middleware = SessionMiddleware()
        middleware.process_request(request)
        citation_list = SavedCitationList(request)
        citation_list.add(article)
        # Run
        citation_list.save()
        # Check
        self.assertEqual(request.session['saved-citations'], [article.id, ])

    def test_can_associate_the_article_to_the_registered_users(self):
        # Setup
        issue = IssueFactory.create(journal=self.journal)
        article = ArticleFactory.create(issue=issue)
        request = self.factory.get('/')
        request.user = self.user
        middleware = SessionMiddleware()
        middleware.process_request(request)
        citation_list = SavedCitationList(request)
        citation_list.add(article)
        # Run
        citation_list.save()
        # Check
        self.assertEqual(DBSavedCitationList.objects.count(), 1)
        db_citation_list = DBSavedCitationList.objects.first()
        self.assertEqual(db_citation_list.user, self.user)
        self.assertEqual(list(db_citation_list.documents.all()), [article, ])
