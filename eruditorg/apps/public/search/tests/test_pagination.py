# -*- coding: utf-8 -*-

from django.test import RequestFactory
from rest_framework.request import Request

from erudit.test import BaseEruditTestCase
from erudit.test.factories import ArticleFactory
from erudit.test.factories import IssueFactory
from erudit.models import Article

from ..pagination import EruditDocumentPagination


class TestEruditDocumentPagination(BaseEruditTestCase):
    def setUp(self):
        super(TestEruditDocumentPagination, self).setUp()
        self.factory = RequestFactory()

    def test_can_properly_paginate_a_queryset_using_a_list_of_localidentifiers(self):
        # Setup
        issue = IssueFactory.create(journal=self.journal)
        localidentifiers = []
        for i in range(0, 10):
            lid = 'lid-{0}'.format(i)
            localidentifiers.append(lid)
            ArticleFactory.create(issue=issue, localidentifier=lid)
        request = Request(self.factory.get('/', data={'page': 1}))
        paginator = EruditDocumentPagination()
        # Run
        object_list = paginator.paginate(10, localidentifiers, Article.objects.all(), request)
        # Check
        self.assertEqual(
            object_list,
            list(Article.objects.filter(localidentifier__in=localidentifiers[:10])
                 .order_by('localidentifier')))

    def test_can_provide_valid_pagination_data(self):
        # Setup
        issue = IssueFactory.create(journal=self.journal)
        localidentifiers = []
        for i in range(0, 50):
            lid = 'lid-{0}'.format(i)
            localidentifiers.append(lid)
            ArticleFactory.create(issue=issue, localidentifier=lid)
        request = Request(self.factory.get('/', data={'page': 2}))
        paginator = EruditDocumentPagination()
        # Run
        paginator.paginate(200, localidentifiers, Article.objects.all(), request)
        response = paginator.get_paginated_response({})
        # Check
        self.assertEqual(response.data['pagination']['count'], 200)
        self.assertEqual(response.data['pagination']['num_pages'], 20)
        self.assertEqual(response.data['pagination']['current_page'], 2)
        self.assertEqual(response.data['pagination']['next_page'], 3)
        self.assertEqual(response.data['pagination']['previous_page'], 1)
        self.assertEqual(response.data['pagination']['page_size'], 10)
