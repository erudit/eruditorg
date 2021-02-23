# -*- coding: utf-8 -*-

from django.contrib.sessions.middleware import SessionMiddleware
from django.test import RequestFactory
import pytest

from apps.public.search.saved_searches import SavedSearchList


@pytest.mark.django_db
class TestSavedSearchList:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.factory = RequestFactory()

    def test_can_add_can_add_new_querystrings(self):
        # Setup
        qs = "foo=bar?xyz=test"
        request = self.factory.get("/")
        middleware = SessionMiddleware()
        middleware.process_request(request)
        searches = SavedSearchList(request)
        # Run
        searches.add(qs, 100)
        # Check
        assert len(searches) == 1
        assert searches[0]["querystring"] == qs
        assert searches[0]["results_count"] == 100
        assert searches[0]["uuid"]
        assert searches[0]["timestamp"]

    def test_can_remove_an_existing_search_using_its_uuid(self):
        # Setup
        qs = "foo=bar?xyz=test"
        request = self.factory.get("/")
        middleware = SessionMiddleware()
        middleware.process_request(request)
        searches = SavedSearchList(request)
        searches.add(qs, 100)
        uuid = searches[0]["uuid"]
        # Run
        searches.remove(uuid)
        # Check
        assert not len(searches)

    def test_can_be_saved_in_the_user_session(self):
        # Setup
        qs = "foo=bar?xyz=test"
        request = self.factory.get("/")
        middleware = SessionMiddleware()
        middleware.process_request(request)
        searches = SavedSearchList(request)
        searches.add(qs, 100)
        # Run
        searches.save()
        # Check
        assert request.session["saved-searches"] == list(searches)
