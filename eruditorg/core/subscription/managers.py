# -*- coding: utf-8 -*-

import datetime as dt

from django.db import models


class JournalAccessSubscriptionValidManager(models.Manager):
    def get_queryset(self):
        """ Returns all the valid JournalAccessSubscription instances. """
        nowd = dt.datetime.now().date()
        return super(JournalAccessSubscriptionValidManager, self).get_queryset().filter(
            journalaccesssubscriptionperiod__start__lte=nowd,
            journalaccesssubscriptionperiod__end__gte=nowd)
