# -*- coding: utf-8 -*-

import datetime as dt
from urllib.parse import urlparse

from django.db import models


class JournalAccessSubscriptionQueryset(models.QuerySet):
    def get_for_ip_address(self, ip_address):
        """ Return all the subscriptions for the given ip address """
        return self.filter(
            institutionipaddressrange__ip_start__lte=ip_address,
            institutionipaddressrange__ip_end__gte=ip_address)

    def get_for_referer(self, referer):
        """ Return all the subscriptions for the given referer """
        if not referer:
            return

        parsed_user_referer = urlparse(referer)

        if parsed_user_referer.netloc == '':
            return

        subscriptions = self.filter(
            referers__referer__contains=parsed_user_referer.netloc,
        )
        for subscription in subscriptions:
            for institution_referer in subscription.referers.filter(
                referer__contains=parsed_user_referer.netloc
            ):
                parsed_institution_referer = urlparse(institution_referer.referer)
                if parsed_institution_referer.path in parsed_user_referer.path:
                    return subscription


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

    def get_for_referer(self, referer):
        return self.get_queryset().get_for_referer(referer)
