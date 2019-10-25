import datetime as dt

from django.utils import timezone as tz
from django.db import models

from .conf import settings as editor_settings


class IssueSubmissionManager(models.Manager):

    def _get_day_range_for_datetime(self, datetime):
        now_dt = tz.now()

        deletion_limit_dt = now_dt - dt.timedelta(days=datetime)

        return [
            deletion_limit_dt.replace(hour=0, minute=0, second=0, microsecond=0),
            deletion_limit_dt.replace(hour=23, minute=59, second=59, microsecond=999999),
        ]

    def archived_expire_soon(self):
        """ Return the IssueSubmissions that are archived and will expire soon """

        return self.get_queryset().filter(
            status="V",
            date_modified__range=self._get_day_range_for_datetime(
                editor_settings.ARCHIVE_DAY_OFFSET - 5
            )
        )

    def archived_expired(self):
        """ Return the IssueSubmissions that are archived and expired """
        return self.get_queryset().filter(
            status="V",
            date_modified__range=self._get_day_range_for_datetime(
                editor_settings.ARCHIVE_DAY_OFFSET
            )
        )

    def action_needed(self):
        """ Return issue submissions that are in need review/corrections for more than 2 weeks. """
        action_needed_dt = tz.now() - dt.timedelta(days=editor_settings.ACTION_NEEDED_DAY_OFFSET)
        return self.get_queryset().filter(
            status__in=["S", "C"],
            date_modified__lt=action_needed_dt,
        )
