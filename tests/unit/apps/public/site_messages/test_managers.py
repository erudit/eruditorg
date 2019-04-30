import pytest

from django.test import override_settings

from apps.public.site_messages.models import SiteMessage
from apps.public.site_messages.tests.utils import generate_site_messages


@pytest.mark.django_db
class TestSiteMessageManager:

    @override_settings(
        FOO=True,
        BAR=False,
        BAZ='BAZ',
    )
    def test_site_message_manager(self):
        generate_site_messages()

        # Check that all active messages are returned.
        assert [site_message for site_message in SiteMessage.objects.active()] == [
            {'level': 'DEBUG', 'message': 'message 1'},
            {'level': 'INFO', 'message': 'message 3'},
            {'level': 'WARNING', 'message': 'message 5'},
            {'level': 'ERROR', 'message': 'message 7'},
            {'level': 'CRITICAL', 'message': 'message 10'},
        ]

        # Check that only messages for the public site are returned.
        assert [site_message for site_message in SiteMessage.objects.public()] == [
            {'level': 'DEBUG', 'message': 'message 1'},
            {'level': 'CRITICAL', 'message': 'message 10'},
        ]

        # Check that only messages for the libraries dashboard are returned.
        assert [site_message for site_message in SiteMessage.objects.library()] == [
            {'level': 'INFO', 'message': 'message 3'},
            {'level': 'ERROR', 'message': 'message 7'},
            {'level': 'CRITICAL', 'message': 'message 10'},
        ]

        # Check that only messages for the journals dashboard are returned.
        assert [site_message for site_message in SiteMessage.objects.journal()] == [
            {'level': 'WARNING', 'message': 'message 5'},
            {'level': 'ERROR', 'message': 'message 7'},
            {'level': 'CRITICAL', 'message': 'message 10'},
        ]
