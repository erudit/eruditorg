import datetime as dt

from django.utils import timezone as tz
from django.db import models

from .conf import settings as editor_settings


class IssueSubmissionManager(models.Manager):
    def eminent_archival(self):
        """ Return issue submissions that will be archived eminently. """
        eminent_archival_dt = tz.now() - dt.timedelta(days=editor_settings.ARCHIVAL_DAY_OFFSET - 5)
        return self.get_queryset().filter(
            status="V",
            archived=False,
            date_modified__lt=eminent_archival_dt,
        )

    def ready_for_archival(self):
        """ Return issue submissions that are ready for archival. """
        ready_for_archival_dt = tz.now() - dt.timedelta(days=editor_settings.ARCHIVAL_DAY_OFFSET)
        return self.get_queryset().filter(
            status="V",
            archived=False,
            date_modified__lt=ready_for_archival_dt,
        )

    def action_needed(self):
        """ Return issue submissions that are in need review/corrections for more than 2 weeks. """
        action_needed_dt = tz.now() - dt.timedelta(days=editor_settings.ACTION_NEEDED_DAY_OFFSET)
        return self.get_queryset().filter(
            status__in=["S", "C"],
            date_modified__lt=action_needed_dt,
        )
