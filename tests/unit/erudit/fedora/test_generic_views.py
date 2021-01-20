import unittest.mock

import pytest
from django.core.exceptions import ImproperlyConfigured
from django.http import Http404
from django.test import RequestFactory

from erudit.fedora.objects import JournalDigitalObject
from erudit.fedora.views.generic import FedoraFileDatastreamView
from erudit.models import Journal
from erudit.test.factories import JournalFactory

pytestmark = pytest.mark.django_db


class TestFedoraFileDatastreamView:
    def test_raises_if_the_fedora_object_class_is_not_defined(self):
        # Setup
        class MyView(FedoraFileDatastreamView):
            pass

        request = RequestFactory().get('/')

        # Run & check
        with pytest.raises(ImproperlyConfigured):
            MyView.as_view()(request)

    def test_raises_if_the_django_object_can_not_be_retrieved(self):
        # Setup
        class MyView(FedoraFileDatastreamView):
            fedora_object_class = JournalDigitalObject

        request = RequestFactory().get('/')

        # Run & check
        with pytest.raises(ImproperlyConfigured):
            MyView.as_view()(request)

    def test_raises_if_the_content_type_is_not_defined(self):
        class MyView(FedoraFileDatastreamView):
            fedora_object_class = JournalDigitalObject
            model = Journal

        journal = JournalFactory()
        request = RequestFactory().get('/')

        with pytest.raises(ImproperlyConfigured):
            MyView.as_view()(request, pk=journal.pk)

    def test_raises_if_the_datastream_name_is_not_defined(self):
        # Setup
        class MyView(FedoraFileDatastreamView):
            content_type = 'image/jpeg'
            fedora_object_class = JournalDigitalObject
            model = Journal

        request = RequestFactory().get('/')
        journal = JournalFactory()

        # Run & check
        with pytest.raises(ImproperlyConfigured):
            MyView.as_view()(request, pk=journal.pk)

    def test_raises_if_the_datastream_is_not_defined_on_the_digital_object(self):
        # Setup
        class MyView(FedoraFileDatastreamView):
            content_type = 'image/jpeg'
            datastream_name = 'dummy'
            fedora_object_class = JournalDigitalObject
            model = Journal

        request = RequestFactory().get('/')
        journal = JournalFactory()

        # Run & check
        with pytest.raises(AttributeError):
            MyView.as_view()(request, pk=journal.pk)

    def test_raises_if_the_datastream_does_not_have_content(self):
        # Setup
        class Dummy:
            logo = 'dummy'
            pid = 'pid'

        class MyView(FedoraFileDatastreamView):
            content_type = 'image/jpeg'
            datastream_name = 'logo'
            fedora_object_class = JournalDigitalObject
            model = Journal

            def get_fedora_object(self):
                return Dummy()

        request = RequestFactory().get('/')
        journal = JournalFactory()

        # Run & check
        with pytest.raises(AttributeError):
            MyView.as_view()(request, pk=journal.pk)

    def test_can_return_the_fedora_pid(self):
        class MyView(FedoraFileDatastreamView):
            fedora_object_class = JournalDigitalObject
            model = Journal

        journal = JournalFactory()
        view = MyView()
        view.kwargs = {'pk': journal.pk}

        pid = view.get_fedora_object_pid()
        assert pid == journal.pid

    @unittest.mock.patch.object(JournalDigitalObject, 'logo')
    def test_raises_http_404_if_the_datastream_cannot_be_retrieved(self, mock_logo):
        class MyView(FedoraFileDatastreamView):
            content_type = 'image/jpeg'
            datastream_name = 'logo'
            fedora_object_class = JournalDigitalObject
            model = Journal

        request = RequestFactory().get('/')
        journal = JournalFactory()
        mock_logo.exists = False

        with pytest.raises(Http404):
            MyView.as_view()(request, pk=journal.pk)

    def test_generates_a_response_with_the_appropriate_content_type(self):
        class MyView(FedoraFileDatastreamView):
            content_type = 'image/jpeg'
            datastream_name = 'logo'
            fedora_object_class = JournalDigitalObject
            model = Journal

            def get_datastream_content(self, fedora_object):
                return 'dummy'

        request = RequestFactory().get('/')
        journal = JournalFactory()

        response = MyView.as_view()(request, pk=journal.pk)
        assert response['Content-Type'] == 'image/jpeg'

    def test_raises_http_404_if_the_datastream_cannot_be_retrieved_on_the_erudit_object(self):
        # Setup
        class MyView(FedoraFileDatastreamView):
            content_type = 'image/jpeg'
            datastream_name = 'dstream'
            fedora_object_class = JournalDigitalObject
            model = Journal

        view = MyView()

        mock_fedora_obj = unittest.mock.MagicMock()
        mock_fedora_obj.pid = "mock"
        mock_fedora_obj.dstream = unittest.mock.MagicMock()
        mock_fedora_obj.dstream.content = None
        mock_fedora_obj.dstream.exists = False

        view.get_object = unittest.mock.MagicMock(return_value=mock_fedora_obj)

        # Run & check
        with pytest.raises(Http404):
            view.get_datastream_content(mock_fedora_obj)

    def test_get_fedora_object_handles_none_pid(self):
        # When the PID is None, we get a None fedora object.
        class MyView(FedoraFileDatastreamView):
            content_type = 'image/jpeg'
            datastream_name = 'dstream'
            fedora_object_class = JournalDigitalObject
            model = Journal

        view = MyView()
        view.get_fedora_object_pid = unittest.mock.MagicMock(return_value=None)

        assert view.get_fedora_object() is None
