import datetime
import pytest
import unittest

from django.test import override_settings

from apps.public.site_messages.models import SiteMessage
from apps.public.site_messages.context_processors import active_site_messages


@pytest.mark.django_db
class TestSiteMessagesContextProcessors:

    @override_settings(
        FOO=True,
        BAR=False,
        BAZ='BAZ',
    )
    def test_active_site_messages(self):
        now = datetime.datetime.now()
        delta = datetime.timedelta(days=1)
        future_date = now + delta
        past_date = now - delta
        SiteMessage.objects.bulk_create([
            SiteMessage(message='message 1', active=True, level='DEBUG'),
            SiteMessage(message='message 2', active=False),
            SiteMessage(message='message 3', start_date=past_date, level='INFO'),
            SiteMessage(message='message 4', start_date=future_date),
            SiteMessage(message='message 5', end_date=future_date, level='WARNING'),
            SiteMessage(message='message 6', end_date=past_date),
            SiteMessage(message='message 7', start_date=past_date, end_date=future_date, level='ERROR'),
            SiteMessage(message='message 8', start_date=past_date, end_date=past_date),
            SiteMessage(message='message 9', start_date=future_date, end_date=future_date),
            SiteMessage(message='message 10', setting='FOO', level='CRITICAL'),
            SiteMessage(message='message 11', setting='BAR'),
            SiteMessage(message='message 12', setting='BAZ'),
        ])
        request = unittest.mock.MagicMock()
        context = active_site_messages(request)
        assert [site_message for site_message in context['site_messages']] == [
            {'level': 'DEBUG', 'message': 'message 1'},
            {'level': 'INFO', 'message': 'message 3'},
            {'level': 'WARNING', 'message': 'message 5'},
            {'level': 'ERROR', 'message': 'message 7'},
            {'level': 'CRITICAL', 'message': 'message 10'},
        ]
