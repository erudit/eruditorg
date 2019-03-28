from django.conf import settings
from django.db.models import Q
from django.utils import timezone

from .models import SiteMessage


def active_site_messages(request):
    """
    Get the active site messages for every template's context.

    A site message is active if:
    * it is marked as active
    * it's start date is in the pass and it's end date is in the future
    * it's start date is in the pass and it has no end date
    * it's end date is in the future and it has no start date
    * it specify a setting that is set to True in the site's settings
    """
    # Get all site messages with a setting.
    site_messages_with_setting = SiteMessage.objects.filter(
        Q(setting__isnull=False)
    ).values('setting')
    # Filter to get only those which have their setting set to True in the site's settings.
    true_settings = [
        site_message['setting'] for site_message in site_messages_with_setting
        if getattr(settings, site_message['setting'], False) is True
    ]
    now = timezone.now()
    # Return all active site messages.
    return {
        'site_messages': SiteMessage.objects.filter(
            Q(active=True) |
            Q(start_date__lte=now, end_date__gte=now) |
            Q(start_date__lte=now, end_date__isnull=True) |
            Q(start_date__isnull=True, end_date__gte=now) |
            Q(setting__in=true_settings)
        ).values('message', 'level'),
    }
