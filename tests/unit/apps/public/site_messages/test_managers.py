import datetime
import pytest
import unittest

from django.test import override_settings

from apps.public.site_messages.models import SiteMessage
from apps.public.site_messages.tests.factories import SiteMessageFactory, TargetSiteFactory


@pytest.mark.django_db
class TestSiteMessageManager:

    @override_settings(
        FOO=True,
        BAR=False,
        BAZ='BAZ',
    )
    def test_site_message_manager(self):
        now = datetime.datetime.now()
        delta = datetime.timedelta(days=1)
        future_date = now + delta
        past_date = now - delta

        public = TargetSiteFactory(label='Public')
        library = TargetSiteFactory(label='Tableau de bord des bibliothèques')
        journal = TargetSiteFactory(label='Tableau de bord des revues')

        SiteMessageFactory(message='message 1', active=True, level='DEBUG', target_sites=[public])
        SiteMessageFactory(message='message 2', active=False, target_sites=[public])
        SiteMessageFactory(message='message 3', start_date=past_date, level='INFO', target_sites=[library])
        SiteMessageFactory(message='message 4', start_date=future_date, target_sites=[library])
        SiteMessageFactory(message='message 5', end_date=future_date, level='WARNING', target_sites=[journal])
        SiteMessageFactory(message='message 6', end_date=past_date, target_sites=[journal])
        SiteMessageFactory(message='message 7', start_date=past_date, end_date=future_date, level='ERROR', target_sites=[library, journal])
        SiteMessageFactory(message='message 8', start_date=past_date, end_date=past_date, target_sites=[library, journal])
        SiteMessageFactory(message='message 9', start_date=future_date, end_date=future_date, target_sites=[library, journal])
        SiteMessageFactory(message='message 10', setting='FOO', level='CRITICAL', target_sites=[public, library, journal])
        SiteMessageFactory(message='message 11', setting='BAR', target_sites=[public, library, journal])
        SiteMessageFactory(message='message 12', setting='BAZ', target_sites=[public, library, journal])

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
