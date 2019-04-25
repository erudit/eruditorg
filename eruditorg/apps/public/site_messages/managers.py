from django.conf import settings
from django.db.models import Manager, Q
from django.utils import timezone


class SiteMessageManager(Manager):

    def active(self):
        """
        Get the active site messages.

        A site message is active if:
        * it is marked as active
        * it's start date is in the pass and it's end date is in the future
        * it's start date is in the pass and it has no end date
        * it's end date is in the future and it has no start date
        * it specify a setting that is set to True in the site's settings
        """
        # Get all site messages with a setting.
        site_messages_with_setting = self.get_queryset().filter(
            Q(setting__isnull=False)
        ).values('setting')
        # Filter to get only those which have their setting set to True in the site's settings.
        true_settings = [
            site_message['setting'] for site_message in site_messages_with_setting
            if getattr(settings, site_message['setting'], False) is True
        ]
        now = timezone.now()
        # Return all active site messages.
        return self.get_queryset().filter(
            Q(active=True) |
            Q(start_date__lte=now, end_date__gte=now) |
            Q(start_date__lte=now, end_date__isnull=True) |
            Q(start_date__isnull=True, end_date__gte=now) |
            Q(setting__in=true_settings)
        ).values('message', 'level')

    def public(self):
        return self.active().filter(target_sites__label='Public')

    def journal(self):
        return self.active().filter(target_sites__label='Tableau de bord des revues')

    def library(self):
        return self.active().filter(target_sites__label='Tableau de bord des bibliothèques')
