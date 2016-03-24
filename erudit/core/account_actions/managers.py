# -*- coding: utf-8 -*-

import datetime as dt

from django.db import models
from django.utils import timezone

from .conf import settings as account_actions_settings


class PendingManager(models.Manager):
    def get_queryset(self):
        """
        Returns all the pending actions.
        """
        dt_limit = timezone.now() - dt.timedelta(
            days=account_actions_settings.ACTION_TOKEN_VALIDITY_DURATION)

        qs = super(PendingManager, self).get_queryset()
        qs = qs.filter(
            user__isnull=True, consumption_date__isnull=True, created__gte=dt_limit)

        return qs
