# -*- coding: utf-8 -*-

import datetime as dt

from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.utils import timezone

from .conf import settings as account_actions_settings


class BaseAccountActionTokenManager(models.Manager):
    def get_for_object(self, obj):
        """ Returns a queryset filtering on a specific content object. """
        qs = self.get_queryset()
        return qs.filter(
            content_type=ContentType.objects.get_for_model(obj), object_id=obj.id)


class PendingManager(BaseAccountActionTokenManager):
    def get_queryset(self):
        """ Returns all the pending actions. """
        dt_limit = timezone.now() - dt.timedelta(
            days=account_actions_settings.ACTION_TOKEN_VALIDITY_DURATION)

        qs = super(PendingManager, self).get_queryset()
        qs = qs.filter(
            active=True, user__isnull=True, consumption_date__isnull=True, created__gte=dt_limit)

        return qs


class ConsumedManager(BaseAccountActionTokenManager):
    def get_queryset(self):
        """ Returns all the consumed actions. """
        qs = super(ConsumedManager, self).get_queryset()
        qs = qs.filter(
            user__isnull=False, consumption_date__isnull=False)

        return qs
