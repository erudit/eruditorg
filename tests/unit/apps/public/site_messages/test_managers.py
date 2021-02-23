import pytest

from django.test import override_settings

from apps.public.site_messages.models import SiteMessage
from apps.public.site_messages.tests.utils import generate_site_messages


@pytest.mark.django_db
class TestSiteMessageManager:
    @override_settings(
        FOO=True,
        BAR=False,
        BAZ="BAZ",
    )
    def test_site_message_manager(self):
        generate_site_messages()

        # Check that all active messages are returned.
        assert [site_message for site_message in SiteMessage.objects.active()] == [
            {"id": 1, "level": "DEBUG", "message": "message 1"},
            {"id": 3, "level": "INFO", "message": "message 3"},
            {"id": 5, "level": "WARNING", "message": "message 5"},
            {"id": 7, "level": "ERROR", "message": "message 7"},
            {"id": 10, "level": "CRITICAL", "message": "message 10"},
        ]

        # Check that only messages for the public site are returned.
        assert [site_message for site_message in SiteMessage.objects.public()] == [
            {"id": 1, "level": "DEBUG", "message": "message 1"},
            {"id": 10, "level": "CRITICAL", "message": "message 10"},
        ]

        # Check that only messages for the libraries dashboard are returned.
        assert [site_message for site_message in SiteMessage.objects.library()] == [
            {"id": 3, "level": "INFO", "message": "message 3"},
            {"id": 7, "level": "ERROR", "message": "message 7"},
            {"id": 10, "level": "CRITICAL", "message": "message 10"},
        ]

        # Check that only messages for the journals dashboard are returned.
        assert [site_message for site_message in SiteMessage.objects.journal()] == [
            {"id": 5, "level": "WARNING", "message": "message 5"},
            {"id": 7, "level": "ERROR", "message": "message 7"},
            {"id": 10, "level": "CRITICAL", "message": "message 10"},
        ]
