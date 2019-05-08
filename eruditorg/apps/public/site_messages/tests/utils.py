import datetime

from ..models import TargetSite
from django.utils import timezone
from .factories import SiteMessageFactory, TargetSiteFactory


def generate_site_messages():
    now = timezone.now()
    delta = datetime.timedelta(days=1)
    future_date = now + delta
    past_date = now - delta

    public = TargetSiteFactory(
        site=TargetSite.TARGET_SITE_PUBLIC,
    )
    library = TargetSiteFactory(
        site=TargetSite.TARGET_SITE_LIBRARY,
    )
    journal = TargetSiteFactory(
        site=TargetSite.TARGET_SITE_JOURNAL,
    )

    SiteMessageFactory(
        message='message 1',
        active=True,
        level='DEBUG',
        target_sites=[public],
    )
    SiteMessageFactory(
        message='message 2',
        active=False,
        target_sites=[public],
    )
    SiteMessageFactory(
        message='message 3',
        start_date=past_date,
        level='INFO',
        target_sites=[library],
    )
    SiteMessageFactory(
        message='message 4',
        start_date=future_date,
        target_sites=[library],
    )
    SiteMessageFactory(
        message='message 5',
        end_date=future_date,
        level='WARNING',
        target_sites=[journal],
    )
    SiteMessageFactory(
        message='message 6',
        end_date=past_date,
        target_sites=[journal],
    )
    SiteMessageFactory(
        message='message 7',
        start_date=past_date,
        end_date=future_date,
        level='ERROR',
        target_sites=[library, journal],
    )
    SiteMessageFactory(
        message='message 8',
        start_date=past_date,
        end_date=past_date,
        target_sites=[library, journal],
    )
    SiteMessageFactory(
        message='message 9',
        start_date=future_date,
        end_date=future_date,
        target_sites=[library, journal],
    )
    SiteMessageFactory(
        message='message 10',
        setting='FOO',
        level='CRITICAL',
        target_sites=[public, library, journal],
    )
    SiteMessageFactory(
        message='message 11',
        setting='BAR',
        target_sites=[public, library, journal],
    )
    SiteMessageFactory(
        message='message 12',
        setting='BAZ',
        target_sites=[public, library, journal],
    )
