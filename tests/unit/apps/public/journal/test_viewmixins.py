# -*- coding: utf-8 -*-

import datetime as dt

from django.views.generic import DetailView

from erudit.test import BaseEruditTestCase
from erudit.test.factories import ArticleFactory
from erudit.test.factories import IssueFactory
from erudit.models import Article

from apps.public.journal.viewmixins import SingleArticleMixin


class TestSingleArticleMixin(BaseEruditTestCase):
    def test_can_retrieve_the_article_using_the_local_identifier(self):
        # Setup
        issue_1 = IssueFactory.create(journal=self.journal, date_published=dt.datetime.now())
        article_1 = ArticleFactory.create(issue=issue_1, localidentifier='test_article')

        class MyView(SingleArticleMixin, DetailView):
            model = Article

        view = MyView()
        view.kwargs = {'localid': article_1.localidentifier}

        # Run & check
        self.assertEqual(view.get_object(), article_1)
