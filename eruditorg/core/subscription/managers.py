# -*- coding: utf-8 -*-

import logging

import datetime as dt
from urllib.parse import urlparse

from django.db import models
from django.conf import settings

logger = logging.getLogger(__name__)


class JournalAccessSubscriptionQueryset(models.QuerySet):
    def get_for_ip_address(self, ip_address):
        """ Return all the subscriptions for the given ip address """
        from .models import InstitutionIPAddressRange
        database_engine = settings.DATABASES[self.db]['ENGINE']
        if 'mysql' in database_engine:
            ip_range = InstitutionIPAddressRange.objects.extra(
                where={
                    "inet_aton(ip_start) <= inet_aton('{}') AND inet_aton(ip_end) >= inet_aton('{}')".format(  # noqa
                        ip_address,
                        ip_address
                    )
                }
            )

            return self.filter(institutionipaddressrange=ip_range)

        if 'psycopg2' not in database_engine:
            logger.warn("Doing string comparison on IP addresses. The results may not be accurate.")

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
