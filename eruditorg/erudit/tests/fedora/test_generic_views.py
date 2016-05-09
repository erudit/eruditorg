# -*- coding: utf-8 -*-

import unittest.mock

from django.core.exceptions import ImproperlyConfigured
from django.http import Http404
from django.test import RequestFactory

from ...fedora.objects import JournalDigitalObject
from ...fedora.views.generic import FedoraFileDatastreamView
from ...models import Journal
from ...tests import BaseEruditTestCase


class TestFedoraFileDatastreamView(BaseEruditTestCase):
    def setUp(self):
        super(TestFedoraFileDatastreamView, self).setUp()
        self.factory = RequestFactory()

    def test_raises_if_the_fedora_object_class_is_not_defined(self):
        # Setup
        class MyView(FedoraFileDatastreamView):
            pass

        request = self.factory.get('/')

        # Run & check
        with self.assertRaises(ImproperlyConfigured):
            MyView.as_view()(request)

    def test_raises_if_the_django_object_can_not_be_retrieved(self):
        # Setup
        class MyView(FedoraFileDatastreamView):
            fedora_object_class = JournalDigitalObject

        request = self.factory.get('/')

        # Run & check
        with self.assertRaises(ImproperlyConfigured):
            MyView.as_view()(request)

    def test_raises_if_the_content_type_is_not_defined(self):
        # Setup
        class MyView(FedoraFileDatastreamView):
            fedora_object_class = JournalDigitalObject
            model = Journal

        request = self.factory.get('/')

        # Run & check
        with self.assertRaises(ImproperlyConfigured):
            MyView.as_view()(request, pk=self.journal.pk)

    def test_raises_if_the_datastream_name_is_not_defined(self):
        # Setup
        class MyView(FedoraFileDatastreamView):
            content_type = 'image/jpeg'
            fedora_object_class = JournalDigitalObject
            model = Journal

        request = self.factory.get('/')

        # Run & check
        with self.assertRaises(ImproperlyConfigured):
            MyView.as_view()(request, pk=self.journal.pk)

    def test_raises_if_the_datastream_is_not_defined_on_the_digital_object(self):
        # Setup
        class MyView(FedoraFileDatastreamView):
            content_type = 'image/jpeg'
            datastream_name = 'dummy'
            fedora_object_class = JournalDigitalObject
            model = Journal

        request = self.factory.get('/')

        # Run & check
        with self.assertRaises(ImproperlyConfigured):
            MyView.as_view()(request, pk=self.journal.pk)

    def test_raises_if_the_datastream_does_not_have_content(self):
        # Setup
        class Dummy(object):
            logo = 'dummy'
            pid = 'pid'

        class MyView(FedoraFileDatastreamView):
            content_type = 'image/jpeg'
            datastream_name = 'logo'
            fedora_object_class = JournalDigitalObject
            model = Journal

            def get_fedora_object(self):
                return Dummy()

        request = self.factory.get('/')

        # Run & check
        with self.assertRaises(ImproperlyConfigured):
            MyView.as_view()(request, pk=self.journal.pk)

    def test_can_return_the_fedora_pid(self):
        # Setup
        class MyView(FedoraFileDatastreamView):
            fedora_object_class = JournalDigitalObject
            model = Journal

        view = MyView()
        view.kwargs = {'pk': self.journal.pk}

        # Run & check
        pid = view.get_fedora_object_pid()
        self.assertEqual(pid, self.journal.pid)

    def test_raises_http_404_if_the_datastream_cannot_be_retrieved(self):
        # Setup
        class MyView(FedoraFileDatastreamView):
            content_type = 'image/jpeg'
            datastream_name = 'logo'
            fedora_object_class = JournalDigitalObject
            model = Journal

        request = self.factory.get('/')

        # Run & check
        with self.assertRaises(Http404):
            MyView.as_view()(request, pk=self.journal.pk)

    def test_generates_a_response_with_the_appropriate_content_type(self):
        # Setup
        class MyView(FedoraFileDatastreamView):
            content_type = 'image/jpeg'
            datastream_name = 'logo'
            fedora_object_class = JournalDigitalObject
            model = Journal

            def get_datastream_content(self, fedora_object):
                return 'dummy'

        request = self.factory.get('/')

        # Run & check
        response = MyView.as_view()(request, pk=self.journal.pk)
        self.assertEqual(response['Content-Type'], 'image/jpeg')

    @unittest.mock.patch.object(FedoraFileDatastreamView, 'get_cache')
    def test_can_set_the_content_of_the_file_in_the_cache_if_it_is_not_there_already(
            self, mock_get_cache):
        # Setup
        class MyView(FedoraFileDatastreamView):
            content_type = 'image/jpeg'
            datastream_name = 'logo'
            fedora_object_class = JournalDigitalObject
            model = Journal

            def get_datastream_content(self, fedora_object):
                return 'dummy'

        mock_cache = unittest.mock.MagicMock()
        mock_cache_get = unittest.mock.MagicMock()
        mock_cache_get.return_value = None
        mock_cache_set = unittest.mock.MagicMock()
        mock_cache.get = mock_cache_get
        mock_cache.set = mock_cache_set
        mock_get_cache.return_value = mock_cache

        request = self.factory.get('/')

        # Run & check
        MyView.as_view()(request, pk=self.journal.pk)
        self.assertEqual(mock_cache_get.call_count, 1)
        self.assertEqual(mock_cache_set.call_count, 1)

    @unittest.mock.patch.object(FedoraFileDatastreamView, 'get_cache')
    def test_can_use_the_content_of_the_file_in_the_cache_if_applicable(self, mock_get_cache):
        # Setup
        class MyView(FedoraFileDatastreamView):
            content_type = 'image/jpeg'
            datastream_name = 'logo'
            fedora_object_class = JournalDigitalObject
            model = Journal

            def get_datastream_content(self, fedora_object):
                return 'dummy'

        mock_cache = unittest.mock.MagicMock()
        mock_cache_get = unittest.mock.MagicMock()
        mock_cache_get.return_value = 'content'
        mock_cache_set = unittest.mock.MagicMock()
        mock_cache.get = mock_cache_get
        mock_cache.set = mock_cache_set
        mock_get_cache.return_value = mock_cache

        request = self.factory.get('/')

        # Run & check
        MyView.as_view()(request, pk=self.journal.pk)
        self.assertEqual(mock_cache_get.call_count, 1)
        self.assertEqual(mock_cache_set.call_count, 0)
