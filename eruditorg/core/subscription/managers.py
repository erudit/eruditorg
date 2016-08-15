# -*- coding: utf-8 -*-

import datetime as dt

from django.db import models


class JournalAccessSubscriptionQueryset(models.QuerySet):
    def get_for_ip_address(self, ip_address):
        """ Return all the subscriptions for the given ip address """
        return self.filter(
            institutionipaddressrange__ip_start__lte=ip_address,
            institutionipaddressrange__ip_end__gte=ip_address)


class JournalAccessSubscriptionValidManager(models.Manager):
    def get_queryset(self):
        """ Returns all the valid JournalAccessSubscription instances. """
        nowd = dt.datetime.now().date()
        return JournalAccessSubscriptionQueryset(self.model, using=self._db).filter(
            journalaccesssubscriptionperiod__start__lte=nowd,
            journalaccesssubscriptionperiod__end__gte=nowd)

    def get_for_ip_address(self, ip_address):
        """ Return all the subscriptions for the given ip address """
        return self.get_queryset().get_for_ip_address(ip_address)
