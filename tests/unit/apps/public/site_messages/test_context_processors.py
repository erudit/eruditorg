import pytest
import unittest

from django.test import override_settings

from apps.public.site_messages.context_processors import active_site_messages
from apps.public.site_messages.tests.utils import generate_site_messages


@pytest.mark.django_db
class TestSiteMessagesContextProcessors:

    @override_settings(
        FOO=True,
        BAR=False,
        BAZ='BAZ',
    )
    def test_active_site_messages(self):
        generate_site_messages()

        request = unittest.mock.MagicMock()
        context = active_site_messages(request)
        assert [site_message for site_message in context['site_messages']] == [
            {'id': 1, 'level': 'DEBUG', 'message': 'message 1'},
            {'id': 10, 'level': 'CRITICAL', 'message': 'message 10'},
        ]
