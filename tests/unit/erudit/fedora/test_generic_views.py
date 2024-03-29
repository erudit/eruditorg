import unittest.mock

import pytest
from django.http import Http404
from django.test import RequestFactory

from erudit.fedora.views.generic import FedoraFileDatastreamView
from erudit.models import Journal
from erudit.test.factories import JournalFactory

pytestmark = pytest.mark.django_db


class TestFedoraFileDatastreamView:
    def test_raises_if_the_django_object_can_not_be_retrieved(self):
        # Setup
        class MyView(FedoraFileDatastreamView):
            @property
            def content_type(self) -> str:
                return "application/xml"

            @property
            def datastream_name(self) -> str:
                return "SUMMARY"

            def get_object_pid(self):
                return "erudit:erudit.foo123.bar456"

        request = RequestFactory().get("/")

        # Run & check
        with pytest.raises(Http404):
            MyView.as_view()(request)

    def test_raises_if_the_content_type_is_not_defined(self):
        class MyView(FedoraFileDatastreamView):
            model = Journal

            @property
            def datastream_name(self) -> str:
                return "PUBLICATIONS"

        journal = JournalFactory()
        request = RequestFactory().get("/")

        with pytest.raises(NotImplementedError):
            MyView.as_view()(request, pk=journal.pk)

    def test_raises_if_the_datastream_name_is_not_defined(self):
        # Setup
        class MyView(FedoraFileDatastreamView):
            model = Journal

            @property
            def content_type(self) -> str:
                return "image/jpeg"

        request = RequestFactory().get("/")
        journal = JournalFactory()

        # Run & check
        with pytest.raises(NotImplementedError):
            MyView.as_view()(request, pk=journal.pk)

    def test_can_return_the_object_pid(self):
        class MyView(FedoraFileDatastreamView):
            model = Journal

        journal = JournalFactory()
        view = MyView()
        view.kwargs = {"pk": journal.pk}

        pid = view.get_object_pid()
        assert pid == journal.pid

    def test_raises_http_404_if_the_datastream_cannot_be_retrieved(self):
        class MyView(FedoraFileDatastreamView):
            model = Journal

            @property
            def content_type(self) -> str:
                return "image/jpeg"

            @property
            def datastream_name(self) -> str:
                return "LOGO"

        request = RequestFactory().get("/")
        journal = JournalFactory()

        with pytest.raises(Http404):
            MyView.as_view()(request, pk=journal.pk)

    def test_generates_a_response_with_the_appropriate_content_type(self):
        class MyView(FedoraFileDatastreamView):
            model = Journal

            @property
            def content_type(self) -> str:
                return "image/jpeg"

            @property
            def datastream_name(self) -> str:
                return "LOGO"

            def get_datastream_content(self):
                return "dummy"

        request = RequestFactory().get("/")
        journal = JournalFactory()

        response = MyView.as_view()(request, pk=journal.pk)
        assert response["Content-Type"] == "image/jpeg"

    def test_raises_http_404_if_the_datastream_cannot_be_retrieved_on_the_erudit_object(
        self, monkeypatch
    ):
        # Setup
        class MyView(FedoraFileDatastreamView):
            model = Journal

            @property
            def content_type(self) -> str:
                return "image/jpeg"

            @property
            def datastream_name(self) -> str:
                return "DSTREAM"

        journal = JournalFactory()
        view = MyView()
        view.kwargs = {"pk": journal.pk}

        import erudit.fedora.views.generic

        monkeypatch.setattr(
            erudit.fedora.views.generic,
            "get_cached_datastream_content",
            unittest.mock.MagicMock(return_value=None),
        )

        # Run & check
        with pytest.raises(Http404):
            view.get_datastream_content()
